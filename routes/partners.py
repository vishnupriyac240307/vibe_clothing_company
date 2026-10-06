from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from models.partner import Customer, Supplier
from models.production import ProductionOrder
from models.shipment import Shipment
from models.inventory import Material
from services.image_service import get_company_logo_url
from utils.auth_helpers import login_required, role_required
from db import db

partners_bp = Blueprint('partners', __name__)

# --- CUSTOMERS ---

@partners_bp.route('/customers')
@partners_bp.route('/customers/')
@login_required
def list_customers():
    search = request.args.get('search', '').strip()
    query = Customer.query
    if search:
        query = query.filter(
            (Customer.company_name.ilike(f"%{search}%")) |
            (Customer.contact_person.ilike(f"%{search}%")) |
            (Customer.email.ilike(f"%{search}%")) |
            (Customer.phone.ilike(f"%{search}%"))
        )
    customers = query.order_by(Customer.company_name.asc()).all()
    
    customer_data = []
    for c in customers:
        orders = ProductionOrder.query.filter_by(customer_id=c.id).order_by(ProductionOrder.created_at.desc()).all()
        shipments = Shipment.query.filter_by(customer_id=c.id).order_by(Shipment.created_at.desc()).all()
        
        customer_data.append({
            'customer': c,
            'total_orders': len(orders),
            'active_orders': sum(1 for o in orders if o.status in ['PLANNED', 'IN PROGRESS']),
            'completed_orders': sum(1 for o in orders if o.status == 'COMPLETED'),
            'orders': orders,
            'shipments': shipments,
            'shipment_count': len(shipments)
        })

    return render_template('customers/list.html', customer_data=customer_data, search=search)


@partners_bp.route('/customers/add', methods=['POST'])
@login_required
@role_required('Admin', 'Supervisor', 'Manager')
def add_customer():
    name = request.form.get('company_name', '').strip()
    contact = request.form.get('contact_person', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    tax_id = request.form.get('tax_id', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    country = request.form.get('country', 'India')
    c_type = request.form.get('customer_type', 'Wholesale')
    website = request.form.get('website', '').strip()
    notes = request.form.get('notes', '')
    
    if not name:
        flash('Company Name is required.', 'danger')
        return redirect(url_for('partners.list_customers'))

    if Customer.query.filter_by(company_name=name).first():
        flash(f'Customer {name} already exists.', 'danger')
        return redirect(url_for('partners.list_customers'))

    logo_url = get_company_logo_url(name, website if website else None)

    customer = Customer(
        company_name=name,
        logo_url=logo_url,
        contact_person=contact,
        email=email,
        phone=phone,
        tax_id=tax_id,
        address=address,
        city=city,
        state=state,
        country=country,
        customer_type=c_type,
        website=website,
        notes=notes,
        is_active=True
    )
    db.session.add(customer)
    db.session.commit()
    
    flash(f"Customer {name} created successfully!", 'success')
    return redirect(url_for('partners.list_customers'))


@partners_bp.route('/customers/edit/<int:customer_id>', methods=['POST'])
@login_required
@role_required('Admin', 'Supervisor', 'Manager')
def edit_customer(customer_id):
    c = Customer.query.get_or_404(customer_id)
    c.company_name = request.form.get('company_name', c.company_name).strip()
    c.contact_person = request.form.get('contact_person', c.contact_person).strip()
    c.email = request.form.get('email', c.email).strip()
    c.phone = request.form.get('phone', c.phone).strip()
    c.tax_id = request.form.get('tax_id', c.tax_id).strip()
    c.address = request.form.get('address', c.address).strip()
    c.city = request.form.get('city', c.city).strip()
    c.state = request.form.get('state', c.state).strip()
    c.country = request.form.get('country', c.country).strip()
    c.customer_type = request.form.get('customer_type', c.customer_type)
    c.notes = request.form.get('notes', c.notes)
    
    db.session.commit()
    flash(f"Customer {c.company_name} updated successfully.", 'success')
    return redirect(url_for('partners.list_customers'))


@partners_bp.route('/customers/delete/<int:customer_id>', methods=['POST'])
@login_required
@role_required('Admin', 'Supervisor', 'Manager')
def delete_customer(customer_id):
    c = Customer.query.get_or_404(customer_id)
    name = c.company_name
    db.session.delete(c)
    db.session.commit()
    flash(f"Customer '{name}' deleted.", 'info')
    return redirect(url_for('partners.list_customers'))


# --- SUPPLIERS ---

@partners_bp.route('/suppliers')
@partners_bp.route('/suppliers/')
@login_required
def list_suppliers():
    search = request.args.get('search', '').strip()
    query = Supplier.query
    if search:
        query = query.filter(
            (Supplier.supplier_name.ilike(f"%{search}%")) |
            (Supplier.contact_person.ilike(f"%{search}%")) |
            (Supplier.category.ilike(f"%{search}%")) |
            (Supplier.materials_supplied.ilike(f"%{search}%"))
        )
    suppliers = query.order_by(Supplier.supplier_name.asc()).all()
    
    supplier_data = []
    for s in suppliers:
        supplied_materials = Material.query.filter_by(supplier_id=s.id).all()
        supplier_data.append({
            'supplier': s,
            'materials': supplied_materials,
            'material_count': len(supplied_materials)
        })

    return render_template('suppliers/list.html', supplier_data=supplier_data, search=search)


@partners_bp.route('/suppliers/add', methods=['POST'])
@login_required
@role_required('Admin', 'Supervisor', 'Manager')
def add_supplier():
    name = request.form.get('supplier_name', '').strip()
    contact = request.form.get('contact_person', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    tax_id = request.form.get('tax_id', '').strip()
    address = request.form.get('address', '').strip()
    city = request.form.get('city', '').strip()
    state = request.form.get('state', '').strip()
    country = request.form.get('country', 'India')
    category = request.form.get('category', 'Fabrics')
    materials_supplied = request.form.get('materials_supplied', '')
    payment_terms = request.form.get('payment_terms', 'Net 30')
    rating = float(request.form.get('rating', 4.5))
    notes = request.form.get('notes', '')
    
    if not name:
        flash('Supplier Name is required.', 'danger')
        return redirect(url_for('partners.list_suppliers'))

    if Supplier.query.filter_by(supplier_name=name).first():
        flash(f'Supplier {name} already exists.', 'danger')
        return redirect(url_for('partners.list_suppliers'))

    logo_url = get_company_logo_url(name)

    supplier = Supplier(
        supplier_name=name,
        logo_url=logo_url,
        contact_person=contact,
        email=email,
        phone=phone,
        tax_id=tax_id,
        address=address,
        city=city,
        state=state,
        country=country,
        category=category,
        materials_supplied=materials_supplied,
        payment_terms=payment_terms,
        rating=rating,
        status='Active',
        notes=notes
    )
    db.session.add(supplier)
    db.session.commit()
    
    flash(f"Supplier {name} added successfully!", 'success')
    return redirect(url_for('partners.list_suppliers'))


@partners_bp.route('/suppliers/edit/<int:supplier_id>', methods=['POST'])
@login_required
@role_required('Admin', 'Supervisor', 'Manager')
def edit_supplier(supplier_id):
    s = Supplier.query.get_or_404(supplier_id)
    s.supplier_name = request.form.get('supplier_name', s.supplier_name).strip()
    s.contact_person = request.form.get('contact_person', s.contact_person).strip()
    s.email = request.form.get('email', s.email).strip()
    s.phone = request.form.get('phone', s.phone).strip()
    s.tax_id = request.form.get('tax_id', s.tax_id).strip()
    s.address = request.form.get('address', s.address).strip()
    s.category = request.form.get('category', s.category)
    s.materials_supplied = request.form.get('materials_supplied', s.materials_supplied)
    s.notes = request.form.get('notes', s.notes)
    
    db.session.commit()
    flash(f"Supplier {s.supplier_name} updated successfully.", 'success')
    return redirect(url_for('partners.list_suppliers'))


@partners_bp.route('/suppliers/delete/<int:supplier_id>', methods=['POST'])
@login_required
@role_required('Admin', 'Supervisor', 'Manager')
def delete_supplier(supplier_id):
    s = Supplier.query.get_or_404(supplier_id)
    name = s.supplier_name
    db.session.delete(s)
    db.session.commit()
    flash(f"Supplier '{name}' deleted.", 'info')
    return redirect(url_for('partners.list_suppliers'))
