from datetime import datetime, timezone
from db import db
from models.material import Material
from models.product import Product, ProductBOM
from models.production import ProductionOrder
from models.batch import Batch
from models.transaction import InventoryTransaction
from models.quality import QualityInspection
from utils.id_generator import generate_next_id
from utils.helpers import log_activity, create_notification

class ERPEngine:

    @staticmethod
    def check_material_availability(product_id, target_quantity):
        """
        Calculates BOM requirement vs current inventory stock for a target production quantity.
        Returns dict with:
        - availability_pct (0.0 to 100.0)
        - readiness_score (0.0 to 100.0)
        - readiness_status ('READY', 'PARTIALLY_READY', 'BLOCKED')
        - missing_materials (list of missing item dicts)
        - bom_analysis (list of detailed material availability dicts)
        """
        product = Product.query.filter_by(product_id=product_id).first()
        if not product or not product.bom_items:
            return {
                'availability_pct': 100.0,
                'readiness_score': 100.0,
                'readiness_status': 'READY',
                'missing_materials': [],
                'bom_analysis': []
            }

        total_required_items = len(product.bom_items)
        fully_available_count = 0
        total_availability_pct_sum = 0.0
        missing_materials = []
        bom_analysis = []

        for item in product.bom_items:
            material = Material.query.filter_by(material_id=item.material_id).first()
            if not material:
                continue

            required_qty = item.quantity_required * target_quantity
            available_qty = material.quantity
            item_avail_pct = min(100.0, (available_qty / required_qty * 100.0)) if required_qty > 0 else 100.0
            
            is_sufficient = available_qty >= required_qty
            if is_sufficient:
                fully_available_count += 1

            total_availability_pct_sum += item_avail_pct

            analysis = {
                'material_id': material.material_id,
                'material_name': material.name,
                'unit': material.unit,
                'required_qty': required_qty,
                'available_qty': available_qty,
                'shortage_qty': max(0.0, required_qty - available_qty),
                'is_sufficient': is_sufficient,
                'availability_pct': round(item_avail_pct, 1)
            }
            bom_analysis.append(analysis)

            if not is_sufficient:
                missing_materials.append({
                    'material_id': material.material_id,
                    'name': material.name,
                    'shortage': max(0.0, required_qty - available_qty),
                    'unit': material.unit
                })

        overall_pct = round(total_availability_pct_sum / total_required_items, 1) if total_required_items > 0 else 100.0
        readiness_score = round((fully_available_count / total_required_items) * 100.0, 1) if total_required_items > 0 else 100.0

        if readiness_score == 100.0:
            readiness_status = 'READY'
        elif readiness_score >= 50.0:
            readiness_status = 'PARTIALLY_READY'
        else:
            readiness_status = 'BLOCKED'

        return {
            'availability_pct': overall_pct,
            'readiness_score': readiness_score,
            'readiness_status': readiness_status,
            'missing_materials': missing_materials,
            'bom_analysis': bom_analysis
        }

    @staticmethod
    def start_production(order_id, user_id='System'):
        """
        Executes Start Production workflow:
        1. Validates material availability
        2. Consumes materials from inventory & records transactions
        3. Creates/updates production batch
        4. Updates production order status to IN_PROGRESS
        5. Records activity log & notification
        """
        order = ProductionOrder.query.filter_by(order_id=order_id).first()
        if not order:
            return False, "Production Order not found"

        if order.status == 'IN_PROGRESS':
            return False, "Production Order is already in progress"

        if order.status == 'COMPLETED':
            return False, "Production Order is already completed"

        analysis = ERPEngine.check_material_availability(order.product_id, order.quantity)
        if analysis['readiness_status'] == 'BLOCKED' or len(analysis['missing_materials']) > 0:
            missing_names = ", ".join([f"{m['name']} ({m['shortage']} {m['unit']} short)" for m in analysis['missing_materials']])
            create_notification(
                title=f"Production Blocked: {order.order_id}",
                message=f"Insufficient materials for {order.product.name if order.product else 'Product'}. Shortage: {missing_names}",
                ntype='danger',
                link='/production'
            )
            return False, f"Material Shortage! Cannot start production. Missing: {missing_names}"

        product = order.product
        if not product:
            return False, "Linked Product not found"

        # Consume Materials
        for item in product.bom_items:
            material = Material.query.filter_by(material_id=item.material_id).first()
            if material:
                qty_needed = item.quantity_required * order.quantity
                prev_qty = material.quantity
                new_qty = max(0.0, prev_qty - qty_needed)
                
                material.quantity = new_qty
                
                # Check low/critical status
                mat_status = material.status
                if mat_status in ['LOW', 'CRITICAL']:
                    create_notification(
                        title=f"{mat_status} Stock Alert: {material.name}",
                        message=f"{material.name} ({material.material_id}) is down to {new_qty} {material.unit} (Min: {material.minimum_level}).",
                        ntype='warning' if mat_status == 'LOW' else 'danger',
                        link='/inventory'
                    )

                # Record Inventory Transaction
                txn = InventoryTransaction(
                    transaction_id=generate_next_id('inventory_transaction'),
                    material_id=material.material_id,
                    transaction_type='Production Consumption',
                    quantity=qty_needed,
                    previous_quantity=prev_qty,
                    new_quantity=new_qty,
                    reference=order.order_id,
                    user_id=user_id,
                    remarks=f"Consumed for Production Order {order.order_id} ({order.quantity} x {product.name})"
                )
                db.session.add(txn)

        # Create or Update Batch
        existing_batch = Batch.query.filter_by(production_order_id=order.order_id).first()
        if not existing_batch:
            batch_id = generate_next_id('batch')
            batch = Batch(
                batch_id=batch_id,
                batch_code=f"BAT-{order.order_id}",
                production_order_id=order.order_id,
                product_id=order.product_id,
                target_quantity=order.quantity,
                produced_quantity=0,
                supervisor=order.assigned_supervisor,
                customer_id=order.customer_id,
                start_date=datetime.now(timezone.utc).date(),
                expected_completion=order.expected_completion,
                current_stage='Cutting',
                status='In Progress'
            )
            db.session.add(batch)
        else:
            existing_batch.status = 'In Progress'
            existing_batch.current_stage = 'Cutting'

        # Update Order Status
        order.status = 'IN_PROGRESS'
        order.material_availability_pct = 100.0
        order.readiness_score = 100.0
        order.readiness_status = 'READY'
        product.status = 'In Production'

        db.session.commit()

        log_activity(
            action='Start Production',
            module='Production',
            record_id=order.order_id,
            description=f"Started production for {order.quantity} units of {product.name} ({product.product_id}). Consumed raw materials.",
            user_id=user_id
        )

        create_notification(
            title=f"Production Started: {order.order_id}",
            message=f"Production order {order.order_id} for {product.name} is now IN PROGRESS.",
            ntype='success',
            link='/production'
        )

        return True, "Production started successfully! Materials consumed and batch created."

    @staticmethod
    def complete_production(order_id, user_id='System'):
        """
        Executes Complete Production workflow:
        1. Checks QC inspection passed units for usable batch quantity
        2. Updates finished goods product stock
        3. Marks batch as Completed
        4. Marks production order as COMPLETED
        5. Logs activity & notification
        """
        order = ProductionOrder.query.filter_by(order_id=order_id).first()
        if not order:
            return False, "Production Order not found"

        if order.status == 'COMPLETED':
            return False, "Production Order is already completed"

        product = order.product
        if not product:
            return False, "Linked Product not found"

        batch = Batch.query.filter_by(production_order_id=order.order_id).first()
        
        # Check if a QC inspection was recorded for this batch
        latest_qc = QualityInspection.query.filter_by(batch_id=batch.batch_id).order_by(QualityInspection.inspection_date.desc()).first() if batch else None

        if latest_qc:
            produced_qty = latest_qc.passed_units
        elif batch and batch.produced_quantity > 0:
            produced_qty = batch.produced_quantity
        else:
            produced_qty = order.quantity

        # Add to finished goods available stock
        product.available_stock += produced_qty
        product.status = 'Active'

        # Update Batch
        if batch:
            batch.status = 'Completed'
            batch.current_stage = 'Packing'
            batch.produced_quantity = produced_qty

        # Update Order
        order.status = 'COMPLETED'

        db.session.commit()

        log_activity(
            action='Complete Production',
            module='Production',
            record_id=order.order_id,
            description=f"Completed production order {order.order_id}. Added {produced_qty} units to Finished Goods stock for {product.name} ({product.product_id}).",
            user_id=user_id
        )

        create_notification(
            title=f"Production Completed: {order.order_id}",
            message=f"Order {order.order_id} completed! {produced_qty} units added to stock for {product.name}.",
            ntype='success',
            link='/products'
        )

        return True, f"Production Order {order.order_id} marked as COMPLETED! Finished goods stock updated by {produced_qty} units."

    @staticmethod
    def record_inventory_transaction(material_id, trans_type, quantity, reference=None, remarks=None, user_id='System'):
        """
        Executes a manual or automated inventory transaction:
        Stock In / Purchase Receipt / Production Return -> Increases stock
        Stock Out / Damaged / Wastage -> Decreases stock
        Adjustment -> Sets exact stock or delta
        """
        material = Material.query.filter_by(material_id=material_id).first()
        if not material:
            return False, "Material not found"

        prev_qty = material.quantity
        qty = float(quantity)

        increase_types = ['Stock In', 'Purchase Receipt', 'Production Return']
        decrease_types = ['Stock Out', 'Damaged', 'Wastage', 'Production Consumption']

        if trans_type in increase_types:
            new_qty = prev_qty + abs(qty)
        elif trans_type in decrease_types:
            new_qty = max(0.0, prev_qty - abs(qty))
        elif trans_type == 'Adjustment':
            new_qty = abs(qty)
        else:
            new_qty = prev_qty + qty

        material.quantity = new_qty
        mat_status = material.status

        # Create Transaction Record
        txn = InventoryTransaction(
            transaction_id=generate_next_id('inventory_transaction'),
            material_id=material.material_id,
            transaction_type=trans_type,
            quantity=qty,
            previous_quantity=prev_qty,
            new_quantity=new_qty,
            reference=reference or 'Manual Entry',
            user_id=user_id,
            remarks=remarks or f"Inventory transaction {trans_type}"
        )
        db.session.add(txn)
        db.session.commit()

        if mat_status in ['LOW', 'CRITICAL']:
            create_notification(
                title=f"{mat_status} Stock Alert: {material.name}",
                message=f"Stock level for {material.name} updated to {new_qty} {material.unit}.",
                ntype='warning' if mat_status == 'LOW' else 'danger',
                link='/inventory'
            )

        log_activity(
            action=f"Inventory {trans_type}",
            module='Inventory',
            record_id=material.material_id,
            description=f"Recorded {trans_type} of {qty} {material.unit} for {material.name}. Quantity changed from {prev_qty} to {new_qty}.",
            user_id=user_id
        )

        return True, f"Inventory updated successfully. New quantity: {new_qty} {material.unit}"
