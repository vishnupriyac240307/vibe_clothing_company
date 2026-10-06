from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from db import db
from models.production import ProductionOrder
from models.product import Product
from models.customer import Customer
from services.erp_engine import ERPEngine
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity

production_bp = Blueprint('production', __name__)

@production_bp.route('/production')
@login_required
def index():
    status_filter = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()

    query = ProductionOrder.query

    if search:
        query = query.filter(
            (ProductionOrder.order_id.ilike(f"%{search}%")) |
            (ProductionOrder.product_id.ilike(f"%{search}%")) |
            (ProductionOrder.assigned_supervisor.ilike(f"%{search}%"))
        )

    orders = query.order_by(ProductionOrder.created_at.desc()).all()

    # Recalculate material readiness for PLANNED orders
    planned_orders = []
    in_progress_orders = []
    completed_orders = []
    cancelled_orders = []

    for order in orders:
        if order.status == 'PLANNED':
            analysis = ERPEngine.check_material_availability(order.product_id, order.quantity)
            order.material_availability_pct = analysis['availability_pct']
            order.readiness_score = analysis['readiness_score']
            order.readiness_status = analysis['readiness_status']
            planned_orders.append(order)
        elif order.status == 'IN_PROGRESS':
            in_progress_orders.append(order)
        elif order.status == 'COMPLETED':
            completed_orders.append(order)
        else:
            cancelled_orders.append(order)

    products = Product.query.filter_by(status='Active').all()
    customers = Customer.query.filter_by(status='Active').all()

    return render_template(
        'production/index.html',
        planned_orders=planned_orders,
        in_progress_orders=in_progress_orders,
        completed_orders=completed_orders,
        cancelled_orders=cancelled_orders,
        all_orders=orders,
        products=products,
        customers=customers,
        search=search,
        selected_status=status_filter
    )

@production_bp.route('/production/add', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def add_order():
    try:
        product_id = request.form.get('product_id', '').strip()
        quantity = int(request.form.get('quantity', 100))
        customer_id = request.form.get('customer_id', '').strip() or None
        priority = request.form.get('priority', 'Medium').strip()
        start_date_str = request.form.get('start_date', '').strip()
        expected_completion_str = request.form.get('expected_completion', '').strip()
        supervisor = request.form.get('assigned_supervisor', '').strip()
        notes = request.form.get('notes', '').strip()

        if not product_id or quantity <= 0:
            flash('Valid Product ID and Quantity are required.', 'danger')
            return redirect(url_for('production.index'))

        product = Product.query.filter_by(product_id=product_id).first()
        if not product:
            flash('Selected Product does not exist.', 'danger')
            return redirect(url_for('production.index'))

        order_id = generate_next_id('production_order')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else datetime.utcnow().date()
        expected_completion = datetime.strptime(expected_completion_str, '%Y-%m-%d').date() if expected_completion_str else None

        # Check Readiness
        analysis = ERPEngine.check_material_availability(product_id, quantity)

        order = ProductionOrder(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            customer_id=customer_id,
            priority=priority,
            start_date=start_date,
            expected_completion=expected_completion,
            assigned_supervisor=supervisor or 'Production Lead',
            status='PLANNED',
            material_availability_pct=analysis['availability_pct'],
            readiness_score=analysis['readiness_score'],
            readiness_status=analysis['readiness_status'],
            notes=notes
        )

        db.session.add(order)
        db.session.commit()

        log_activity('Create Production Order', 'Production', f"Created Production Order {order_id} for {quantity} units of {product.name} ({product_id}). Readiness: {analysis['readiness_status']} ({analysis['readiness_score']}%).", record_id=order_id)
        flash(f"Production Order {order_id} created successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating production order: {str(e)}", 'danger')

    return redirect(url_for('production.index'))

@production_bp.route('/production/check-readiness/<order_id>')
@login_required
def check_readiness_api(order_id):
    order = ProductionOrder.query.filter_by(order_id=order_id).first_or_404()
    analysis = ERPEngine.check_material_availability(order.product_id, order.quantity)
    return jsonify({
        'success': True,
        'order_id': order.order_id,
        'product_id': order.product_id,
        'product_name': order.product.name if order.product else 'Unknown',
        'quantity': order.quantity,
        'analysis': analysis
    })

@production_bp.route('/production/start/<order_id>', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def start_production(order_id):
    user_id = session.get('username', 'System')
    success, msg = ERPEngine.start_production(order_id, user_id=user_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('production.index'))

@production_bp.route('/production/complete/<order_id>', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def complete_production(order_id):
    user_id = session.get('username', 'System')
    success, msg = ERPEngine.complete_production(order_id, user_id=user_id)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'danger')
    return redirect(url_for('production.index'))

@production_bp.route('/production/cancel/<order_id>', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def cancel_order(order_id):
    order = ProductionOrder.query.filter_by(order_id=order_id).first_or_404()
    order.status = 'CANCELLED'
    db.session.commit()
    log_activity('Cancel Production Order', 'Production', f"Cancelled Production Order {order_id}.", record_id=order_id)
    flash(f"Production Order {order_id} has been cancelled.", 'info')
    return redirect(url_for('production.index'))
