-- VIBE CLOTHING COMPANY — Smart Production & Manufacturing ERP Schema
-- Compatible with MySQL 5.7+ / 8.0+

CREATE DATABASE IF NOT EXISTS vibe_clothing_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE vibe_clothing_db;

-- 1. Users & RBAC
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(20) NOT NULL UNIQUE,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20),
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'staff',
    is_active BOOLEAN DEFAULT TRUE,
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_username (username)
) ENGINE=InnoDB;

-- 2. Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id VARCHAR(20) NOT NULL UNIQUE,
    supplier_name VARCHAR(120) NOT NULL,
    logo_url VARCHAR(255),
    contact_person VARCHAR(80),
    email VARCHAR(120),
    phone VARCHAR(20),
    gst_id VARCHAR(30),
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'India',
    supplier_category VARCHAR(50) DEFAULT 'Fabrics',
    payment_terms VARCHAR(50) DEFAULT 'Net 30',
    rating FLOAT DEFAULT 4.5,
    status VARCHAR(20) DEFAULT 'Active',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_supplier_id (supplier_id)
) ENGINE=InnoDB;

-- 3. Customers
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(120) NOT NULL,
    logo_url VARCHAR(255),
    contact_person VARCHAR(80),
    email VARCHAR(120),
    phone VARCHAR(20),
    gst_id VARCHAR(30),
    address VARCHAR(255),
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'India',
    customer_type VARCHAR(30) DEFAULT 'Wholesale',
    status VARCHAR(20) DEFAULT 'Active',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_customer_id (customer_id)
) ENGINE=InnoDB;

-- 4. Materials (Inventory)
CREATE TABLE IF NOT EXISTS materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_id VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    code VARCHAR(50),
    category VARCHAR(50) NOT NULL DEFAULT 'Fabric',
    description TEXT,
    quantity FLOAT NOT NULL DEFAULT 0.0,
    unit VARCHAR(20) NOT NULL DEFAULT 'Meter',
    color VARCHAR(50),
    specifications VARCHAR(255),
    minimum_level FLOAT NOT NULL DEFAULT 100.0,
    reorder_level FLOAT NOT NULL DEFAULT 150.0,
    critical_level FLOAT NOT NULL DEFAULT 50.0,
    unit_cost FLOAT NOT NULL DEFAULT 0.0,
    supplier_id VARCHAR(20),
    storage_location VARCHAR(100),
    batch_number VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
    INDEX idx_material_id (material_id),
    INDEX idx_material_name (name)
) ENGINE=InnoDB;

-- 5. Products (NO SKU FIELD)
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'T-Shirts',
    description TEXT,
    image_url VARCHAR(255),
    size VARCHAR(20) NOT NULL DEFAULT 'M',
    color VARCHAR(50),
    selling_price FLOAT NOT NULL DEFAULT 0.0,
    cost_price FLOAT NOT NULL DEFAULT 0.0,
    target_quantity INT NOT NULL DEFAULT 100,
    available_stock INT NOT NULL DEFAULT 0,
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_product_id (product_id),
    INDEX idx_product_name (name)
) ENGINE=InnoDB;

-- 6. Product Bill of Materials (BOM)
CREATE TABLE IF NOT EXISTS product_bom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id VARCHAR(20) NOT NULL,
    material_id VARCHAR(20) NOT NULL,
    quantity_required FLOAT NOT NULL DEFAULT 1.0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materials(material_id) ON DELETE CASCADE,
    INDEX idx_bom_product (product_id)
) ENGINE=InnoDB;

-- 7. Production Orders
CREATE TABLE IF NOT EXISTS production_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL UNIQUE,
    product_id VARCHAR(20) NOT NULL,
    quantity INT NOT NULL DEFAULT 100,
    customer_id VARCHAR(20),
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    start_date DATE,
    expected_completion DATE,
    assigned_supervisor VARCHAR(80),
    status VARCHAR(20) NOT NULL DEFAULT 'PLANNED',
    material_availability_pct FLOAT DEFAULT 100.0,
    readiness_score FLOAT DEFAULT 100.0,
    readiness_status VARCHAR(20) DEFAULT 'READY',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    INDEX idx_order_id (order_id)
) ENGINE=InnoDB;

-- 8. Batches
CREATE TABLE IF NOT EXISTS batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id VARCHAR(20) NOT NULL UNIQUE,
    batch_code VARCHAR(50),
    production_order_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    target_quantity INT NOT NULL DEFAULT 100,
    produced_quantity INT NOT NULL DEFAULT 0,
    supervisor VARCHAR(80),
    customer_id VARCHAR(20),
    start_date DATE,
    expected_completion DATE,
    current_stage VARCHAR(30) NOT NULL DEFAULT 'Cutting',
    status VARCHAR(20) NOT NULL DEFAULT 'In Progress',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (production_order_id) REFERENCES production_orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE SET NULL,
    INDEX idx_batch_id (batch_id)
) ENGINE=InnoDB;

-- 9. Quality Inspections
CREATE TABLE IF NOT EXISTS quality_inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(20) NOT NULL UNIQUE,
    batch_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    inspector VARCHAR(80) NOT NULL DEFAULT 'QA Inspector',
    inspection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_evaluated INT NOT NULL DEFAULT 100,
    defective_units INT NOT NULL DEFAULT 0,
    passed_units INT NOT NULL DEFAULT 100,
    pass_rate FLOAT NOT NULL DEFAULT 100.0,
    defect_type VARCHAR(100),
    remarks TEXT,
    qa_status VARCHAR(10) NOT NULL DEFAULT 'PASS',
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    INDEX idx_inspection_id (inspection_id)
) ENGINE=InnoDB;

-- 10. Shipments
CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_id VARCHAR(20) NOT NULL UNIQUE,
    batch_id VARCHAR(20),
    production_order_id VARCHAR(20),
    product_id VARCHAR(20) NOT NULL,
    customer_id VARCHAR(20) NOT NULL,
    quantity INT NOT NULL DEFAULT 100,
    carrier VARCHAR(80) NOT NULL DEFAULT 'Blue Dart Logistics',
    tracking_number VARCHAR(50),
    shipment_date DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'READY',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    INDEX idx_shipment_id (shipment_id)
) ENGINE=InnoDB;

-- 11. Inventory Transactions
CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_id VARCHAR(30) NOT NULL UNIQUE,
    material_id VARCHAR(20) NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    quantity FLOAT NOT NULL,
    previous_quantity FLOAT NOT NULL,
    new_quantity FLOAT NOT NULL,
    reference VARCHAR(100),
    user_id VARCHAR(80) NOT NULL DEFAULT 'System',
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(material_id),
    INDEX idx_trans_id (transaction_id)
) ENGINE=InnoDB;

-- 12. Activity Logs
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id VARCHAR(80) NOT NULL DEFAULT 'System',
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    record_id VARCHAR(50),
    description TEXT NOT NULL,
    ip_address VARCHAR(45),
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_activity_module (module)
) ENGINE=InnoDB;

-- 13. Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'info',
    link VARCHAR(255),
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
