from datetime import datetime, timezone
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from db import db
from models.shipment import Shipment
from models.customer import Customer
from models.product import Product
from models.batch import Batch
from models.production import ProductionOrder
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity, create_notification

shipments_bp = Blueprint('shipments', __name__)

@shipments_bp.route('/shipments')
@login_required
def index():
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()

    query = Shipment.query

    if search:
        query = query.filter(
            (Shipment.shipment_id.ilike(f"%{search}%")) |
            (Shipment.tracking_number.ilike(f"%{search}%")) |
            (Shipment.product_id.ilike(f"%{search}%")) |
            (Shipment.customer_id.ilike(f"%{search}%")) |
            (Shipment.carrier.ilike(f"%{search}%"))
        )

    if status_filter:
        query = query.filter(Shipment.status == status_filter.upper())

    shipments = query.order_by(Shipment.created_at.desc()).all()

    customers = Customer.query.filter_by(status='Active').all()
    products = Product.query.filter_by(status='Active').all()
    batches = Batch.query.filter_by(status='Completed').all()
    orders = ProductionOrder.query.filter_by(status='COMPLETED').all()

    return render_template(
        'shipments/index.html',
        shipments=[s.to_dict() for s in shipments],
        customers=customers,
        products=products,
        batches=batches,
        orders=orders,
        search=search,
        selected_status=status_filter
    )

@shipments_bp.route('/shipments/add', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def add_shipment():
    try:
        customer_id = request.form.get('customer_id', '').strip()
        product_id = request.form.get('product_id', '').strip()
        batch_id = request.form.get('batch_id', '').strip() or None
        production_order_id = request.form.get('production_order_id', '').strip() or None
        quantity = int(request.form.get('quantity', 100))
        carrier = request.form.get('carrier', 'Blue Dart Logistics').strip()
        tracking_number = request.form.get('tracking_number', '').strip()
        expected_delivery_str = request.form.get('expected_delivery', '').strip()
        notes = request.form.get('notes', '').strip()

        if not customer_id or not product_id:
            flash('Customer and Product are required for Shipment.', 'danger')
            return redirect(url_for('shipments.index'))

        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            flash('Selected product not found.', 'danger')
            return redirect(url_for('shipments.index'))

        if product.available_stock < quantity:
            flash(f"Insufficient finished goods stock! Product {product.name} ({product_id}) has {product.available_stock} units available, requested {quantity} units.", 'danger')
            return redirect(url_for('shipments.index'))

        shipment_id = generate_next_id('shipment')
        shipment_date = datetime.now(timezone.utc).date()
        expected_delivery = datetime.strptime(expected_delivery_str, '%Y-%m-%d').date() if expected_delivery_str else None

        # Deduct Finished Goods Stock
        product.available_stock -= quantity

        shipment = Shipment(
            shipment_id=shipment_id,
            batch_id=batch_id,
            production_order_id=production_order_id,
            product_id=product_id,
            customer_id=customer_id,
            quantity=quantity,
            carrier=carrier,
            tracking_number=tracking_number or f"TRK-{shipment_id}",
            shipment_date=shipment_date,
            expected_delivery=expected_delivery,
            status='READY',
            notes=notes
        )

        db.session.add(shipment)
        db.session.commit()

        user_id = session.get('username', 'System')
        log_activity('Create Shipment', 'Shipments', f"Created shipment {shipment_id} for {quantity} units to customer {customer_id}. Deducted {quantity} units from Finished Goods stock.", record_id=shipment_id, user_id=user_id)
        flash(f"Shipment {shipment_id} created successfully! Deducted {quantity} units from finished goods stock.", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating shipment: {str(e)}", 'danger')

    return redirect(url_for('shipments.index'))

@shipments_bp.route('/shipments/update-status/<shipment_id>', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def update_status(shipment_id):
    shipment = Shipment.query.filter_by(shipment_id=shipment_id).first_or_404()
    new_status = request.form.get('status', 'READY').upper()

    try:
        old_status = shipment.status
        shipment.status = new_status

        if new_status == 'DELIVERED':
            shipment.actual_delivery = datetime.now(timezone.utc).date()
            create_notification(
                title=f"Delivery Completed: {shipment_id}",
                message=f"Shipment {shipment_id} delivered to customer {shipment.customer.company_name if shipment.customer else 'Customer'}.",
                ntype='success',
                link='/shipments'
            )

        db.session.commit()
        user_id = session.get('username', 'System')
        log_activity('Update Shipment Status', 'Shipments', f"Shipment {shipment_id} status changed from {old_status} to {new_status}.", record_id=shipment_id, user_id=user_id)
        flash(f"Shipment {shipment_id} updated to {new_status}.", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error updating shipment status: {str(e)}", 'danger')

    return redirect(url_for('shipments.index'))
