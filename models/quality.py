from datetime import datetime
from db import db

class QualityInspection(db.Model):
    __tablename__ = 'quality_inspections'

    id = db.Column(db.Integer, primary_key=True)
    inspection_id = db.Column(db.String(20), unique=True, nullable=False, index=True) # QC-0001
    batch_id = db.Column(db.String(20), db.ForeignKey('batches.batch_id'), nullable=False, index=True)
    product_id = db.Column(db.String(20), db.ForeignKey('products.product_id'), nullable=False, index=True)
    inspector = db.Column(db.String(80), nullable=False, default='QA Inspector')
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_evaluated = db.Column(db.Integer, nullable=False, default=100)
    defective_units = db.Column(db.Integer, nullable=False, default=0)
    passed_units = db.Column(db.Integer, nullable=False, default=100)
    pass_rate = db.Column(db.Float, nullable=False, default=100.0) # Percentage
    defect_type = db.Column(db.String(100), nullable=True) # Stitching, Stain, Sizing, etc.
    remarks = db.Column(db.Text, nullable=True)
    qa_status = db.Column(db.String(10), nullable=False, default='PASS') # PASS, FAIL

    # Relationships
    batch = db.relationship('Batch', lazy='joined')
    product = db.relationship('Product', lazy='joined')

    def calculate_metrics(self, pass_threshold=90.0):
        self.passed_units = max(0, self.total_evaluated - self.defective_units)
        if self.total_evaluated > 0:
            self.pass_rate = round((self.passed_units / self.total_evaluated) * 100.0, 2)
        else:
            self.pass_rate = 100.0
        self.qa_status = 'PASS' if self.pass_rate >= pass_threshold else 'FAIL'

    def to_dict(self):
        return {
            'id': self.id,
            'inspection_id': self.inspection_id,
            'batch_id': self.batch_id,
            'product_id': self.product_id,
            'product_name': self.product.name if self.product else 'Unknown Product',
            'inspector': self.inspector,
            'inspection_date': self.inspection_date.strftime('%Y-%m-%d %H:%M:%S') if self.inspection_date else '',
            'total_evaluated': self.total_evaluated,
            'defective_units': self.defective_units,
            'passed_units': self.passed_units,
            'pass_rate': round(self.pass_rate, 2),
            'defect_type': self.defect_type or 'None',
            'remarks': self.remarks or '',
            'qa_status': self.qa_status
        }
