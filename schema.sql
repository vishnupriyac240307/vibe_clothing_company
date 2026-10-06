-- Vibe Clothing Company - Smart Production & Manufacturing Management System
-- Relational MySQL Schema Definition

CREATE DATABASE IF NOT EXISTS vibe_clothing_erp;
USE vibe_clothing_erp;

-- 1. Users & RBAC
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone_number VARCHAR(20),
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'Staff',
    status VARCHAR(20) NOT NULL DEFAULT 'Active',
    last_login DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    action VARCHAR(100) NOT NULL,
    module VARCHAR(50) NOT NULL,
    record_id VARCHAR(50),
    description TEXT,
    ip_address VARCHAR(45),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 2. Suppliers & Customers
CREATE TABLE IF NOT EXISTS suppliers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL UNIQUE,
    logo_url TEXT,
    contact_person VARCHAR(100),
    email VARCHAR(120),
    phone VARCHAR(30),
    tax_id VARCHAR(50),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'India',
    category VARCHAR(50) DEFAULT 'Fabrics',
    materials_supplied TEXT,
    payment_terms VARCHAR(100) DEFAULT 'Net 30',
    rating FLOAT DEFAULT 4.5,
    status VARCHAR(20) DEFAULT 'Active',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL UNIQUE,
    logo_url TEXT,
    contact_person VARCHAR(100),
    email VARCHAR(120),
    phone VARCHAR(30),
    tax_id VARCHAR(50),
    address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50) DEFAULT 'India',
    customer_type VARCHAR(50) DEFAULT 'Wholesale',
    website VARCHAR(150),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 3. Inventory & Materials
CREATE TABLE IF NOT EXISTS material_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(150) NOT NULL,
    category_id INT,
    description TEXT,
    quantity FLOAT NOT NULL DEFAULT 0.0,
    unit VARCHAR(20) NOT NULL DEFAULT 'Meter',
    color VARCHAR(50),
    size_spec VARCHAR(100),
    min_level FLOAT NOT NULL DEFAULT 50.0,
    reorder_level FLOAT NOT NULL DEFAULT 100.0,
    critical_level FLOAT NOT NULL DEFAULT 20.0,
    unit_cost FLOAT NOT NULL DEFAULT 0.0,
    supplier_id INT,
    storage_location VARCHAR(100) DEFAULT 'Warehouse A',
    batch_number VARCHAR(50),
    expiry_date DATE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES material_categories(id) ON DELETE SET NULL,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS inventory_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    material_id INT NOT NULL,
    transaction_type VARCHAR(50) NOT NULL,
    quantity FLOAT NOT NULL,
    previous_quantity FLOAT NOT NULL,
    new_quantity FLOAT NOT NULL,
    reference VARCHAR(100),
    user_id INT,
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 4. Products & Bill of Materials (BOM)
CREATE TABLE IF NOT EXISTS product_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    sku VARCHAR(50) NOT NULL UNIQUE,
    category_id INT,
    description TEXT,
    image_url TEXT,
    size VARCHAR(50),
    color VARCHAR(50),
    selling_price FLOAT NOT NULL DEFAULT 0.0,
    cost_price FLOAT NOT NULL DEFAULT 0.0,
    target_production_qty INT NOT NULL DEFAULT 100,
    stock_quantity INT NOT NULL DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES product_categories(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS product_bom (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    material_id INT NOT NULL,
    required_quantity FLOAT NOT NULL DEFAULT 1.0,
    unit VARCHAR(20) NOT NULL DEFAULT 'Meter',
    notes TEXT,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
    FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE CASCADE
);

-- 5. Production Orders & Batches
CREATE TABLE IF NOT EXISTS production_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(50) NOT NULL UNIQUE,
    product_id INT NOT NULL,
    customer_id INT,
    quantity INT NOT NULL DEFAULT 100,
    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
    start_date DATE,
    expected_completion_date DATE,
    supervisor_id INT,
    status VARCHAR(30) NOT NULL DEFAULT 'PLANNED',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (supervisor_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_code VARCHAR(50) NOT NULL UNIQUE,
    production_order_id INT NOT NULL UNIQUE,
    product_id INT NOT NULL,
    customer_id INT,
    target_quantity INT NOT NULL DEFAULT 100,
    produced_quantity INT NOT NULL DEFAULT 0,
    supervisor_id INT,
    start_date DATE,
    expected_completion DATE,
    current_stage VARCHAR(30) NOT NULL DEFAULT 'Cutting',
    status VARCHAR(30) NOT NULL DEFAULT 'IN_PROGRESS',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (production_order_id) REFERENCES production_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (supervisor_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS batch_stage_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    stage VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'COMPLETED',
    updated_by_user_id INT,
    notes TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
    FOREIGN KEY (updated_by_user_id) REFERENCES users(id) ON DELETE SET NULL
);

-- 6. Quality Inspections & Shipments
CREATE TABLE IF NOT EXISTS quality_inspections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT NOT NULL,
    product_id INT NOT NULL,
    inspector_id INT,
    inspection_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_evaluated INT NOT NULL DEFAULT 0,
    defective_units INT NOT NULL DEFAULT 0,
    passed_units INT NOT NULL DEFAULT 0,
    defect_type VARCHAR(100),
    remarks TEXT,
    qa_status VARCHAR(20) NOT NULL DEFAULT 'PASS',
    pass_rate FLOAT NOT NULL DEFAULT 100.0,
    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (inspector_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS shipments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    shipment_number VARCHAR(50) NOT NULL UNIQUE,
    batch_id INT,
    production_order_id INT,
    product_id INT NOT NULL,
    customer_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    carrier VARCHAR(100) DEFAULT 'FedEx',
    tracking_number VARCHAR(100) UNIQUE,
    shipment_date DATE,
    expected_delivery DATE,
    actual_delivery DATE,
    status VARCHAR(30) NOT NULL DEFAULT 'READY',
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (batch_id) REFERENCES batches(id) ON DELETE SET NULL,
    FOREIGN KEY (production_order_id) REFERENCES production_orders(id) ON DELETE SET NULL,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE RESTRICT
);

-- 7. Audit & Operational Transactions & Notifications
CREATE TABLE IF NOT EXISTS operational_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    transaction_type VARCHAR(50) NOT NULL,
    reference VARCHAR(100),
    entity_name VARCHAR(100) NOT NULL,
    entity_id VARCHAR(50),
    quantity FLOAT,
    user_id INT,
    description TEXT,
    previous_state VARCHAR(100),
    new_state VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(150) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    user_id INT,
    link VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
