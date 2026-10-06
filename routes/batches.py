from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from db import db
from models.batch import Batch
from services.erp_engine import ERPEngine
from utils.decorators import login_required, role_required
from utils.helpers import log_activity

batches_bp = Blueprint('batches', __name__)

from datetime import datetime, timedelta, timezone
from models.production import ProductionOrder
from models.product import Product
from models.customer import Customer
from utils.id_generator import generate_next_id

@batches_bp.route('/batches')
@login_required
def index():
    stage_filter = request.args.get('stage', '').strip()
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()

    query = Batch.query

    if search:
        query = query.filter(
            (Batch.batch_id.ilike(f"%{search}%")) |
            (Batch.production_order_id.ilike(f"%{search}%")) |
            (Batch.product_id.ilike(f"%{search}%")) |
            (Batch.supervisor.ilike(f"%{search}%"))
        )

    if stage_filter:
        query = query.filter(Batch.current_stage == stage_filter)
    if status_filter:
        query = query.filter(Batch.status == status_filter)

    batches = query.order_by(Batch.created_at.desc()).all()

    stages = Batch.STAGES

    production_orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).all()
    products = Product.query.order_by(Product.name.asc()).all()
    customers = Customer.query.order_by(Customer.company_name.asc()).all()

    return render_template(
        'batches/index.html',
        batches=batches,
        stages=stages,
        production_orders=production_orders,
        products=products,
        customers=customers,
        search=search,
        selected_stage=stage_filter,
        selected_status=status_filter
    )

@batches_bp.route('/batches/create', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def create_batch():
    try:
        production_order_id = request.form.get('production_order_id', '').strip()
        product_id = request.form.get('product_id', '').strip()
        batch_code = request.form.get('batch_code', '').strip()
        target_quantity = int(request.form.get('target_quantity', 100))
        supervisor = request.form.get('supervisor', '').strip()
        customer_id = request.form.get('customer_id', '').strip()
        current_stage = request.form.get('current_stage', 'Cutting').strip()
        start_date_str = request.form.get('start_date', '').strip()
        expected_completion_str = request.form.get('expected_completion', '').strip()

        # Auto-fill from production order if selected
        if production_order_id:
            order = ProductionOrder.query.filter_by(order_id=production_order_id).first()
            if order:
                if not product_id:
                    product_id = order.product_id
                if not customer_id and order.customer_id:
                    customer_id = order.customer_id
                if not supervisor and order.assigned_supervisor:
                    supervisor = order.assigned_supervisor
                if not target_quantity or target_quantity == 100:
                    target_quantity = order.quantity

        if not product_id:
            flash('Product selection is required to create a batch.', 'danger')
            return redirect(url_for('batches.index'))

        batch_id = generate_next_id('batch')
        if not batch_code:
            batch_code = f"BAT-{production_order_id}" if production_order_id else f"BAT-{batch_id}"

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.now(timezone.utc).date()
        expected_completion = datetime.strptime(expected_completion_str, '%Y-%m-%d').date() if expected_completion_str else (start_date + timedelta(days=7))

        batch = Batch(
            batch_id=batch_id,
            batch_code=batch_code,
            production_order_id=production_order_id or f"ORD-{batch_id}",
            product_id=product_id,
            target_quantity=target_quantity,
            produced_quantity=0,
            supervisor=supervisor or 'Floor Supervisor',
            customer_id=customer_id or None,
            start_date=start_date,
            expected_completion=expected_completion,
            current_stage=current_stage,
            status='In Progress'
        )

        db.session.add(batch)
        db.session.commit()

        user_id = session.get('username', 'System')
        log_activity('Create Batch', 'Batches', f"Created batch {batch_id} ({batch_code}) for product {product_id} with target {target_quantity} units.", record_id=batch_id, user_id=user_id)
        flash(f"Batch {batch_id} ({batch_code}) created successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating batch: {str(e)}", 'danger')

    return redirect(url_for('batches.index'))


@batches_bp.route('/batches/advance-stage/<batch_id>', methods=['POST'])
@login_required
def advance_stage(batch_id):
    batch = Batch.query.filter_by(batch_id=batch_id).first_or_404()
    stages = Batch.STAGES

    direction = request.form.get('direction', 'next') # 'next' or 'prev'
    try:
        current_idx = stages.index(batch.current_stage)
        if direction == 'next':
            if current_idx < len(stages) - 1:
                batch.current_stage = stages[current_idx + 1]
                if batch.current_stage == 'Packing':
                    batch.produced_quantity = batch.target_quantity
            else:
                batch.status = 'Completed'
                # Trigger complete_production to update ProductionOrder and finished goods stock
                user_id = session.get('username', 'System')
                ERPEngine.complete_production(batch.production_order_id, user_id=user_id)

        elif direction == 'prev':
            if current_idx > 0:
                batch.current_stage = stages[current_idx - 1]

        db.session.commit()
        log_activity('Update Batch Stage', 'Batches', f"Batch {batch_id} moved to stage '{batch.current_stage}' ({batch.status}).", record_id=batch_id)

        if request.is_json:
            return jsonify({'success': True, 'batch': batch.to_dict()})

        flash(f"Batch {batch_id} updated to stage: {batch.current_stage}", 'success')
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        flash(f"Error updating batch: {str(e)}", 'danger')

    return redirect(url_for('batches.index'))

@batches_bp.route('/batches/update-produced/<batch_id>', methods=['POST'])
@login_required
def update_produced_qty(batch_id):
    batch = Batch.query.filter_by(batch_id=batch_id).first_or_404()
    qty = request.form.get('produced_quantity', 0)
    try:
        batch.produced_quantity = int(qty)
        db.session.commit()
        log_activity('Update Batch Produced Quantity', 'Batches', f"Updated batch {batch_id} produced quantity to {qty}.", record_id=batch_id)
        flash(f"Produced quantity for {batch_id} updated to {qty}.", 'success')
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating produced quantity: {str(e)}", 'danger')

    return redirect(url_for('batches.index'))
