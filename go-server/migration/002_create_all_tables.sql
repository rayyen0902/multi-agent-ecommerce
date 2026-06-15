-- 002_create_products.sql
CREATE TABLE IF NOT EXISTS products (
    id BIGSERIAL PRIMARY KEY,
    shop_id BIGINT NOT NULL REFERENCES shops(id),
    platform_product_id VARCHAR(100),
    platform_sku_id VARCHAR(100),
    name VARCHAR(255),
    sku_name VARCHAR(255),
    price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    stock INT DEFAULT 0,
    stock_warning_threshold INT DEFAULT 10,
    image_url VARCHAR(500),
    status SMALLINT DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_products_shop_id ON products(shop_id);
CREATE INDEX IF NOT EXISTS idx_products_status ON products(status);
CREATE INDEX IF NOT EXISTS idx_products_stock_alert ON products(stock, stock_warning_threshold) WHERE status = 1;

-- 003_create_orders.sql
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    order_no VARCHAR(64) NOT NULL UNIQUE,
    platform_order_no VARCHAR(100),
    shop_id BIGINT NOT NULL REFERENCES shops(id),
    platform VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    buyer_name VARCHAR(100),
    buyer_message TEXT,
    seller_remark TEXT,
    receiver_name VARCHAR(50),
    receiver_phone VARCHAR(255),
    receiver_province VARCHAR(20),
    receiver_city VARCHAR(20),
    receiver_district VARCHAR(20),
    receiver_address VARCHAR(512),
    total_amount DECIMAL(10,2),
    discount_amount DECIMAL(10,2) DEFAULT 0,
    shipping_fee DECIMAL(10,2) DEFAULT 0,
    pay_amount DECIMAL(10,2),
    payment_method VARCHAR(20),
    platform_created_at TIMESTAMPTZ,
    platform_paid_at TIMESTAMPTZ,
    shipped_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    synced_at TIMESTAMPTZ,
    raw_data JSONB,
    tags VARCHAR(255)[],
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_orders_shop_status ON orders(shop_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_platform_order_no ON orders(platform_order_no);
CREATE INDEX IF NOT EXISTS idx_orders_platform_created_at ON orders(platform_created_at);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);

CREATE TABLE IF NOT EXISTS order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    platform_item_id VARCHAR(100),
    product_id BIGINT REFERENCES products(id),
    product_name VARCHAR(255),
    sku_name VARCHAR(255),
    price DECIMAL(10,2),
    quantity INT,
    total_price DECIMAL(10,2),
    image_url VARCHAR(500)
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);

-- 004_create_logistics.sql
CREATE TABLE IF NOT EXISTS logistics (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE REFERENCES orders(id),
    shipping_company VARCHAR(50),
    shipping_company_code VARCHAR(20),
    tracking_no VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    latest_info TEXT,
    traces JSONB,
    shipped_at TIMESTAMPTZ,
    delivered_at TIMESTAMPTZ,
    last_tracked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_logistics_tracking_no ON logistics(tracking_no);
CREATE INDEX IF NOT EXISTS idx_logistics_status ON logistics(status);

-- 005_create_rules.sql
CREATE TABLE IF NOT EXISTS rules (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(30) NOT NULL,
    shop_id BIGINT REFERENCES shops(id),
    platform VARCHAR(20),
    conditions JSONB,
    actions JSONB,
    priority INT DEFAULT 100,
    enabled BOOLEAN DEFAULT FALSE,
    last_triggered_at TIMESTAMPTZ,
    trigger_count BIGINT DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_rules_type ON rules(type);
CREATE INDEX IF NOT EXISTS idx_rules_enabled ON rules(enabled);

CREATE TABLE IF NOT EXISTS automation_logs (
    id BIGSERIAL PRIMARY KEY,
    rule_id BIGINT NOT NULL REFERENCES rules(id),
    order_id BIGINT REFERENCES orders(id),
    action_type VARCHAR(30),
    status VARCHAR(20),
    detail JSONB,
    error_message TEXT,
    executed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_automation_logs_rule_id ON automation_logs(rule_id);
CREATE INDEX IF NOT EXISTS idx_automation_logs_order_id ON automation_logs(order_id);

-- 006_create_users.sql
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    nickname VARCHAR(50),
    email VARCHAR(100),
    role VARCHAR(20) DEFAULT 'admin',
    status SMALLINT DEFAULT 1,
    last_login TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    deleted_at TIMESTAMPTZ
);

-- 默认管理员账号 (密码: admin123, bcrypt加密)
INSERT INTO users (username, password, nickname, role, status)
VALUES ('admin', '$2a$10$N9qo8uLOickgx2ZMRZoMyeIjZAgcfl7p92ldGxad68LJZdL17lhWy', '系统管理员', 'admin', 1)
ON CONFLICT (username) DO NOTHING;
