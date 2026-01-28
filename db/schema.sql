-- A2A Supply Chain Optimization - Database Schema (MVP)
-- PostgreSQL 15+

-- 店舗マスタ
CREATE TABLE IF NOT EXISTS stores (
    store_id VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(200) NOT NULL,
    latitude DECIMAL(9, 6) NOT NULL,
    longitude DECIMAL(9, 6) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 商品マスタ
CREATE TABLE IF NOT EXISTS products (
    product_sku VARCHAR(100) PRIMARY KEY,
    product_name VARCHAR(200) NOT NULL,
    category VARCHAR(100) NOT NULL,
    shelf_life_days INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- サプライヤーマスタ
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id VARCHAR(50) PRIMARY KEY,
    supplier_name VARCHAR(200) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    lead_time_hours INTEGER NOT NULL,
    quality_score DECIMAL(3, 2) DEFAULT 0.85,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- POS販売データ
CREATE TABLE IF NOT EXISTS pos_sales (
    id BIGSERIAL PRIMARY KEY,
    date DATE NOT NULL,
    store_id VARCHAR(50) NOT NULL REFERENCES stores(store_id),
    product_sku VARCHAR(100) NOT NULL REFERENCES products(product_sku),
    sales_quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_holiday BOOLEAN NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- インデックス
CREATE INDEX IF NOT EXISTS idx_pos_sales_product_store_date
    ON pos_sales(product_sku, store_id, date DESC);

CREATE INDEX IF NOT EXISTS idx_pos_sales_date
    ON pos_sales(date DESC);

-- Phase 2以降で追加予定
-- CREATE TABLE agent_executions (...);
-- CREATE TABLE optimization_tasks (...);
