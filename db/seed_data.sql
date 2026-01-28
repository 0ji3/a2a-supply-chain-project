-- A2A Supply Chain Optimization - Seed Data (MVP)
-- テストデータ: 1店舗、トマト1商品

-- 店舗データ
INSERT INTO stores (store_id, store_name, latitude, longitude) VALUES
('S001', '本店（渋谷）', 35.661777, 139.704051)
ON CONFLICT (store_id) DO NOTHING;

-- 商品データ
INSERT INTO products (product_sku, product_name, category, shelf_life_days) VALUES
('tomato-medium-domestic', 'トマト（中玉・国産）', '生鮮野菜', 3)
ON CONFLICT (product_sku) DO NOTHING;

-- サプライヤーデータ
INSERT INTO suppliers (supplier_id, supplier_name, unit_price, lead_time_hours, quality_score) VALUES
('SUP001', '静岡農協', 120.00, 8, 0.95),
('SUP002', '熊本直送便', 115.00, 12, 0.88),
('SUP003', '北海道ファーム', 130.00, 24, 0.92)
ON CONFLICT (supplier_id) DO NOTHING;

-- POS販売データ（過去30日分のサンプル）
-- 曜日パターン: 0=月, 1=火, 2=水, 3=木, 4=金, 5=土, 6=日
-- 平日: 300-400個、週末: 450-550個

DO $$
DECLARE
    v_date DATE;
    v_day_of_week INTEGER;
    v_is_holiday BOOLEAN;
    v_quantity INTEGER;
    v_price DECIMAL(10, 2);
BEGIN
    -- 30日前から昨日まで
    FOR i IN 1..30 LOOP
        v_date := CURRENT_DATE - i;
        v_day_of_week := EXTRACT(DOW FROM v_date); -- 0=日, 1=月, ...
        v_is_holiday := (v_day_of_week IN (0, 6)); -- 土日

        -- 数量: 週末は多め、平日は少なめ
        IF v_is_holiday THEN
            v_quantity := 450 + (RANDOM() * 100)::INTEGER;
        ELSE
            v_quantity := 300 + (RANDOM() * 100)::INTEGER;
        END IF;

        -- 価格: 198円で固定（MVPなので変動なし）
        v_price := 198.00;

        -- データ挿入
        INSERT INTO pos_sales (
            date,
            store_id,
            product_sku,
            sales_quantity,
            price,
            day_of_week,
            is_holiday
        ) VALUES (
            v_date,
            'S001',
            'tomato-medium-domestic',
            v_quantity,
            v_price,
            v_day_of_week,
            v_is_holiday
        )
        ON CONFLICT DO NOTHING;
    END LOOP;
END $$;
