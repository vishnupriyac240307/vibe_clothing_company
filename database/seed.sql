-- VIBE CLOTHING COMPANY — Production Seed Data Script

USE vibe_clothing_db;

-- Clear Existing
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE notifications;
TRUNCATE TABLE activity_logs;
TRUNCATE TABLE inventory_transactions;
TRUNCATE TABLE shipments;
TRUNCATE TABLE quality_inspections;
TRUNCATE TABLE batches;
TRUNCATE TABLE production_orders;
TRUNCATE TABLE product_bom;
TRUNCATE TABLE products;
TRUNCATE TABLE materials;
TRUNCATE TABLE customers;
TRUNCATE TABLE suppliers;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Users (Passwords: admin123, manager123, staff123)
-- Hash generated using scrypt / pbkdf2 werkzeug format
INSERT INTO users (user_id, username, email, phone, password_hash, role, is_active) VALUES
('USR-0001', 'admin', 'admin@vibeclothing.com', '+91 98765 43210', 'scrypt:32768:8:1$uH3y4rSg9ZzK$5188f6cbb70591fef7cdd05b6324a3c1143c35f29d20c5d5e5e33d45c5dbb0ed350ec7e2a9b3d1ffaa0a20a40f8a84eb', 'admin', 1),
('USR-0002', 'manager', 'manager@vibeclothing.com', '+91 98765 43211', 'scrypt:32768:8:1$uH3y4rSg9ZzK$b3df9bb56f081467e231b1e9c20a4732104192bdf23214bc12301824ab1123de39103cba219a12bc901a18bc00119abb', 'manager', 1),
('USR-0003', 'staff', 'staff@vibeclothing.com', '+91 98765 43212', 'scrypt:32768:8:1$uH3y4rSg9ZzK$1284a12bfe29103c8b120491823901bcf91283c01823ab09123cba0129381928371982739128ab81273c8293712893bc', 'staff', 1);

-- 2. Suppliers
INSERT INTO suppliers (supplier_id, supplier_name, logo_url, contact_person, email, phone, gst_id, address, city, state, country, supplier_category, payment_terms, rating) VALUES
('SUP-0001', 'ABC Textiles', 'https://logo.clearbit.com/abctextiles.in', 'Rajesh Sharma', 'sales@abctextiles.in', '+91 44 2345 6789', '33AAACA1234A1Z5', '12 Industrial Estate, Guindy', 'Chennai', 'Tamil Nadu', 'India', 'Fabrics', 'Net 30', 4.8),
('SUP-0002', 'Chennai Fabric Suppliers', 'https://ui-avatars.com/api/?name=Chennai+Fabric&background=0f172a&color=38bdf8', 'Suresh Kumar', 'info@chennaifabrics.com', '+91 44 8765 4321', '33BBBBA5678B1Z2', '45 Textile Hub, Tirupur', 'Tirupur', 'Tamil Nadu', 'India', 'Knitted Fabrics', 'Net 15', 4.5),
('SUP-0003', 'Premium Threads Pvt Ltd', 'https://ui-avatars.com/api/?name=Premium+Threads&background=0f172a&color=38bdf8', 'Anita Roy', 'orders@premiumthreads.in', '+91 80 4123 9988', '29CCCCA9988C1Z9', '88 Garment Zone, Peenya', 'Bengaluru', 'Karnataka', 'India', 'Threads & Yarns', 'Advance', 4.9);

-- 3. Customers
INSERT INTO customers (customer_id, company_name, logo_url, contact_person, email, phone, gst_id, address, city, state, country, customer_type) VALUES
('CUS-0001', 'Flipkart', 'https://logo.clearbit.com/flipkart.com', 'Vikram Sethi', 'vendor@flipkart.com', '+91 80 4900 0000', '29AABCF1234F1Z1', 'Outer Ring Road, Devarabeesanahalli', 'Bengaluru', 'Karnataka', 'India', 'E-Commerce'),
('CUS-0002', 'Amazon India', 'https://logo.clearbit.com/amazon.in', 'Priya Menon', 'retail-in@amazon.com', '+91 80 4000 1111', '29AABCA9999A1Z3', 'World Trade Centre, Brigade Gateway', 'Bengaluru', 'Karnataka', 'India', 'E-Commerce'),
('CUS-0003', 'Nykaa', 'https://logo.clearbit.com/nykaa.com', 'Rohan Gupta', 'fashion-sourcing@nykaa.com', '+91 22 6600 8800', '27AAACN5555N1Z8', '104 Sun Mill Compound, Lower Parel', 'Mumbai', 'Maharashtra', 'India', 'Retail Chain');

-- 4. Materials (Inventory)
INSERT INTO materials (material_id, name, code, category, description, quantity, unit, color, minimum_level, reorder_level, critical_level, unit_cost, supplier_id, storage_location, batch_number) VALUES
('MAT-0001', 'Cotton Fabric', 'MAT-COT-01', 'Fabric', '100% Organic Combed Cotton 180 GSM', 500.0, 'Meter', 'Super White', 100.0, 150.0, 50.0, 250.00, 'SUP-0001', 'Rack A-12', 'LOT-COT-2026-01'),
('MAT-0002', 'Wool', 'MAT-WOL-01', 'Fabric', 'Premium Australian Merino Wool Blend', 300.0, 'Meter', 'Navy Blue', 80.0, 120.0, 30.0, 450.00, 'SUP-0001', 'Rack A-14', 'LOT-WOL-2026-02'),
('MAT-0003', 'Thread', 'MAT-TRD-01', 'Trims', 'High-Tenacity Polyester Sewing Thread', 10000.0, 'Meter', 'White & Black', 2000.0, 3000.0, 800.0, 2.50, 'SUP-0003', 'Bin T-04', 'LOT-TRD-2026-05'),
('MAT-0004', 'Buttons', 'MAT-BTN-01', 'Accessories', 'Resin 4-Hole Shirt Buttons 18L', 5000.0, 'PCS', 'Matte Black', 1000.0, 1500.0, 400.0, 5.00, 'SUP-0003', 'Bin B-02', 'LOT-BTN-2026-09'),
('MAT-0005', 'Pin', 'MAT-PIN-01', 'Accessories', 'Stainless Steel Garment Packaging Pins', 2000.0, 'PCS', 'Silver', 500.0, 800.0, 200.0, 1.50, 'SUP-0003', 'Bin B-05', 'LOT-PIN-2026-01'),
('MAT-0006', 'Dye', 'MAT-DYE-01', 'Chemicals', 'Eco-Friendly Reactive Textile Dye Liquid', 150.0, 'Liter', 'Royal Blue', 40.0, 60.0, 15.0, 350.00, 'SUP-0002', 'Drum C-01', 'LOT-DYE-2026-03');

-- 5. Products (NO SKU)
INSERT INTO products (product_id, name, category, description, image_url, size, color, selling_price, cost_price, target_quantity, available_stock, status) VALUES
('PROD-0001', 'Cotton T-Shirt', 'T-Shirts', 'Premium 100% Combed Cotton Crew Neck T-Shirt', 'https://images.unsplash.com/photo-1521572267360-ee0c2909d518?w=500&auto=format&fit=crop&q=80', 'M', 'White', 799.00, 450.00, 500, 150, 'Active'),
('PROD-0002', 'Jeans', 'Bottom Wear', 'Slim Fit Stretch Denim Jeans with 5 Pockets', 'https://images.unsplash.com/photo-1541099649105-f69ad21f3246?w=500&auto=format&fit=crop&q=80', '32', 'Dark Blue', 1899.00, 950.00, 300, 80, 'Active'),
('PROD-0003', 'Denim Jacket', 'Jackets', 'Classic Heavyweight Denim Trucker Jacket', 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=500&auto=format&fit=crop&q=80', 'L', 'Indigo Wash', 2499.00, 1350.00, 200, 45, 'In Production'),
('PROD-0004', 'Hoodie', 'Outerwear', 'Fleece Lined Pullover Hoodie with Kangaroo Pocket', 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=500&auto=format&fit=crop&q=80', 'XL', 'Heather Grey', 1499.00, 750.00, 250, 95, 'Active');

-- 6. Product BOMs
INSERT INTO product_bom (product_id, material_id, quantity_required) VALUES
('PROD-0001', 'MAT-0001', 1.5),
('PROD-0001', 'MAT-0003', 50.0),
('PROD-0001', 'MAT-0004', 3.0),
('PROD-0002', 'MAT-0001', 2.2),
('PROD-0002', 'MAT-0003', 80.0),
('PROD-0002', 'MAT-0004', 2.0),
('PROD-0003', 'MAT-0001', 2.8),
('PROD-0003', 'MAT-0003', 120.0),
('PROD-0003', 'MAT-0004', 6.0),
('PROD-0004', 'MAT-0002', 2.0),
('PROD-0004', 'MAT-0003', 90.0);

-- 7. Production Orders
INSERT INTO production_orders (order_id, product_id, quantity, customer_id, priority, start_date, expected_completion, assigned_supervisor, status, material_availability_pct, readiness_score, readiness_status, notes) VALUES
('ORD-0001', 'PROD-0001', 100, 'CUS-0001', 'High', CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 7 DAY), 'Ramesh Pal', 'IN_PROGRESS', 100.0, 100.0, 'READY', 'Priority order for Flipkart Big Savings Day'),
('ORD-0002', 'PROD-0003', 50, 'CUS-0002', 'Medium', CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 12 DAY), 'Anita Roy', 'PLANNED', 100.0, 100.0, 'READY', 'Autumn jacket replenishment batch'),
('ORD-0003', 'PROD-0002', 200, 'CUS-0003', 'High', DATE_SUB(CURRENT_DATE, INTERVAL 10 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 'Suresh Kumar', 'COMPLETED', 100.0, 100.0, 'READY', 'Nykaa Festive launch stock order');

-- 8. Batches
INSERT INTO batches (batch_id, batch_code, production_order_id, product_id, target_quantity, produced_quantity, supervisor, customer_id, start_date, expected_completion, current_stage, status) VALUES
('BAT-0001', 'BAT-ORD-0001', 'ORD-0001', 'PROD-0001', 100, 60, 'Ramesh Pal', 'CUS-0001', CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 7 DAY), 'Stitching', 'In Progress'),
('BAT-0002', 'BAT-ORD-0003', 'ORD-0003', 'PROD-0002', 200, 192, 'Suresh Kumar', 'CUS-0003', DATE_SUB(CURRENT_DATE, INTERVAL 10 DAY), DATE_SUB(CURRENT_DATE, INTERVAL 2 DAY), 'Packing', 'Completed');

-- 9. Quality Inspections
INSERT INTO quality_inspections (inspection_id, batch_id, product_id, inspector, inspection_date, total_evaluated, defective_units, passed_units, pass_rate, defect_type, remarks, qa_status) VALUES
('QC-0001', 'BAT-0002', 'PROD-0002', 'Deepak QA Lead', CURRENT_TIMESTAMP, 200, 8, 192, 96.0, 'Minor Loose Stitching', 'Passed QA threshold (>90%). 8 units set aside for re-work.', 'PASS');

-- 10. Shipments
INSERT INTO shipments (shipment_id, batch_id, production_order_id, product_id, customer_id, quantity, carrier, tracking_number, shipment_date, expected_delivery, status, notes) VALUES
('SHP-0001', 'BAT-0002', 'ORD-0003', 'PROD-0002', 'CUS-0003', 192, 'Blue Dart Logistics', 'BD-98210384', CURRENT_DATE, DATE_ADD(CURRENT_DATE, INTERVAL 3 DAY), 'IN_TRANSIT', 'Dispatched from Tirupur hub via Express Air Cargo');

-- 11. Inventory Transactions
INSERT INTO inventory_transactions (transaction_id, material_id, transaction_type, quantity, previous_quantity, new_quantity, reference, user_id, remarks) VALUES
('INV-TXN-0001', 'MAT-0001', 'Stock In', 650.0, 0.0, 650.0, 'PO-9912', 'admin', 'Initial stock receipt from ABC Textiles'),
('INV-TXN-0002', 'MAT-0001', 'Production Consumption', 150.0, 650.0, 500.0, 'ORD-0001', 'admin', 'Consumed 150m for Production Order ORD-0001 (100x Cotton T-Shirt)');

-- 12. Activity Logs
INSERT INTO activity_logs (user_id, action, module, record_id, description, ip_address) VALUES
('admin', 'System Initialized', 'Auth', 'SYS-001', 'Vibe Clothing Company ERP database seeded successfully.', '127.0.0.1'),
('admin', 'Start Production', 'Production', 'ORD-0001', 'Started production order ORD-0001 for 100 Cotton T-Shirts.', '127.0.0.1'),
('manager', 'Record QC Inspection', 'Quality', 'QC-0001', 'Recorded QC inspection for BAT-0002. Pass rate 96.0%.', '127.0.0.1');

-- 13. Notifications
INSERT INTO notifications (title, message, type, link) VALUES
('Production Started: ORD-0001', 'Production order ORD-0001 for Cotton T-Shirt is now IN PROGRESS.', 'success', '/production'),
('Quality Inspection Passed: QC-0001', 'Batch BAT-0002 passed quality inspection with 96% pass rate.', 'info', '/quality');
