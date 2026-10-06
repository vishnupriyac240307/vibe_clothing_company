from flask import Blueprint, render_template, request, jsonify
from models.batch import Batch
from models.production import ProductionOrder
from models.product import Product
from models.quality import QualityInspection
from models.shipment import Shipment
from models.transaction import InventoryTransaction
from utils.decorators import login_required

traceability_bp = Blueprint('traceability', __name__)

@traceability_bp.route('/traceability')
@login_required
def index():
    batch_id = request.args.get('batch_id', '').strip()
    order_id = request.args.get('order_id', '').strip()

    batch = None
    order = None
    inspections = []
    shipments = []
    transactions = []

    if batch_id:
        batch = Batch.query.filter_by(batch_id=batch_id).first()
        if batch:
            order = ProductionOrder.query.filter_by(order_id=batch.production_order_id).first()
            inspections = QualityInspection.query.filter_by(batch_id=batch_id).all()
            shipments = Shipment.query.filter_by(batch_id=batch_id).all()
            transactions = InventoryTransaction.query.filter_by(reference=batch.production_order_id).all()

    elif order_id:
        order = ProductionOrder.query.filter_by(order_id=order_id).first()
        if order:
            batch = Batch.query.filter_by(production_order_id=order_id).first()
            if batch:
                inspections = QualityInspection.query.filter_by(batch_id=batch.batch_id).all()
                shipments = Shipment.query.filter_by(batch_id=batch.batch_id).all()
            transactions = InventoryTransaction.query.filter_by(reference=order_id).all()

    recent_batches = Batch.query.order_by(Batch.created_at.desc()).limit(15).all()

    return render_template(
        'traceability/index.html',
        batch=batch.to_dict() if batch else None,
        order=order.to_dict() if order else None,
        inspections=[q.to_dict() for q in inspections],
        shipments=[s.to_dict() for s in shipments],
        transactions=[t.to_dict() for t in transactions],
        recent_batches=recent_batches,
        searched_batch_id=batch_id,
        searched_order_id=order_id
    )
