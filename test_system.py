from app import create_app
from db import db
from models import User, Material, Product, ProductBOM, ProductionOrder

app = create_app()

def run_tests():
    # 1. Test Login with Admin
    with app.test_client() as client:
        response = client.post('/login', data={'username': 'admin', 'password': 'admin123'}, follow_redirects=True)
        assert response.status_code == 200, f"Login failed: {response.status_code}"
        print("✓ Login successful!")

        # 2. Test Main Routes
        routes_to_test = [
            '/',
            '/inventory/',
            '/products/',
            '/production/kanban',
            '/batches/',
            '/customers/',
            '/suppliers/',
            '/quality/',
            '/shipments/',
            '/analytics/',
            '/users/',
            '/notifications/'
        ]

        for route in routes_to_test:
            res = client.get(route)
            assert res.status_code == 200, f"Route {route} returned {res.status_code}"
            print(f"✓ Route {route} -> 200 OK")

        # 3. Setup Test Orders
        with app.app_context():
            ProductionOrder.query.filter(ProductionOrder.order_number.in_(["ORD-TEST-INSUFFICIENT", "ORD-TEST-VALID"])).delete()
            db.session.commit()

            prod = Product.query.first()
            mat = Material.query.first()

            # Ensure BOM exists
            bom_item = ProductBOM.query.filter_by(product_id=prod.id, material_id=mat.id).first()
            if not bom_item:
                bom_item = ProductBOM(product_id=prod.id, material_id=mat.id, required_quantity=2.0)
                db.session.add(bom_item)
                db.session.commit()

            print(f"Testing BOM: Product '{prod.name}' requires {bom_item.required_quantity} of '{mat.name}' per unit.")

            huge_order = ProductionOrder(
                order_number="ORD-TEST-INSUFFICIENT",
                product_id=prod.id,
                quantity=10000,
                status="Planned"
            )
            db.session.add(huge_order)
            db.session.commit()
            huge_order_id = huge_order.id

        # 4. Attempt to start order with insufficient stock
        res_start = client.post(f'/production/start/{huge_order_id}', follow_redirects=True)
        assert res_start.status_code == 200
        assert b"Insufficient inventory to start production" in res_start.data, "Expected warning alert for insufficient inventory!"
        print("✓ Insufficient stock warning correctly displayed and blocked order start!")

        # 5. Create manageable order with sufficient stock
        with app.app_context():
            prod = Product.query.first()
            mat = Material.query.first()
            bom_item = ProductBOM.query.filter_by(product_id=prod.id, material_id=mat.id).first()

            mat.quantity = 50.0  # set ample stock
            db.session.commit()
            initial_stock = mat.quantity
            required_needed = bom_item.required_quantity * 5

            valid_order = ProductionOrder(
                order_number="ORD-TEST-VALID",
                product_id=prod.id,
                quantity=5,
                status="Planned"
            )
            db.session.add(valid_order)
            db.session.commit()
            valid_order_id = valid_order.id

        # 6. Start valid order
        res_valid = client.post(f'/production/start/{valid_order_id}', follow_redirects=True)
        assert res_valid.status_code == 200
        assert b"started successfully" in res_valid.data or b"In Progress" in res_valid.data

        # 7. Verify stock deduction
        with app.app_context():
            mat = Material.query.first()
            expected_stock = initial_stock - required_needed
            assert abs(mat.quantity - expected_stock) < 0.001, f"Expected stock {expected_stock}, got {mat.quantity}"
            print(f"✓ Valid order started successfully! Raw material stock deducted from {initial_stock} to {mat.quantity}.")

            # Clean up test orders
            ProductionOrder.query.filter(ProductionOrder.order_number.in_(["ORD-TEST-INSUFFICIENT", "ORD-TEST-VALID"])).delete()
            db.session.commit()

        print("\nALL VERIFICATION TESTS PASSED 100% SUCCESSFULLY!")

if __name__ == '__main__':
    run_tests()
