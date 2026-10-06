from datetime import datetime
from db import db

class MaterialCategory(db.Model):
    __tablename__ = 'material_categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

class Material(db.Model):
    __tablename__ = 'materials'

    id = db.Column(db.Integer, primary_key=True)
    material_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('material_categories.id', ondelete='SET NULL'), nullable=True)
    category = db.relationship('MaterialCategory', backref=db.backref('materials', lazy=True))
    
    description = db.Column(db.Text, nullable=True)
    quantity = db.Column(db.Float, default=0.0, nullable=False)
    unit = db.Column(db.String(20), nullable=False, default='Meter') # Meter, KG, PCS, Roll, Liter, Box
    color = db.Column(db.String(50), nullable=True)
    size_spec = db.Column(db.String(100), nullable=True)
    
    min_level = db.Column(db.Float, default=50.0, nullable=False)
    reorder_level = db.Column(db.Float, default=100.0, nullable=False)
    critical_level = db.Column(db.Float, default=20.0, nullable=False)
    unit_cost = db.Column(db.Float, default=0.0, nullable=False)
    
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id', ondelete='SET NULL'), nullable=True)
    supplier = db.relationship('Supplier', backref=db.backref('materials', lazy=True))
    
    storage_location = db.Column(db.String(100), nullable=True, default='Warehouse A')
    batch_number = db.Column(db.String(50), nullable=True)
    expiry_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def status(self):
        if self.quantity <= self.critical_level:
            return 'CRITICAL'
        elif self.quantity <= self.min_level:
            return 'LOW'
        return 'OK'

    @property
    def total_value(self):
        return round(self.quantity * self.unit_cost, 2)

    def to_dict(self):
        return {
            'id': self.id,
            'material_code': self.material_code,
            'name': self.name,
            'category': self.category.name if self.category else 'Uncategorized',
            'category_id': self.category_id,
            'description': self.description,
            'quantity': self.quantity,
            'unit': self.unit,
            'color': self.color,
            'size_spec': self.size_spec,
            'min_level': self.min_level,
            'reorder_level': self.reorder_level,
            'critical_level': self.critical_level,
            'unit_cost': self.unit_cost,
            'total_value': self.total_value,
            'status': self.status,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier.supplier_name if self.supplier else 'None',
            'storage_location': self.storage_location,
            'batch_number': self.batch_number,
            'expiry_date': self.expiry_date.strftime('%Y-%m-%d') if self.expiry_date else None,
            'notes': self.notes,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M')
        }

