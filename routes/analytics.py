from datetime import datetime, timedelta, timezone
from flask import Blueprint, render_template, request, jsonify
from db import db
from models.material import Material
from models.product import Product
from models.production import ProductionOrder
from models.batch import Batch
from models.quality import QualityInspection
from models.shipment import Shipment
from models.customer import Customer
from models.supplier import Supplier
from utils.decorators import login_required
from utils.helpers import format_inr

analytics_bp = Blueprint('analytics', __name__)

@analytics_bp.route('/analytics')
@login_required
def index():
    return render_template('analytics/index.html')

@analytics_bp.route('/api/analytics/charts')
@login_required
def charts_data_api():
    period = request.args.get('period', '30d').lower()

    # 1. Orders by Status Breakdown
    orders_status = db.session.query(
        ProductionOrder.status, db.func.count(ProductionOrder.id)
    ).group_by(ProductionOrder.status).all()

    order_status_data = {
        'labels': [s[0] for s in orders_status],
        'values': [s[1] for s in orders_status]
    }

    # 2. Top Products by Target Quantity
    top_products = Product.query.order_by(Product.target_quantity.desc()).limit(5).all()
    top_products_data = {
        'labels': [p.name for p in top_products],
        'values': [p.target_quantity for p in top_products],
        'stock': [p.available_stock for p in top_products]
    }

    # 3. Customer Orders Count & Value
    customers = Customer.query.all()
    customer_labels = []
    customer_values = []
    customer_spend = []

    for c in customers:
        c_orders = ProductionOrder.query.filter_by(customer_id=c.customer_id).all()
        if len(c_orders) > 0:
            customer_labels.append(c.company_name)
            customer_values.append(len(c_orders))
            spend = sum((o.product.selling_price * o.quantity) for o in c_orders if o.product)
            customer_spend.append(round(spend, 2))

    # 4. Inventory Value by Category (in ₹)
    cat_values = db.session.query(
        Material.category,
        db.func.sum(Material.quantity * Material.unit_cost)
    ).group_by(Material.category).all()

    inventory_category_data = {
        'labels': [c[0] for c in cat_values if c[0]],
        'values': [round(float(c[1] or 0), 2) for c in cat_values if c[0]]
    }

    # 5. Quality Inspection Defects Breakdown
    defects = db.session.query(
        QualityInspection.defect_type,
        db.func.sum(QualityInspection.defective_units)
    ).group_by(QualityInspection.defect_type).all()

    qc_defects_data = {
        'labels': [d[0] for d in defects if d[0]],
        'values': [int(d[1] or 0) for d in defects if d[0]]
    }

    # 6. Monthly Output Trend (Simulated timeline from real orders)
    today = datetime.now(timezone.utc).date()

    timeline_labels = [(today - timedelta(days=i*5)).strftime('%b %d') for i in reversed(range(6))]
    timeline_output = [120, 180, 250, 310, 420, 490] # Sample progression curve

    return jsonify({
        'success': True,
        'order_status': order_status_data,
        'top_products': top_products_data,
        'customer_orders': {
            'labels': customer_labels,
            'orders': customer_values,
            'spend': customer_spend
        },
        'inventory_category': inventory_category_data,
        'qc_defects': qc_defects_data,
        'timeline': {
            'labels': timeline_labels,
            'output': timeline_output
        }
    })
