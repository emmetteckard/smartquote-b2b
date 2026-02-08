-- SmartQuote Database Schema
-- PostgreSQL 14+

-- Create database (run separately)
-- CREATE DATABASE smartquote;

-- ============================================
-- 1. ROLES & USERS
-- ============================================

CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255) NOT NULL,
    role_id INTEGER REFERENCES roles(id),
    client_id INTEGER REFERENCES clients(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role_id);

-- ============================================
-- 2. CLIENTS
-- ============================================

CREATE TABLE clients (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(255),
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    tax_id VARCHAR(100),
    payment_terms INTEGER DEFAULT 30,
    credit_limit DECIMAL(15, 2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 3. PRODUCTS
-- ============================================

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    unit VARCHAR(50) DEFAULT 'pcs',
    min_order_qty INTEGER DEFAULT 1,
    lingxing_product_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 4. PRICING
-- ============================================

CREATE TABLE base_prices (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    tier VARCHAR(10) NOT NULL,
    price DECIMAL(15, 2) NOT NULL,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, tier, effective_from)
);

CREATE INDEX idx_base_prices_product ON base_prices(product_id);

CREATE TABLE client_prices (
    id SERIAL PRIMARY KEY,
    client_id INTEGER REFERENCES clients(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    price DECIMAL(15, 2) NOT NULL,
    is_protected BOOLEAN DEFAULT FALSE,
    effective_from DATE NOT NULL,
    effective_to DATE,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(client_id, product_id, effective_from)
);

CREATE INDEX idx_client_prices_client ON client_prices(client_id);
CREATE INDEX idx_client_prices_product ON client_prices(product_id);

CREATE TABLE price_history (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    client_id INTEGER,
    tier VARCHAR(10),
    old_price DECIMAL(15, 2),
    new_price DECIMAL(15, 2),
    change_type VARCHAR(50),
    reason TEXT,
    changed_by INTEGER REFERENCES users(id),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 5. INVENTORY
-- ============================================

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    warehouse_code VARCHAR(50),
    available_qty INTEGER DEFAULT 0,
    reserved_qty INTEGER DEFAULT 0,
    total_qty INTEGER GENERATED ALWAYS AS (available_qty + reserved_qty) STORED,
    last_sync_at TIMESTAMP,
    lingxing_warehouse_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, warehouse_code)
);

CREATE INDEX idx_inventory_product ON inventory(product_id);

-- ============================================
-- 6. QUOTATIONS
-- ============================================

CREATE TABLE quotations (
    id SERIAL PRIMARY KEY,
    quotation_number VARCHAR(50) UNIQUE NOT NULL,
    client_id INTEGER REFERENCES clients(id),
    status VARCHAR(50) DEFAULT 'draft',
    total_amount DECIMAL(15, 2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    valid_until DATE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_quotations_client ON quotations(client_id);
CREATE INDEX idx_quotations_status ON quotations(status);

CREATE TABLE quotation_items (
    id SERIAL PRIMARY KEY,
    quotation_id INTEGER REFERENCES quotations(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_percent / 100)) STORED,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 7. ORDERS
-- ============================================

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    quotation_id INTEGER REFERENCES quotations(id),
    client_id INTEGER REFERENCES clients(id),
    status VARCHAR(50) DEFAULT 'pending_payment',
    total_amount DECIMAL(15, 2) DEFAULT 0,
    currency VARCHAR(10) DEFAULT 'USD',
    payment_status VARCHAR(50) DEFAULT 'unpaid',
    stock_locked BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_orders_client ON orders(client_id);
CREATE INDEX idx_orders_status ON orders(status);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(15, 2) NOT NULL,
    discount_percent DECIMAL(5, 2) DEFAULT 0,
    line_total DECIMAL(15, 2) GENERATED ALWAYS AS (quantity * unit_price * (1 - discount_percent / 100)) STORED,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 8. PAYMENTS
-- ============================================

CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id),
    payment_method VARCHAR(50),
    amount DECIMAL(15, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    payment_date DATE,
    reference_number VARCHAR(100),
    status VARCHAR(50) DEFAULT 'pending',
    confirmed_by INTEGER REFERENCES users(id),
    confirmed_at TIMESTAMP,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- 9. STOCK LOCKS
-- ============================================

CREATE TABLE stock_locks (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id),
    warehouse_code VARCHAR(50),
    quantity INTEGER NOT NULL,
    locked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    locked_by INTEGER REFERENCES users(id),
    released_at TIMESTAMP,
    status VARCHAR(50) DEFAULT 'locked'
);

-- ============================================
-- SEED DATA
-- ============================================

-- Insert default roles
INSERT INTO roles (name, description) VALUES
    ('super_admin', 'Super Administrator with full system access'),
    ('admin', 'Administrator with management access'),
    ('sales', 'Sales representative'),
    ('client', 'Client user with limited access');
