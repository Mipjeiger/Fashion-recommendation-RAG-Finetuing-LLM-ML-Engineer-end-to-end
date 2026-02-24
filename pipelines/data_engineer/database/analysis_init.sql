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

