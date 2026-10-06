from datetime import datetime
from db import db

class Supplier(db.Model):
    __tablename__ = 'suppliers'

    id = db.Column(db.Integer, primary_key=True)
    supplier_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # SUP-0001
    supplier_name = db.Column(db.String(120), nullable=False, index=True)
    logo_url = db.Column(db.String(255), nullable=True)
    contact_person = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    gst_id = db.Column(db.String(30), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), default='India')
    supplier_category = db.Column(db.String(50), default='Fabrics')
    payment_terms = db.Column(db.String(50), default='Net 30')
    rating = db.Column(db.Float, default=4.5) # 1.0 to 5.0
    status = db.Column(db.String(20), default='Active')
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'supplier_id': self.supplier_id,
            'supplier_name': self.supplier_name,
            'logo_url': self.logo_url or f"https://ui-avatars.com/api/?name={self.supplier_name}&background=0f172a&color=ffffff",
            'contact_person': self.contact_person or '',
            'email': self.email or '',
            'phone': self.phone or '',
            'gst_id': self.gst_id or '',
            'address': self.address or '',
            'city': self.city or '',
            'state': self.state or '',
            'country': self.country or 'India',
            'supplier_category': self.supplier_category,
            'payment_terms': self.payment_terms,
            'rating': self.rating,
            'status': self.status,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
