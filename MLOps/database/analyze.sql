-- Active: 1771596228182@@127.0.0.1@5432@airflow
SELECT * FROM fashion;
SELECT * FROM market_sentiment;

-- analyze the fashion each columns it has
SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'fashion';

-- Inner JOIN (fashion + market_sentiment table dataset)
SELECT
    f.item_id,
    f.category,
    f.brand,
    f.price,
    m.view_count,
    m.click_count,
    m.purchase_count
FROM fashion f
INNER JOIN market_sentiment m ON f.item_id = m.item_id;

-- LEFT JOIN (fashion as base data + market_sentiment as additional data)
SELECT
    f.item_id,
    f.category,
    f.brand,
    f.price,
    f.view_count,
    f.click_count,
    f.purchase_count
FROM fashion f
LEFT JOIN market_sentiment m ON f.item_id = m.item_id;

-- Total revenue by category
SELECT
    f.category,
    COUNT(DISTINCT f.item_id) as total_items,
    SUM(f.purchase_count) as total_purchases,
    SUM(f.price * m.purchase_count) as total_revenue,
    ROUND(AVG(f.price), 2) as avg_price,
    ROUND(SUM(f.price * m.purchase_count) / NULLIF(SUM(m.purchase_count), 0), 2) as revenue_per_purchase
FROM fashion f
LEFT JOIN market_sentiment m ON f.item_id = m.item_id
GROUP BY f.category
ORDER BY total_revenue DESC;

-- Customer Engagement Analysis
-- Engagement funnel: views -> clicks -> purchases
SELECT
    f.subcategory,
    SUM(f.view_count) as total_views,
    SUM(f.click_count) as total_clicks,
    SUM(f.purchase_count) as total_purchases,
    ROUND(100.0 * SUM(f.click_count) / NULLIF(SUM(f.view_count), 0), 2) as click_through_rate,
    ROUND(100.0 * SUM(f.purchase_count) / NULLIF(SUM(f.click_count), 0), 2) as conversion_rate,
    ROUND(100.0 * SUM(f.purchase_count) / NULLIF(SUM(f.view_count), 0), 2) as overall_conversion
FROM fashion f
LEFT JOIN market_sentiment m ON f.item_id = m.item_id
GROUP BY f.subcategory
ORDER BY overall_conversion DESC;