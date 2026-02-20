import os
import random

base_dir = "/Users/miftahhadiyannoor/Documents/Fashion_Recommendation_Engineer/fashion_images/dataset_clean"
sql_file = "/Users/miftahhadiyannoor/Documents/Fashion_Recommendation_Engineer/MLOps/database/fashion_system.sql"

brands = ["IndoCloth", "StyleGen", "UrbanWear", "ClassicFit"]
seasons = ["Summer", "Winter", "Spring", "Fall"]

sql_statements = [
    "-- SQL Schema for fashion images integration",
    "DROP TABLE IF EXISTS fashion_system;",
    "CREATE TABLE fashion_system (",
    "    item_id TEXT PRIMARY KEY,",
    "    category TEXT,",
    "    brand TEXT,",
    "    season TEXT,",
    "    price BIGINT,",
    "    image_path TEXT,",
    "    view_count INT,",
    "    purchase_count INT,",
    "    stocks INT",
    ");",
    ""
]

inserts = []

item_counter = 1
for category in sorted(os.listdir(base_dir)):
    cat_path = os.path.join(base_dir, category)
    if os.path.isdir(cat_path):
        for img in sorted(os.listdir(cat_path)):
            if img.endswith('.jpg'):
                item_id = f"item_{item_counter:04d}"
                brand = random.choice(brands)
                season = random.choice(seasons)
                price = random.randint(15, 150)
                image_path = f"{category}/{img}"
                view_count = random.randint(10, 500)
                purchase_count = random.randint(0, 50)
                stocks = random.randint(10, 100)
                
                inserts.append(f"INSERT INTO fashion_system (item_id, category, brand, season, price, image_path, view_count, purchase_count, stocks) VALUES ('{item_id}', '{category}', '{brand}', '{season}', {price}, '{image_path}', {view_count}, {purchase_count}, {stocks});")
                item_counter += 1

sql_statements.extend(inserts)

with open(sql_file, "w") as f:
    f.write("\n".join(sql_statements))

print(f"Generated {len(inserts)} inserts in {sql_file}")
