from flask import Blueprint, request, jsonify
from models.inventory import Material
from models.product import Product
from models.production import ProductionOrder, Batch
from models.partner import Customer, Supplier
from models.shipment import Shipment
from models.notification import Notification
from utils.auth_helpers import login_required
from db import db

api_bp = Blueprint('api_search', __name__)

@api_bp.route('/api/search')
@login_required
def global_search():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify({'results': []})
        
    results = []
    
    # 1. Materials
    materials = Material.query.filter(
        (Material.name.ilike(f"%{q}%")) | (Material.material_code.ilike(f"%{q}%"))
    ).limit(5).all()
    for m in materials:
        results.append({
            'category': 'Material',
            'title': m.name,
            'subtitle': f"Code: {m.material_code} | Qty: {m.quantity} {m.unit}",
            'link': f"/inventory?search={m.material_code}",
            'icon': 'fa-boxes-stacked'
        })
        
    # 2. Products
    products = Product.query.filter(
        (Product.name.ilike(f"%{q}%")) | (Product.sku.ilike(f"%{q}%"))
    ).limit(5).all()
    for p in products:
        results.append({
            'category': 'Product',
            'title': p.name,
            'subtitle': f"SKU: {p.sku} | Price: ₹{p.selling_price:.2f}",
            'link': f"/products?search={p.sku}",
            'icon': 'fa-shirt'
        })

    # 3. Production Orders
    orders = ProductionOrder.query.filter(
        ProductionOrder.order_number.ilike(f"%{q}%")
    ).limit(5).all()
    for o in orders:
        results.append({
            'category': 'Production Order',
            'title': f"Order #{o.order_number}",
            'subtitle': f"Product: {o.product.name if o.product else ''} | Status: {o.status}",
            'link': f"/production?search={o.order_number}",
            'icon': 'fa-industry'
        })

    # 4. Batches
    batches = Batch.query.filter(
        Batch.batch_code.ilike(f"%{q}%")
    ).limit(5).all()
    for b in batches:
        results.append({
            'category': 'Batch',
            'title': f"Batch #{b.batch_code}",
            'subtitle': f"Stage: {b.current_stage} | Target: {b.target_quantity}",
            'link': f"/batches?search={b.batch_code}",
            'icon': 'fa-layer-group'
        })

    # 5. Customers
    customers = Customer.query.filter(
        (Customer.company_name.ilike(f"%{q}%")) | (Customer.contact_person.ilike(f"%{q}%"))
    ).limit(5).all()
    for c in customers:
        results.append({
            'category': 'Customer',
            'title': c.company_name,
            'subtitle': f"Contact: {c.contact_person or 'N/A'} | Email: {c.email or 'N/A'}",
            'link': f"/customers?search={c.company_name}",
            'icon': 'fa-users'
        })

    # 6. Suppliers
    suppliers = Supplier.query.filter(
        (Supplier.supplier_name.ilike(f"%{q}%")) | (Supplier.category.ilike(f"%{q}%"))
    ).limit(5).all()
    for s in suppliers:
        results.append({
            'category': 'Supplier',
            'title': s.supplier_name,
            'subtitle': f"Category: {s.category} | Rating: {s.rating}★",
            'link': f"/suppliers?search={s.supplier_name}",
            'icon': 'fa-truck-field'
        })

    # 7. Shipments
    shipments = Shipment.query.filter(
        (Shipment.shipment_number.ilike(f"%{q}%")) | (Shipment.tracking_number.ilike(f"%{q}%"))
    ).limit(5).all()
    for sh in shipments:
        results.append({
            'category': 'Shipment',
            'title': f"Shipment #{sh.shipment_number}",
            'subtitle': f"Tracking: {sh.tracking_number} | Status: {sh.status}",
            'link': f"/shipments?search={sh.shipment_number}",
            'icon': 'fa-truck-fast'
        })

    return jsonify({'results': results})
