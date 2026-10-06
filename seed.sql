-- Vibe Clothing Company - Seed Data SQL Script

USE vibe_clothing_erp;

-- Users (Password for all accounts is 'admin123' / 'manager123' / 'staff123')
INSERT INTO users (username, email, phone_number, password_hash, role, status) VALUES
('admin', 'admin@vibeclothing.com', '+91 9876543210', 'pbkdf2:sha256:600000$w81729182$hashedpassword_admin123', 'Admin', 'Active'),
('manager', 'manager@vibeclothing.com', '+91 9876543211', 'pbkdf2:sha256:600000$w81729182$hashedpassword_manager123', 'Manager', 'Active'),
('staff', 'staff@vibeclothing.com', '+91 9876543212', 'pbkdf2:sha256:600000$w81729182$hashedpassword_staff123', 'Staff', 'Active');

-- Suppliers
INSERT INTO suppliers (supplier_name, contact_person, email, phone, city, state, country, category, materials_supplied, rating) VALUES
('ABC Textiles', 'Rajesh Kumar', 'orders@abctextiles.com', '+91 9123456789', 'Surat', 'Gujarat', 'India', 'Fabrics', 'Cotton, Silk, Denim', 4.8),
('Chennai Fabric Suppliers', 'Srinivasan M', 'contact@chennaifabric.com', '+91 9444012345', 'Chennai', 'Tamil Nadu', 'India', 'Fabrics', 'Wool, Linen, Blends', 4.6),
('Premium Threads Pvt Ltd', 'Anand Verma', 'sales@premiumthreads.com', '+91 9888123456', 'Coimbatore', 'Tamil Nadu', 'India', 'Trims', 'Spool Threads, Zippers, Buttons', 4.9);

-- Customers
INSERT INTO customers (company_name, contact_person, email, phone, city, state, country, customer_type, website) VALUES
('Flipkart', 'Priya Sharma', 'vendor@flipkart.com', '+91 80 6789 0000', 'Bengaluru', 'Karnataka', 'India', 'Wholesale', 'https://www.flipkart.com'),
('Amazon', 'Vikram Seth', 'fashion-sourcing@amazon.in', '+91 40 4000 1111', 'Hyderabad', 'Telangana', 'India', 'Wholesale', 'https://www.amazon.in'),
('Nykaa', 'Ananya Roy', 'apparel@nykaa.com', '+91 22 6666 8888', 'Mumbai', 'Maharashtra', 'India', 'Retailer', 'https://www.nykaa.com');

-- Material Categories
INSERT INTO material_categories (name, description) VALUES
('Fabrics', 'Raw woven and knitted textiles'),
('Trims & Fasteners', 'Buttons, zippers, rivets, and labels'),
('Packaging', 'Boxes, polybags, and hangtags');
