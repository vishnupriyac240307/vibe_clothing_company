from datetime import datetime
from db import db

class ProductionOrder(db.Model):
    __tablename__ = 'production_orders'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # ORD-0001
    product_id = db.Column(db.String(20), db.ForeignKey('products.product_id'), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False, default=100)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.customer_id'), nullable=True, index=True)
    priority = db.Column(db.String(20), nullable=False, default='Medium') # Low, Medium, High, Urgent
    start_date = db.Column(db.Date, nullable=True)
    expected_completion = db.Column(db.Date, nullable=True)
    assigned_supervisor = db.Column(db.String(80), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='PLANNED') # PLANNED, IN_PROGRESS, COMPLETED, CANCELLED
    material_availability_pct = db.Column(db.Float, default=100.0)
    readiness_score = db.Column(db.Float, default=100.0)
    readiness_status = db.Column(db.String(20), default='READY') # READY, PARTIALLY_READY, BLOCKED
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', lazy='joined')
    customer = db.relationship('Customer', lazy='joined')
    batches = db.relationship('Batch', backref='production_order', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'product_image': self.product.image_url if self.product else '/static/images/placeholder.svg',
            'quantity': self.quantity,
            'customer_id': self.customer_id or '',
            'customer_name': self.customer.company_name if self.customer else 'Internal Stock',
            'priority': self.priority,
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'expected_completion': self.expected_completion.strftime('%Y-%m-%d') if self.expected_completion else '',
            'assigned_supervisor': self.assigned_supervisor or 'Unassigned',
            'status': self.status,
            'material_availability_pct': round(self.material_availability_pct or 0, 1),
            'readiness_score': round(self.readiness_score or 0, 1),
            'readiness_status': self.readiness_status,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
