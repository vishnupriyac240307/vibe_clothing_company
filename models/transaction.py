from datetime import datetime
from db import db

class InventoryTransaction(db.Model):
    __tablename__ = 'inventory_transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(30), unique=True, nullable=False, index=True) # INV-TXN-0001
    material_id = db.Column(db.String(20), db.ForeignKey('materials.material_id'), nullable=False, index=True)
    transaction_type = db.Column(db.String(50), nullable=False) # Stock In, Stock Out, Adjustment, Production Consumption, etc.
    quantity = db.Column(db.Float, nullable=False)
    previous_quantity = db.Column(db.Float, nullable=False)
    new_quantity = db.Column(db.Float, nullable=False)
    reference = db.Column(db.String(100), nullable=True) # e.g. ORD-0001 or PO-9982
    user_id = db.Column(db.String(80), nullable=False, default='System')
    remarks = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    material = db.relationship('Material', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'material_id': self.material_id,
            'material_name': self.material.name if self.material else 'Unknown Material',
            'material_unit': self.material.unit if self.material else '',
            'transaction_type': self.transaction_type,
            'quantity': self.quantity,
            'previous_quantity': self.previous_quantity,
            'new_quantity': self.new_quantity,
            'reference': self.reference or 'N/A',
            'user_id': self.user_id,
            'remarks': self.remarks or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
