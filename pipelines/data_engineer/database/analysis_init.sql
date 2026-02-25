DROP TABLE IF EXISTS loss_profit;

-- Create loss & profit table
CREATE TABLE IF NOT EXISTS loss_profit (
    item_id TEXT PRIMARY KEY,
    purchase_count INT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stocks INT NOT NULL
);

-- revenue database
SELECT * FROM loss_profit;

-- sort by price in descending order
SELECT * FROM loss_profit
ORDER BY price DESC;

-- Get tall fashion items with price > 100
SELECT * FROM loss_profit
WHERE price > 100;

-- Get specific columns filterted by item_id
SELECT item_id, purchase_count, price, stocks
FROM loss_profit
WHERE item_id = 'item_0090';

SELECT * FROM fashion_system;




-- Market sentiment database
SELECT * FROM market_sentiment;


-- website traffic database
SELECT * FROM recommendation_logs;

SELECT * FROM drift_events;