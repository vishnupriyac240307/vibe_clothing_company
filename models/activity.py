from datetime import datetime
from db import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(80), nullable=False, default='System')
    action = db.Column(db.String(100), nullable=False)
    module = db.Column(db.String(50), nullable=False) # Inventory, Products, Production, QC, Shipments, Auth, Users
    record_id = db.Column(db.String(50), nullable=True) # MAT-0001, PROD-0001, ORD-0001, etc.
    description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'module': self.module,
            'record_id': self.record_id or 'N/A',
            'description': self.description,
            'ip_address': self.ip_address or '127.0.0.1',
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S') if self.timestamp else ''
        }
