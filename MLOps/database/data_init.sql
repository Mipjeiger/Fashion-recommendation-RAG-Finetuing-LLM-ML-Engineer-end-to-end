-- Active: 1771296061150@@127.0.0.1@5432@airflow
-- Active: 1770487880142@@127.0.0.1@5432.0.0.1@5432.0.0.1@5432.0.0.1@5432.0.0.1@5432

-- AIRFLOW + SPARK ENVIRONMENT
-- Create data_registry table

CREATE TABLE IF NOT EXISTS data_registry (
    item_id TEXT PRIMARY KEY,
    dataset_name TEXT,
    dataset_version TEXT,
    path TEXT,
    row_count BIGINT,
    schema_hash TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Validate the table creation
SELECT * FROM data_registry;

SELECT * FROM data_registry WHERE dataset_name = 'market_sentiment';

-- Create pipeline_runs table
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id TEXT PRIMARY KEY,
    dag_id TEXT,
    status TEXT,
    started_at TIMESTAMP,
    finished_at TIMESTAMP
);
-- validate the table creation
SELECT * FROM pipeline_runs;

-- Fashion recommendation business metrics -  POSTGRESQL ENVIRONMENT

-- Create Fashion table
CREATE TABLE IF NOT EXISTS fashion (
    item_id TEXT PRIMARY KEY,
    category TEXT,
    subcategory TEXT,
    sleeve_type TEXT,
    season TEXT,
    fabric TEXT,
    occasion TEXT,
    formality_level TEXT,
    size_range TEXT,
    brand TEXT,
    view_count INT,
    click_count INT,
    purchase_count INT,
    length_cm INT,
    price BIGINT,
    stocks INT
);

-- Validate the table creation
SELECT * FROM fashion;

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

-- create cost table
CREATE TABLE IF NOT EXISTS cost (
    item_id TEXT PRIMARY KEY,
    price DECIMAL(10, 2) NOT NULL,
    stocks INT NOT NULL,
    category VARCHAR(50) NOT NULL,
    fabric VARCHAR(50) NOT NULL
);
-- validate the table creation
SELECT * FROM cost;