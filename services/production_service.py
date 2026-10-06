from db import db
from models.product import Product, ProductBOM
from models.inventory import Material
from models.production import ProductionOrder, Batch, BatchStageHistory
from models.notification import Notification
from datetime import datetime

def check_production_readiness(product_id, target_quantity):
    """
    Calculates material availability & production readiness percentage for a product order.
    Returns dict with readiness %, status ('READY', 'PARTIALLY READY', 'BLOCKED'), and detailed material breakdown.
    """
    bom_items = ProductBOM.query.filter_by(product_id=product_id).all()
    if not bom_items:
        return {
            'readiness_percent': 100.0,
            'status': 'READY',
            'has_bom': False,
            'materials': [],
            'missing_count': 0
        }

    materials_detail = []
    total_items = len(bom_items)
    ready_items_count = 0
    missing_count = 0

    for item in bom_items:
        mat = Material.query.get(item.material_id)
        if not mat:
            continue

        required_qty = round(item.required_quantity * target_quantity, 2)
        available_qty = mat.quantity
        is_sufficient = available_qty >= required_qty
        
        availability_ratio = min(1.0, available_qty / required_qty) if required_qty > 0 else 1.0
        
        if is_sufficient:
            ready_items_count += 1
        else:
            ready_items_count += availability_ratio
            missing_count += 1

        materials_detail.append({
            'material_id': mat.id,
            'material_code': mat.material_code,
            'material_name': mat.name,
            'unit': item.unit,
            'required_per_unit': item.required_quantity,
            'total_required': required_qty,
            'available_quantity': available_qty,
            'deficit': round(max(0.0, required_qty - available_qty), 2),
            'is_sufficient': is_sufficient
        })

    readiness_percent = round((ready_items_count / total_items) * 100.0, 1) if total_items > 0 else 100.0
    
    if readiness_percent >= 100.0 and missing_count == 0:
        status = 'READY'
    elif readiness_percent >= 50.0:
        status = 'PARTIALLY READY'
    else:
        status = 'BLOCKED'

    return {
        'readiness_percent': readiness_percent,
        'status': status,
        'has_bom': True,
        'materials': materials_detail,
        'missing_count': missing_count
    }


def start_production_order(order_id, user_id):
    """
    Executes production launch workflow:
    1. Validates order status
    2. Checks required raw materials against available inventory
    3. If ANY required material is insufficient -> BLOCKS launch and returns detailed error alert!
    4. If materials are sufficient -> Deducts required materials internally from inventory
    5. Creates associated Batch & initial BatchStageHistory ('Cutting')
    6. Updates order status to 'IN PROGRESS'
    7. Generates notifications for low-stock materials and new order start
    """
    try:
        order = ProductionOrder.query.get(order_id)
        if not order:
            return False, "Production Order not found"

        if (order.status or '').upper() not in ['PLANNED', 'PENDING']:
            return False, f"Cannot start order in '{order.status}' state"

        # Check raw materials availability
        bom_items = ProductBOM.query.filter_by(product_id=order.product_id).all()
        insufficient_materials = []

        for item in bom_items:
            mat = Material.query.get(item.material_id)
            if mat:
                qty_needed = round(item.required_quantity * order.quantity, 2)
                if mat.quantity < qty_needed:
                    insufficient_materials.append(
                        f"• {mat.name} (Required: {qty_needed} {mat.unit}, Available: {mat.quantity} {mat.unit})"
                    )

        if insufficient_materials:
            err_msg = "Insufficient inventory to start production.\n" + "\n".join(insufficient_materials)
            return False, err_msg

        # If sufficient, deduct raw materials internally
        for item in bom_items:
            mat = Material.query.get(item.material_id)
            if mat:
                qty_needed = round(item.required_quantity * order.quantity, 2)
                mat.quantity = round(max(0.0, mat.quantity - qty_needed), 2)
                
                # Check low stock threshold & notify
                if mat.quantity <= mat.min_level:
                    low_stock_notif = Notification(
                        title=f"Low Stock Warning: {mat.name}",
                        message=f"Stock for '{mat.name}' is now {mat.quantity} {mat.unit} (Minimum Stock Level: {mat.min_level} {mat.unit}).",
                        notification_type='low_stock',
                        link='/inventory'
                    )
                    db.session.add(low_stock_notif)

        # Update Production Order Status
        order.status = 'IN PROGRESS'
        order.start_date = datetime.utcnow().date()
        
        # Create Production Batch
        batch_code = f"BAT-{datetime.utcnow().strftime('%Y%m%d')}-{order.id:04d}"
        batch = Batch(
            batch_code=batch_code,
            production_order_id=order.id,
            product_id=order.product_id,
            customer_id=order.customer_id,
            target_quantity=order.quantity,
            produced_quantity=0,
            supervisor_id=order.supervisor_id or user_id,
            start_date=datetime.utcnow().date(),
            expected_completion=order.expected_completion_date,
            current_stage='Cutting',
            status='IN_PROGRESS'
        )
        db.session.add(batch)
        db.session.flush()

        # Add Stage History
        stage_hist = BatchStageHistory(
            batch_id=batch.id,
            stage='Cutting',
            status='STARTED',
            updated_by_user_id=user_id,
            notes='Production started. Material inventory deducted automatically.'
        )
        db.session.add(stage_hist)

        # Notification
        notif = Notification(
            title=f"Production Started: #{order.order_number}",
            message=f"Production for {order.quantity} units of {order.product.name if order.product else 'Product'} is now IN PROGRESS (Batch #{batch_code}).",
            notification_type='new_order',
            link='/production'
        )
        db.session.add(notif)

        db.session.commit()
        return True, f"Production Order #{order.order_number} started successfully! Raw materials deducted. Batch #{batch_code} launched."

    except Exception as e:
        db.session.rollback()
        return False, f"Failed to start production order: {str(e)}"


def complete_production_order(order_id, user_id):
    """
    Completes a production order:
    1. Updates finished product stock quantity
    2. Updates order status to 'COMPLETED'
    3. Updates batch status to 'COMPLETED'
    4. Generates completion notification
    """
    try:
        order = ProductionOrder.query.get(order_id)
        if not order:
            return False, "Production Order not found"

        if order.status == 'COMPLETED':
            return False, "Order is already completed"

        # Update Finished Product Inventory Stock
        product = Product.query.get(order.product_id)
        if product:
            product.stock_quantity += order.quantity

        order.status = 'COMPLETED'
        
        # Complete Batch if exists
        batch = Batch.query.filter_by(production_order_id=order.id).first()
        if batch:
            batch.status = 'COMPLETED'
            batch.produced_quantity = order.quantity
            batch.current_stage = 'Packing'
            
            stage_hist = BatchStageHistory(
                batch_id=batch.id,
                stage='Packing',
                status='COMPLETED',
                updated_by_user_id=user_id,
                notes='Final stage packing finished. Production order completed.'
            )
            db.session.add(stage_hist)

        # Notification
        notif = Notification(
            title=f"Order Completed: #{order.order_number}",
            message=f"Production order #{order.order_number} for {order.product.name if order.product else ''} marked COMPLETED. Finished goods stock updated.",
            notification_type='production_completed',
            link='/production'
        )
        db.session.add(notif)

        db.session.commit()
        return True, f"Production Order #{order.order_number} marked as COMPLETED! {order.quantity} units added to finished products."

    except Exception as e:
        db.session.rollback()
        return False, f"Error completing order: {str(e)}"
