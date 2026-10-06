from datetime import datetime
from db import db

class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    material_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # MAT-0001
    name = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=True) # Material Code
    category = db.Column(db.String(50), nullable=False, default='Fabric')
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Float, nullable=False, default=0.0)
    unit = db.Column(db.String(20), nullable=False, default='Meter') # Meter, KG, PCS, Roll, Liter, Box
    color = db.Column(db.String(50), nullable=True)
    specifications = db.Column(db.String(255), nullable=True)
    minimum_level = db.Column(db.Float, nullable=False, default=100.0)
    reorder_level = db.Column(db.Float, nullable=False, default=150.0)
    critical_level = db.Column(db.Float, nullable=False, default=50.0)
    unit_cost = db.Column(db.Float, nullable=False, default=0.0) # In ₹
    supplier_id = db.Column(db.String(20), db.ForeignKey('suppliers.supplier_id'), nullable=True)
    storage_location = db.Column(db.String(100), nullable=True)
    batch_number = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    supplier = db.relationship('Supplier', backref='materials', lazy=True)

    @property
    def total_value(self):
        return round(float(self.quantity or 0) * float(self.unit_cost or 0), 2)

    @property
    def status(self):
        qty = float(self.quantity or 0)
        crit = float(self.critical_level or 0)
        min_lvl = float(self.minimum_level or 0)
        if qty <= crit:
            return 'CRITICAL'
        elif qty <= min_lvl:
            return 'LOW'
        return 'OK'

    def to_dict(self):
        return {
            'id': self.id,
            'material_id': self.material_id,
            'name': self.name,
            'code': self.code or '',
            'category': self.category,
            'description': self.description or '',
            'quantity': self.quantity,
            'unit': self.unit,
            'color': self.color or '',
            'specifications': self.specifications or '',
            'minimum_level': self.minimum_level,
            'reorder_level': self.reorder_level,
            'critical_level': self.critical_level,
            'unit_cost': self.unit_cost,
            'total_value': self.total_value,
            'supplier_id': self.supplier_id or '',
            'supplier_name': self.supplier.supplier_name if self.supplier else 'N/A',
            'storage_location': self.storage_location or '',
            'batch_number': self.batch_number or '',
            'status': self.status,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else ''
        }
