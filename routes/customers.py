from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from db import db
from models.customer import Customer
from models.production import ProductionOrder
from models.shipment import Shipment
from services.logo_service import LogoService
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity, format_inr

customers_bp = Blueprint('customers', __name__)

@customers_bp.route('/customers')
@login_required
def index():
    search = request.args.get('search', '').strip()
    customer_type = request.args.get('type', '').strip()

    query = Customer.query

    if search:
        query = query.filter(
            (Customer.company_name.ilike(f"%{search}%")) |
            (Customer.customer_id.ilike(f"%{search}%")) |
            (Customer.contact_person.ilike(f"%{search}%")) |
            (Customer.city.ilike(f"%{search}%"))
        )
    if customer_type:
        query = query.filter(Customer.customer_type == customer_type)

    customers = query.order_by(Customer.company_name.asc()).all()

    # Calculate metrics for each customer
    customer_list = []
    for c in customers:
        c_dict = c.to_dict()
        orders = ProductionOrder.query.filter_by(customer_id=c.customer_id).all()
        shipments = Shipment.query.filter_by(customer_id=c.customer_id).all()

        total_orders = len(orders)
        active_orders = sum(1 for o in orders if o.status == 'IN_PROGRESS')
        completed_orders = sum(1 for o in orders if o.status == 'COMPLETED')
        
        # Calculate total spend based on product selling price * order quantity
        total_spend = 0.0
        for o in orders:
            if o.product and o.status == 'COMPLETED':
                total_spend += (o.product.selling_price * o.quantity)

        c_dict['total_orders'] = total_orders
        c_dict['active_orders'] = active_orders
        c_dict['completed_orders'] = completed_orders
        c_dict['shipment_count'] = len(shipments)
        c_dict['formatted_total_spend'] = format_inr(total_spend)
        customer_list.append(c_dict)

    return render_template('customers/index.html', customers=customer_list, search=search, selected_type=customer_type)

@customers_bp.route('/customers/add', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def add_customer():
    try:
        company_name = request.form.get('company_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        gst_id = request.form.get('gst_id', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        country = request.form.get('country', 'India').strip()
        customer_type = request.form.get('customer_type', 'Wholesale').strip()
        custom_logo_url = request.form.get('logo_url', '').strip()

        if not company_name:
            flash('Company name is required.', 'danger')
            return redirect(url_for('customers.index'))

        customer_id = generate_next_id('customer')
        logo_url = custom_logo_url or LogoService.get_company_logo(company_name)

        customer = Customer(
            customer_id=customer_id,
            company_name=company_name,
            logo_url=logo_url,
            contact_person=contact_person,
            email=email,
            phone=phone,
            gst_id=gst_id,
            address=address,
            city=city,
            state=state,
            country=country,
            customer_type=customer_type,
            status='Active'
        )

        db.session.add(customer)
        db.session.commit()

        log_activity('Add Customer', 'Customers', f"Created customer {company_name} ({customer_id}).", record_id=customer_id)
        flash(f"Customer {company_name} ({customer_id}) added successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding customer: {str(e)}", 'danger')

    return redirect(url_for('customers.index'))

@customers_bp.route('/customers/<customer_id>')
@login_required
def detail(customer_id):
    customer = Customer.query.filter_by(customer_id=customer_id).first_or_404()
    orders = ProductionOrder.query.filter_by(customer_id=customer_id).order_by(ProductionOrder.created_at.desc()).all()
    shipments = Shipment.query.filter_by(customer_id=customer_id).order_by(Shipment.created_at.desc()).all()

    total_spend = sum((o.product.selling_price * o.quantity) for o in orders if o.product and o.status == 'COMPLETED')

    return render_template(
        'customers/detail.html',
        customer=customer.to_dict(),
        orders=[o.to_dict() for o in orders],
        shipments=[s.to_dict() for s in shipments],
        formatted_total_spend=format_inr(total_spend)
    )
