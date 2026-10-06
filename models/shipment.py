from datetime import datetime
from db import db

class Shipment(db.Model):
    __tablename__ = 'shipments'

    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # SHP-0001
    batch_id = db.Column(db.String(20), db.ForeignKey('batches.batch_id'), nullable=True, index=True)
    production_order_id = db.Column(db.String(20), db.ForeignKey('production_orders.order_id'), nullable=True, index=True)
    product_id = db.Column(db.String(20), db.ForeignKey('products.product_id'), nullable=False, index=True)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.customer_id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=100)
    carrier = db.Column(db.String(80), nullable=False, default='Blue Dart Logistics')
    tracking_number = db.Column(db.String(50), nullable=True)
    shipment_date = db.Column(db.Date, nullable=True)
    expected_delivery = db.Column(db.Date, nullable=True)
    actual_delivery = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='READY') # READY, PACKED, SHIPPED, IN_TRANSIT, DELIVERED, DELAYED, CANCELLED
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', lazy='joined')
    customer = db.relationship('Customer', lazy='joined')
    batch = db.relationship('Batch', lazy='joined')
    production_order = db.relationship('ProductionOrder', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'shipment_id': self.shipment_id,
            'batch_id': self.batch_id or 'N/A',
            'production_order_id': self.production_order_id or 'N/A',
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'customer_id': self.customer_id,
            'customer_name': self.customer.company_name if self.customer else 'Unknown Customer',
            'quantity': self.quantity,
            'carrier': self.carrier,
            'tracking_number': self.tracking_number or 'Unassigned',
            'shipment_date': self.shipment_date.strftime('%Y-%m-%d') if self.shipment_date else '',
            'expected_delivery': self.expected_delivery.strftime('%Y-%m-%d') if self.expected_delivery else '',
            'actual_delivery': self.actual_delivery.strftime('%Y-%m-%d') if self.actual_delivery else '',
            'status': self.status,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
