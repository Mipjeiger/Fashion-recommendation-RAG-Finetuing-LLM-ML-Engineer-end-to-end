-- Active: 1771162575354@@localhost@5432
-- SQL Schema for fashion images integration
DROP TABLE IF EXISTS fashion_system;

CREATE TABLE fashion_system (
    item_id TEXT PRIMARY KEY,
    category TEXT,
    brand TEXT,
    season TEXT,
    price BIGINT,
    image_path TEXT,
    view_count INT,
    purchase_count INT,
    stocks INT
);

SELECT * FROM fashion_system;

-- validate kafka into database postgres
SELECT * FROM fashion_system WHERE item_id = 'TNC_000001';

-- Create ENUM type first
CREATE TYPE profit_status_enum AS ENUM ('profit', 'loss');

-- Create fashion_recommendation table with ENUM type
DROP TABLE IF EXISTS fashion_recommendation;
CREATE TABLE IF NOT EXISTS fashion_recommendation (
    id SERIAL PRIMARY KEY,
    item_id TEXT UNIQUE NOT NULL,
    purchase_count INTEGER NOT NULL DEFAULT 0,
    view_count INTEGER NOT NULL DEFAULT 0,
    price BIGINT NOT NULL,
    stocks INTEGER NOT NULL DEFAULT 0,
    sales BIGINT NOT NULL,
    profit_status TEXT NOT NULL,
    conversion_rate NUMERIC(10, 2) NOT NULL DEFAULT 0.00,
    image_path VARCHAR(500) NOT NULL
);

-- Create indexes for better query performance
CREATE INDEX idx_fashion_recommendation_item_id ON fashion_recommendation(item_id);
CREATE INDEX idx_fashion_recommendation_profit_status ON fashion_recommendation(profit_status);
CREATE INDEX idx_fashion_recommendation_image_path ON fashion_recommendation(image_path);

SELECT * FROM fashion_recommendation;