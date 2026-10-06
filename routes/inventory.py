from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from db import db
from models.material import Material
from models.supplier import Supplier
from models.transaction import InventoryTransaction
from services.erp_engine import ERPEngine
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity, format_inr

inventory_bp = Blueprint('inventory', __name__)

@inventory_bp.route('/inventory')
@login_required
def index():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    supplier_id = request.args.get('supplier_id', '').strip()

    query = Material.query

    if search:
        query = query.filter(
            (Material.name.ilike(f"%{search}%")) |
            (Material.material_id.ilike(f"%{search}%")) |
            (Material.code.ilike(f"%{search}%")) |
            (Material.color.ilike(f"%{search}%"))
        )
    if category:
        query = query.filter(Material.category == category)
    if supplier_id:
        query = query.filter(Material.supplier_id == supplier_id)

    materials = query.order_by(Material.updated_at.desc()).all()

    # Filter status if specified
    if status:
        materials = [m for m in materials if m.status == status.upper()]

    suppliers = Supplier.query.filter_by(status='Active').all()
    categories = db.session.query(Material.category).distinct().all()
    category_list = [c[0] for c in categories if c[0]]

    # Overview Metrics
    total_items = len(materials)
    total_val = sum(m.total_value for m in materials)
    low_stock = sum(1 for m in materials if m.status == 'LOW')
    critical_stock = sum(1 for m in materials if m.status == 'CRITICAL')

    return render_template(
        'inventory/index.html',
        materials=materials,
        suppliers=suppliers,
        categories=category_list,
        total_items=total_items,
        total_value=total_val,
        formatted_total_value=format_inr(total_val),
        low_stock=low_stock,
        critical_stock=critical_stock,
        search=search,
        selected_category=category,
        selected_status=status,
        selected_supplier=supplier_id
    )

@inventory_bp.route('/inventory/add', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def add_material():
    try:
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        category = request.form.get('category', 'Fabric').strip()
        description = request.form.get('description', '').strip()
        quantity = float(request.form.get('quantity', 0.0))
        unit = request.form.get('unit', 'Meter').strip()
        color = request.form.get('color', '').strip()
        specifications = request.form.get('specifications', '').strip()
        minimum_level = float(request.form.get('minimum_level', 100.0))
        reorder_level = float(request.form.get('reorder_level', 150.0))
        critical_level = float(request.form.get('critical_level', 50.0))
        unit_cost = float(request.form.get('unit_cost', 0.0))
        supplier_id = request.form.get('supplier_id', '').strip() or None
        storage_location = request.form.get('storage_location', '').strip()
        batch_number = request.form.get('batch_number', '').strip()

        if not name:
            flash('Material name is required.', 'danger')
            return redirect(url_for('inventory.index'))

        material_id = generate_next_id('material')

        material = Material(
            material_id=material_id,
            name=name,
            code=code or material_id,
            category=category,
            description=description,
            quantity=quantity,
            unit=unit,
            color=color,
            specifications=specifications,
            minimum_level=minimum_level,
            reorder_level=reorder_level,
            critical_level=critical_level,
            unit_cost=unit_cost,
            supplier_id=supplier_id,
            storage_location=storage_location,
            batch_number=batch_number
        )

        db.session.add(material)
        db.session.commit()

        # Log initial inventory transaction if quantity > 0
        if quantity > 0:
            ERPEngine.record_inventory_transaction(
                material_id=material_id,
                trans_type='Stock In',
                quantity=quantity,
                reference='Initial Addition',
                remarks=f"Initial stock added for new material {name}",
                user_id=session.get('username', 'System')
            )

        log_activity('Add Material', 'Inventory', f"Added material {name} ({material_id}) with initial quantity {quantity} {unit}.", record_id=material_id)
        flash(f"Material {name} ({material_id}) added successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding material: {str(e)}", 'danger')

    return redirect(url_for('inventory.index'))

@inventory_bp.route('/inventory/edit/<material_id>', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def edit_material(material_id):
    material = Material.query.filter_by(material_id=material_id).first_or_404()
    try:
        material.name = request.form.get('name', material.name).strip()
        material.code = request.form.get('code', material.code).strip()
        material.category = request.form.get('category', material.category).strip()
        material.description = request.form.get('description', material.description).strip()
        material.unit = request.form.get('unit', material.unit).strip()
        material.color = request.form.get('color', material.color).strip()
        material.specifications = request.form.get('specifications', material.specifications).strip()
        material.minimum_level = float(request.form.get('minimum_level', material.minimum_level))
        material.reorder_level = float(request.form.get('reorder_level', material.reorder_level))
        material.critical_level = float(request.form.get('critical_level', material.critical_level))
        material.unit_cost = float(request.form.get('unit_cost', material.unit_cost))
        material.supplier_id = request.form.get('supplier_id', '').strip() or None
        material.storage_location = request.form.get('storage_location', material.storage_location).strip()

        db.session.commit()
        log_activity('Edit Material', 'Inventory', f"Updated material parameters for {material.name} ({material_id}).", record_id=material_id)
        flash(f"Material {material.name} updated successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error updating material: {str(e)}", 'danger')

    return redirect(url_for('inventory.index'))

@inventory_bp.route('/inventory/delete/<material_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def delete_material(material_id):
    material = Material.query.filter_by(material_id=material_id).first_or_404()
    mat_name = material.name
    try:
        db.session.delete(material)
        db.session.commit()
        log_activity('Delete Material', 'Inventory', f"Deleted material {mat_name} ({material_id}).", record_id=material_id)
        flash(f"Material {mat_name} deleted successfully.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Cannot delete material: {str(e)}", 'danger')
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/inventory/transaction', methods=['POST'])
@login_required
def record_transaction():
    material_id = request.form.get('material_id', '').strip()
    trans_type = request.form.get('transaction_type', 'Stock In').strip()
    quantity = request.form.get('quantity', 0.0)
    reference = request.form.get('reference', '').strip()
    remarks = request.form.get('remarks', '').strip()

    if not material_id or not quantity:
        flash('Material ID and Quantity are required.', 'danger')
        return redirect(url_for('inventory.index'))

    success, msg = ERPEngine.record_inventory_transaction(
        material_id=material_id,
        trans_type=trans_type,
        quantity=float(quantity),
        reference=reference,
        remarks=remarks,
        user_id=session.get('username', 'System')
    )

    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')

    return redirect(url_for('inventory.index'))

@inventory_bp.route('/inventory/transactions')
@login_required
def transactions():
    txns = InventoryTransaction.query.order_by(InventoryTransaction.created_at.desc()).all()
    return render_template('inventory/transactions.html', transactions=txns)
