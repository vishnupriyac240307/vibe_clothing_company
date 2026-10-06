from datetime import datetime
from db import db

class Batch(db.Model):
    __tablename__ = 'batches'

    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # BAT-0001
    batch_code = db.Column(db.String(50), nullable=True)
    production_order_id = db.Column(db.String(20), db.ForeignKey('production_orders.order_id'), nullable=False, index=True)
    product_id = db.Column(db.String(20), db.ForeignKey('products.product_id'), nullable=False, index=True)
    target_quantity = db.Column(db.Integer, nullable=False, default=100)
    produced_quantity = db.Column(db.Integer, nullable=False, default=0)
    supervisor = db.Column(db.String(80), nullable=True)
    customer_id = db.Column(db.String(20), db.ForeignKey('customers.customer_id'), nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    expected_completion = db.Column(db.Date, nullable=True)
    current_stage = db.Column(db.String(30), nullable=False, default='Cutting') # Cutting, Dyeing, Stitching, Finishing, Packing
    status = db.Column(db.String(20), nullable=False, default='In Progress') # In Progress, On Hold, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    product = db.relationship('Product', lazy='joined')
    customer = db.relationship('Customer', lazy='joined')

    STAGES = ['Cutting', 'Dyeing', 'Stitching', 'Finishing', 'Packing', 'Completed']

    @property
    def stage_progress_pct(self):
        try:
            idx = self.STAGES.index(self.current_stage)
            return int(((idx + 1) / len(self.STAGES)) * 100)
        except ValueError:
            return 100 if self.status == 'Completed' or self.current_stage == 'Completed' else 0


    def to_dict(self):
        return {
            'id': self.id,
            'batch_id': self.batch_id,
            'batch_code': self.batch_code or self.batch_id,
            'production_order_id': self.production_order_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'target_quantity': self.target_quantity,
            'produced_quantity': self.produced_quantity,
            'supervisor': self.supervisor or 'N/A',
            'customer_id': self.customer_id or '',
            'customer_name': self.customer.company_name if self.customer else 'Internal',
            'start_date': self.start_date.strftime('%Y-%m-%d') if self.start_date else '',
            'expected_completion': self.expected_completion.strftime('%Y-%m-%d') if self.expected_completion else '',
            'current_stage': self.current_stage,
            'status': self.status,
            'progress_pct': self.stage_progress_pct,
            'stages': self.STAGES,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
