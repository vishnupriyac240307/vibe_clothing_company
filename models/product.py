from datetime import datetime
from db import db

class ProductBOM(db.Model):
    __tablename__ = 'product_bom'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), db.ForeignKey('products.product_id', ondelete='CASCADE'), nullable=False, index=True)
    material_id = db.Column(db.String(20), db.ForeignKey('materials.material_id', ondelete='CASCADE'), nullable=False, index=True)
    quantity_required = db.Column(db.Float, nullable=False, default=1.0) # Quantity required per 1 finished product unit

    material = db.relationship('Material', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'material_id': self.material_id,
            'material_name': self.material.name if self.material else 'Unknown',
            'material_unit': self.material.unit if self.material else '',
            'material_stock': self.material.quantity if self.material else 0,
            'quantity_required': self.quantity_required
        }

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # PROD-0001 (NO SKU)
    name = db.Column(db.String(120), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default='T-Shirts')
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    size = db.Column(db.String(20), nullable=False, default='M') # S, M, L, XL, XXL, Free Size
    color = db.Column(db.String(50), nullable=True)
    selling_price = db.Column(db.Float, nullable=False, default=0.0) # In ₹
    cost_price = db.Column(db.Float, nullable=False, default=0.0) # In ₹
    target_quantity = db.Column(db.Integer, nullable=False, default=100)
    available_stock = db.Column(db.Integer, nullable=False, default=0) # Finished Goods Stock
    status = db.Column(db.String(20), nullable=False, default='Active') # Active, Inactive, In Production
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to BOM
    bom_items = db.relationship('ProductBOM', backref='product', cascade='all, delete-orphan', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'name': self.name,
            'category': self.category,
            'description': self.description or '',
            'image_url': self.image_url or '/static/images/placeholder.svg',
            'size': self.size,
            'color': self.color or '',
            'selling_price': self.selling_price,
            'cost_price': self.cost_price,
            'target_quantity': self.target_quantity,
            'available_stock': self.available_stock,
            'status': self.status,
            'bom': [item.to_dict() for item in self.bom_items],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
