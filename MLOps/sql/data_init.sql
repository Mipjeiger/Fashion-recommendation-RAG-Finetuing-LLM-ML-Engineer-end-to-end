-- Active: 1770487880142@@127.0.0.1@5432
-- Active: 1770487880142@@127.0.0.1@5432.0.0.1@5432.0.0.1@5432.0.0.1@5432.0.0.1@5432
-- Create data_registry table
CREATE TABLE IF NOT EXISTS data_registry (
    item_id SERIAL PRIMARY KEY,
    dataset_name TEXT,
    dataset_version TEXT,
    path TEXT,
    row_count BIGINT,
    schema_hash TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Validate the table creation
SELECT * FROM data_registry;

CREATE TABLE IF NOT EXISTS market_sentiment (
    item_id SERIAL PRIMARY KEY,
    view_count INT NOT NULL,
    click_count INT NOT NULL,
    purchase_count INT NOT NULL
);

-- Validate the table creation
SELECT * FROM market_sentiment;

-- Create Churn_prediction table
CREATE TABLE IF NOT EXISTS churn_prediction (
    item_id SERIAL PRIMARY KEY,
    view_count INT NOT NULL,
    purchase_count INT NOT NULL,
    stocks INT NOT NULL
);
-- Validate the table creation
SELECT * FROM churn_prediction;

-- Create loss & profit table
CREATE TABLE IF NOT EXISTS loss_profit (
    item_id SERIAL PRIMARY KEY,
    purchase_count INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stocks INT NOT NULL
);
-- Validate the table creation
SELECT * FROM loss_profit;

-- create cost table
CREATE TABLE IF NOT EXISTS cost (
    item_id SERIAL PRIMARY KEY,
    price DECIMAL(10, 2) NOT NULL,
    stocks INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    fabric VARCHAR(50) NOT NULL
);
-- validate the table creation
SELECT * FROM cost;