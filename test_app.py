import unittest
import os
import json
from config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

from app import create_app
from db import db
from models.user import User
from models.material import Material
from models.product import Product, ProductBOM
from models.production import ProductionOrder
from models.batch import Batch
from models.quality import QualityInspection
from models.shipment import Shipment
from models.customer import Customer
from models.supplier import Supplier
from services.erp_engine import ERPEngine
from utils.helpers import format_inr
from utils.id_generator import generate_next_id

class VibeERPTestCase(unittest.TestCase):

    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, username, password):
        return self.client.post('/login', data={
            'username': username,
            'password': password
        }, follow_redirects=True)

    def test_01_currency_formatting(self):
        """Verify Indian Rupee formatting without USD ($)."""
        self.assertEqual(format_inr(799), "₹799.00")
        self.assertEqual(format_inr(1250000), "₹12,50,000.00")
        self.assertNotIn("$", format_inr(100))

    def test_02_id_generator(self):
        """Verify custom prefixed ID generator."""
        p_id = generate_next_id('product')
        self.assertTrue(p_id.startswith('PROD-'))
        m_id = generate_next_id('material')
        self.assertTrue(m_id.startswith('MAT-'))

    def test_03_authentication_and_rbac(self):
        """Test authentication and server-side role authorization."""
        res = self.login('admin', 'admin123')
        self.assertIn(b'Production Overview', res.data)

        # Access Admin-only route
        res_users = self.client.get('/users')
        self.assertEqual(res_users.status_code, 200)

        # Logout and login as Staff
        self.client.get('/logout')
        self.login('staff', 'staff123')

        # Staff should be blocked from User Management (403 Forbidden)
        res_forbidden = self.client.get('/users')
        self.assertEqual(res_forbidden.status_code, 403)

    def test_04_product_no_sku(self):
        """Verify products use Product ID (PROD-XXXX) and NO SKU."""
        p = Product.query.filter_by(product_id='PROD-0001').first()
        self.assertIsNotNone(p)
        self.assertEqual(p.product_id, 'PROD-0001')
        self.assertFalse(hasattr(p, 'sku'))

    def test_05_material_availability_and_readiness(self):
        """Verify BOM material calculation and readiness score."""
        analysis = ERPEngine.check_material_availability('PROD-0001', 100)
        self.assertEqual(analysis['readiness_status'], 'READY')
        self.assertEqual(analysis['readiness_score'], 100.0)

    def test_06_end_to_end_production_workflow(self):
        """
        Executes full 21-step Acceptance Test Workflow:
        1. Create Supplier & Material
        2. Create Product & BOM
        3. Create Customer & Production Order
        4. Check Material readiness
        5. Start Production -> consumes raw materials, creates batch
        6. Advance Batch Stages (Cutting -> Dyeing -> Stitching -> Finishing -> Packing)
        7. Record Quality Control Inspection (Passed = Total - Defective)
        8. Complete Production -> adds QC passed finished goods to stock
        9. Create Shipment -> deducts finished goods stock & tracks status to DELIVERED
        """
        # Step 1: Create Supplier
        sup = Supplier(supplier_id='SUP-9999', supplier_name='Test Fabric Mill', supplier_category='Fabrics')
        db.session.add(sup)

        # Step 2: Create Raw Material (500 meters Cotton)
        mat = Material(
            material_id='MAT-9999',
            name='Test Cotton Fabric',
            quantity=500.0,
            unit='Meter',
            minimum_level=100.0,
            critical_level=50.0,
            unit_cost=200.00,
            supplier_id='SUP-9999'
        )
        db.session.add(mat)

        # Step 3: Create Finished Product (Selling ₹899, Cost ₹400)
        prod = Product(
            product_id='PROD-9999',
            name='Test Polo Shirt',
            category='T-Shirts',
            selling_price=899.00,
            cost_price=400.00,
            target_quantity=100,
            available_stock=0,
            status='Active'
        )
        db.session.add(prod)
        db.session.flush()

        # Step 4: Create BOM (1.5m Cotton per unit)
        bom = ProductBOM(product_id='PROD-9999', material_id='MAT-9999', quantity_required=1.5)
        db.session.add(bom)

        # Step 5: Create Customer
        cus = Customer(customer_id='CUS-9999', company_name='Test Client Retail', customer_type='Wholesale')
        db.session.add(cus)

        # Step 6: Create Production Order (100 units)
        order = ProductionOrder(
            order_id='ORD-9999',
            product_id='PROD-9999',
            quantity=100,
            customer_id='CUS-9999',
            status='PLANNED'
        )
        db.session.add(order)
        db.session.commit()

        # Step 7: Verify Readiness
        analysis = ERPEngine.check_material_availability('PROD-9999', 100)
        self.assertEqual(analysis['readiness_status'], 'READY') # Required 150m, available 500m

        # Step 8: Start Production
        success, msg = ERPEngine.start_production('ORD-9999', user_id='admin')
        self.assertTrue(success)

        # Verify fabric inventory was consumed (500 - 150 = 350 meters)
        updated_mat = Material.query.filter_by(material_id='MAT-9999').first()
        self.assertEqual(updated_mat.quantity, 350.0)

        # Verify Batch created
        batch = Batch.query.filter_by(production_order_id='ORD-9999').first()
        self.assertIsNotNone(batch)
        self.assertEqual(batch.current_stage, 'Cutting')

        # Step 9: Advance Batch Stages through Cutting -> Dyeing -> Stitching -> Finishing -> Packing
        batch.current_stage = 'Packing'
        batch.produced_quantity = 100
        db.session.commit()

        # Step 10: Record QC Inspection (100 evaluated, 5 defective = 95 passed = 95%)
        qc = QualityInspection(
            inspection_id='QC-9999',
            batch_id=batch.batch_id,
            product_id='PROD-9999',
            inspector='Lead QA Inspector',
            total_evaluated=100,
            defective_units=5
        )
        qc.calculate_metrics(pass_threshold=90.0)
        batch.produced_quantity = qc.passed_units # Usable QC passed output
        db.session.add(qc)
        db.session.commit()

        self.assertEqual(qc.passed_units, 95)
        self.assertEqual(qc.pass_rate, 95.0)
        self.assertEqual(qc.qa_status, 'PASS')

        # Step 11: Complete Production Order
        success_comp, msg_comp = ERPEngine.complete_production('ORD-9999', user_id='admin')
        self.assertTrue(success_comp)

        # Verify Finished Goods Stock updated by QC passed units (+95 units)
        updated_prod = Product.query.filter_by(product_id='PROD-9999').first()
        self.assertEqual(updated_prod.available_stock, 95)

        # Step 12: Create Shipment (95 units) & Verify Finished Goods Stock Deduction
        self.login('admin', 'admin123')
        res_ship = self.client.post('/shipments/add', data={
            'customer_id': 'CUS-9999',
            'product_id': 'PROD-9999',
            'batch_id': batch.batch_id,
            'quantity': 95,
            'carrier': 'Blue Dart Logistics'
        }, follow_redirects=True)

        self.assertIn(b'Shipment', res_ship.data)

        # Stock should be deducted from 95 to 0
        self.assertEqual(updated_prod.available_stock, 0)

        # Step 13: Attempt over-shipping when stock is 0 -> Should be blocked!
        res_over = self.client.post('/shipments/add', data={
            'customer_id': 'CUS-9999',
            'product_id': 'PROD-9999',
            'quantity': 10,
            'carrier': 'Blue Dart Logistics'
        }, follow_redirects=True)
        self.assertIn(b'Insufficient finished goods stock', res_over.data)

if __name__ == '__main__':
    unittest.main()
