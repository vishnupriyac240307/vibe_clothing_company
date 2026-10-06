from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from db import db
from models.supplier import Supplier
from models.material import Material
from services.logo_service import LogoService
from utils.decorators import login_required, role_required
from utils.id_generator import generate_next_id
from utils.helpers import log_activity

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/suppliers')
@login_required
def index():
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()

    query = Supplier.query

    if search:
        query = query.filter(
            (Supplier.supplier_name.ilike(f"%{search}%")) |
            (Supplier.supplier_id.ilike(f"%{search}%")) |
            (Supplier.contact_person.ilike(f"%{search}%")) |
            (Supplier.city.ilike(f"%{search}%"))
        )

    if category:
        query = query.filter(Supplier.supplier_category == category)

    suppliers = query.order_by(Supplier.supplier_name.asc()).all()

    supplier_list = []
    for s in suppliers:
        s_dict = s.to_dict()
        mat_count = Material.query.filter_by(supplier_id=s.supplier_id).count()
        s_dict['materials_supplied_count'] = mat_count
        supplier_list.append(s_dict)

    categories = db.session.query(Supplier.supplier_category).distinct().all()
    category_list = [c[0] for c in categories if c[0]]

    return render_template('suppliers/index.html', suppliers=supplier_list, categories=category_list, search=search, selected_category=category)

@suppliers_bp.route('/suppliers/add', methods=['POST'])
@login_required
@role_required(['admin', 'manager'])
def add_supplier():
    try:
        supplier_name = request.form.get('supplier_name', '').strip()
        contact_person = request.form.get('contact_person', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        gst_id = request.form.get('gst_id', '').strip()
        address = request.form.get('address', '').strip()
        city = request.form.get('city', '').strip()
        state = request.form.get('state', '').strip()
        country = request.form.get('country', 'India').strip()
        category = request.form.get('supplier_category', 'Fabrics').strip()
        payment_terms = request.form.get('payment_terms', 'Net 30').strip()
        rating = float(request.form.get('rating', 4.5))
        custom_logo_url = request.form.get('logo_url', '').strip()

        if not supplier_name:
            flash('Supplier name is required.', 'danger')
            return redirect(url_for('suppliers.index'))

        supplier_id = generate_next_id('supplier')
        logo_url = custom_logo_url or LogoService.get_company_logo(supplier_name)

        supplier = Supplier(
            supplier_id=supplier_id,
            supplier_name=supplier_name,
            logo_url=logo_url,
            contact_person=contact_person,
            email=email,
            phone=phone,
            gst_id=gst_id,
            address=address,
            city=city,
            state=state,
            country=country,
            supplier_category=category,
            payment_terms=payment_terms,
            rating=rating,
            status='Active'
        )

        db.session.add(supplier)
        db.session.commit()

        log_activity('Add Supplier', 'Suppliers', f"Created supplier {supplier_name} ({supplier_id}).", record_id=supplier_id)
        flash(f"Supplier {supplier_name} ({supplier_id}) created successfully!", 'success')

    except Exception as e:
        db.session.rollback()
        flash(f"Error adding supplier: {str(e)}", 'danger')

    return redirect(url_for('suppliers.index'))
