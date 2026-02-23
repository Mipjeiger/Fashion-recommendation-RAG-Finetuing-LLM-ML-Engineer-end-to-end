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