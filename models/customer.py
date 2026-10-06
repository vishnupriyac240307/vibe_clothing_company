from datetime import datetime
from db import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # CUS-0001
    company_name = db.Column(db.String(120), nullable=False, index=True)
    logo_url = db.Column(db.String(255), nullable=True)
    contact_person = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    gst_id = db.Column(db.String(30), nullable=True) # Tax / GST ID
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(50), nullable=True)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(50), default='India')
    customer_type = db.Column(db.String(30), default='Wholesale') # Wholesale, Retail, E-Commerce, Export
    status = db.Column(db.String(20), default='Active') # Active, Inactive
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'company_name': self.company_name,
            'logo_url': self.logo_url or f"https://ui-avatars.com/api/?name={self.company_name}&background=1e293b&color=ffffff",
            'contact_person': self.contact_person or '',
            'email': self.email or '',
            'phone': self.phone or '',
            'gst_id': self.gst_id or '',
            'address': self.address or '',
            'city': self.city or '',
            'state': self.state or '',
            'country': self.country or 'India',
            'customer_type': self.customer_type,
            'status': self.status,
            'notes': self.notes or '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else ''
        }
