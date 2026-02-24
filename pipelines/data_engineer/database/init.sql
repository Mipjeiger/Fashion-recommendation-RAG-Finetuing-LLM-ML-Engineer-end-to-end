-- Active: 1771162575354@@localhost@5432@airflow
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

CREATE TABLE IF NOT EXISTS market_sentiment (
    item_id TEXT PRIMARY KEY,
    view_count INT NOT NULL,
    click_count INT NOT NULL,
    purchase_count INT NOT NULL
);

-- Validate the table creation
SELECT * FROM market_sentiment;

-- Create Churn_prediction table
CREATE TABLE IF NOT EXISTS churn_prediction (
    item_id TEXT PRIMARY KEY,
    view_count INT NOT NULL,
    purchase_count INT NOT NULL,
    stocks INT NOT NULL
);
-- Validate the table creation
SELECT * FROM churn_prediction;

-- Create loss & profit table
CREATE TABLE IF NOT EXISTS loss_profit (
    item_id TEXT PRIMARY KEY,
    purchase_count INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stocks INT NOT NULL
);
-- Validate the table creation
SELECT * FROM loss_profit;