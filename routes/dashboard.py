from flask import Blueprint, render_template, jsonify
from db import db
from models.material import Material
from models.product import Product
from models.production import ProductionOrder
from models.batch import Batch
from models.quality import QualityInspection
from models.shipment import Shipment
from models.transaction import InventoryTransaction
from utils.decorators import login_required
from utils.helpers import format_inr

dashboard_bp = Blueprint('dashboard', __name__)

def get_dashboard_stats():
    # 1. Total Materials
    total_materials = Material.query.count()

    # 2. Total Active Products
    total_products = Product.query.filter(Product.status != 'Inactive').count()

    # 3. Active Production Orders
    active_orders = ProductionOrder.query.filter_by(status='IN_PROGRESS').count()

    # 4. Completed Orders
    completed_orders = ProductionOrder.query.filter_by(status='COMPLETED').count()

    # 5. Active Batches
    active_batches = Batch.query.filter_by(status='In Progress').count()

    # 6. Low Stock Items (Quantity <= Minimum Level)
    materials = Material.query.all()
    low_stock_count = sum(1 for m in materials if m.status in ['LOW', 'CRITICAL'])

    # 7. Total Inventory Value (SUM quantity * unit_cost)
    total_inventory_value = sum(m.total_value for m in materials)

    # 8. Quality Pass Rate %
    qc_inspections = QualityInspection.query.all()
    total_eval = sum(q.total_evaluated for q in qc_inspections)
    total_passed = sum(q.passed_units for q in qc_inspections)
    quality_pass_rate = round((total_passed / total_eval * 100.0), 1) if total_eval > 0 else 100.0

    # 9. Shipments in Transit
    shipments_in_transit = Shipment.query.filter(Shipment.status.in_(['SHIPPED', 'IN_TRANSIT'])).count()

    # 10. Production Efficiency % (Completed / Total Planned)
    total_orders = ProductionOrder.query.count()
    completed_count = ProductionOrder.query.filter_by(status='COMPLETED').count()
    production_efficiency = round((completed_count / total_orders * 100.0), 1) if total_orders > 0 else 92.5

    # Widget Collections
    recent_orders = ProductionOrder.query.order_by(ProductionOrder.created_at.desc()).limit(5).all()
    low_stock_materials = [m for m in materials if m.status in ['LOW', 'CRITICAL']][:5]
    recent_transactions = InventoryTransaction.query.order_by(InventoryTransaction.created_at.desc()).limit(6).all()
    active_batch_list = Batch.query.filter_by(status='In Progress').order_by(Batch.updated_at.desc()).limit(5).all()
    recent_shipments = Shipment.query.order_by(Shipment.created_at.desc()).limit(5).all()

    return {
        'total_materials': total_materials,
        'total_products': total_products,
        'active_orders': active_orders,
        'completed_orders': completed_orders,
        'active_batches': active_batches,
        'low_stock_count': low_stock_count,
        'total_inventory_value': total_inventory_value,
        'formatted_inventory_value': format_inr(total_inventory_value),
        'quality_pass_rate': quality_pass_rate,
        'shipments_in_transit': shipments_in_transit,
        'production_efficiency': production_efficiency,
        'recent_orders': [o.to_dict() for o in recent_orders],
        'low_stock_materials': [m.to_dict() for m in low_stock_materials],
        'recent_transactions': [t.to_dict() for t in recent_transactions],
        'active_batch_list': [b.to_dict() for b in active_batch_list],
        'recent_shipments': [s.to_dict() for s in recent_shipments]
    }

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    stats = get_dashboard_stats()
    return render_template('dashboard/index.html', stats=stats)

@dashboard_bp.route('/api/dashboard/metrics')
@login_required
def dashboard_metrics_api():
    stats = get_dashboard_stats()
    return jsonify({'success': True, 'data': stats})
