from datetime import datetime
from db import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    logo_url = db.Column(db.Text, nullable=True)
    contact_person = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True, default='India')
    customer_type = db.Column(db.String(50), nullable=True, default='Wholesale') # Wholesale, Retailer, Brand
    website = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'logo_url': self.logo_url,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'tax_id': self.tax_id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'customer_type': self.customer_type,
            'website': self.website,
            'notes': self.notes,
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }


class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    supplier_name = db.Column(db.String(150), unique=True, nullable=False, index=True)
    logo_url = db.Column(db.Text, nullable=True)
    contact_person = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    address = db.Column(db.Text, nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), nullable=True, default='India')
    category = db.Column(db.String(50), nullable=True, default='Fabrics') # Fabrics, Trims, Accessories, Packaging
    materials_supplied = db.Column(db.Text, nullable=True)
    payment_terms = db.Column(db.String(100), nullable=True, default='Net 30')
    rating = db.Column(db.Float, default=4.5) # 1.0 to 5.0
    status = db.Column(db.String(20), default='Active') # Active, Inactive, Blocked
    notes = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_name': self.supplier_name,
            'logo_url': self.logo_url,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'tax_id': self.tax_id,
            'address': self.address,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'category': self.category,
            'materials_supplied': self.materials_supplied,
            'payment_terms': self.payment_terms,
            'rating': self.rating,
            'status': self.status,
            'notes': self.notes,
            'created_at': self.created_at.strftime('%Y-%m-%d')
        }
