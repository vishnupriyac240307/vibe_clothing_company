import unittest
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from db import db
from config import Config
from models import (
    User, Material, MaterialCategory, Product, ProductCategory, ProductBOM,
    ProductionOrder, Batch, QualityInspection, Shipment, Customer, Supplier
)

class TestErpWorkflow(unittest.TestCase):
    def setUp(self):
        class TestConfig(Config):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SECRET_KEY = 'test-key'
            WTF_CSRF_ENABLED = False

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_end_to_end_manufacturing_workflow(self):
        # 1. Retrieve or Create Admin User
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='test_admin', email='test_admin@test.com', role='Admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

        # 2. Retrieve or Create Supplier & Raw Material Category
        supplier = Supplier.query.first()
        if not supplier:
            supplier = Supplier(supplier_name='Surat Mills', rating=4.5)
            db.session.add(supplier)
            db.session.commit()

        cat_fab = MaterialCategory.query.filter_by(name='Fabrics').first()
        if not cat_fab:
            cat_fab = MaterialCategory(name='Fabrics')
            db.session.add(cat_fab)
            db.session.commit()

        cotton = Material(
            material_code='MAT-TEST-500', name='Test Cotton 180GSM', category_id=cat_fab.id,
            quantity=500.0, unit='Meter', min_level=100.0, critical_level=20.0, unit_cost=5.0,
            supplier_id=supplier.id
        )
        db.session.add(cotton)
        db.session.commit()
        self.assertEqual(cotton.quantity, 500.0)

        # 3. Create Product & BOM (100 T-Shirts = 150 meters Cotton)
        cat_app = ProductCategory.query.first()
        if not cat_app:
            cat_app = ProductCategory(name='Apparel')
            db.session.add(cat_app)
            db.session.commit()

        tshirt = Product(name='Test T-Shirt', sku='PRD-TSH-TEST', category_id=cat_app.id, selling_price=25.0, cost_price=10.0)
        db.session.add(tshirt)
        db.session.commit()

        bom = ProductBOM(product_id=tshirt.id, material_id=cotton.id, required_quantity=1.5, unit='Meter')
        db.session.add(bom)
        db.session.commit()

        # 4. Create Customer & Production Order
        customer = Customer.query.first()
        if not customer:
            customer = Customer(company_name='Flipkart')
            db.session.add(customer)
            db.session.commit()

        order = ProductionOrder(order_number='PO-TEST-1001', product_id=tshirt.id, customer_id=customer.id, quantity=100, status='PLANNED')
        db.session.add(order)
        db.session.commit()

        # 5. Start Production via Service
        from services.production_service import start_production_order, complete_production_order
        success, msg = start_production_order(order.id, admin.id)
        self.assertTrue(success)

        # Verify Material Quantity decreased by 150m (500 - 150 = 350)
        cotton_updated = Material.query.get(cotton.id)
        self.assertEqual(cotton_updated.quantity, 350.0)

        # Verify Batch created in stage 'Cutting'
        batch = Batch.query.filter_by(production_order_id=order.id).first()
        self.assertIsNotNone(batch)
        self.assertEqual(batch.current_stage, 'Cutting')

        # 6. Quality Control Inspection (100 evaluated, 95 passed = 95% pass rate -> PASS)
        qc = QualityInspection(
            batch_id=batch.id, product_id=tshirt.id, inspector_id=admin.id,
            total_evaluated=100, defective_units=5, passed_units=95,
            pass_rate=95.0, qa_status='PASS'
        )
        db.session.add(qc)
        db.session.commit()

        # 7. Complete Production Order
        c_success, c_msg = complete_production_order(order.id, admin.id)
        self.assertTrue(c_success)
        self.assertEqual(tshirt.stock_quantity, 100)

        # 8. Create Shipment
        shipment = Shipment(
            shipment_number='SHP-TEST-1001', batch_id=batch.id, production_order_id=order.id,
            product_id=tshirt.id, customer_id=customer.id, quantity=95, carrier='FedEx', status='READY'
        )
        db.session.add(shipment)
        db.session.commit()

        # Advance shipment status to DELIVERED
        shipment.status = 'DELIVERED'
        db.session.commit()
        self.assertEqual(shipment.status, 'DELIVERED')

        print("End-to-End Manufacturing Integration Test Passed Successfully!")

    def test_all_view_routes_render(self):
        admin = User.query.filter_by(username='admin').first()
        with self.client.session_transaction() as sess:
            sess['user_id'] = admin.id
            sess['username'] = admin.username
            sess['user_role'] = admin.role

        routes = [
            '/dashboard',
            '/inventory',
            '/products',
            '/production',
            '/batches',
            '/quality',
            '/shipments',
            '/customers',
            '/suppliers',
            '/analytics',
            '/users',
            '/activity-logs',
            '/traceability'
        ]

        for route in routes:
            response = self.client.get(route)
            self.assertEqual(response.status_code, 200, f"Route {route} failed with status {response.status_code}")
        print("All view routes rendered without error (200 OK)!")

if __name__ == '__main__':
    unittest.main()
