import os
import random
from matplotlib import category
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Path mapping for configuration and data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
ENV_PATH = os.path.join(BASE_DIR, "website", ".env")
IMAGE_DIR = os.path.join(BASE_DIR, "fashion_images", "dataset_clean")
SQL_FILE = os.path.join(BASE_DIR, "MLOps", "database", "fashion_system.sql") # Output SQL file for schema creation

# Configuration - set item limit
ITEM_LIMIT = None

# Load environment variables
load_dotenv(ENV_PATH)

# --------- Database Seeding Script for Fashion Images --------

def get_connection_db():
    # Config postgresql connection
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
        raise ValueError("Database credentials are not fully set in the environment variables.")
    return {
        "user": DB_USER,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "port": DB_PORT,
        "dbname": DB_NAME
    }

def seed_database_from_parquet():
    """Load 300k rows directly from parquet file"""
    creds = get_connection_db()
    parquet_path = os.path.join(BASE_DIR, "MLOps", "database", "data", "raw", "matched_fashion_dataset_300k_rows.parquet")
    df = pd.read_parquet(parquet_path)
     
    print(f"Connecting to database {creds['dbname']} at {creds['host']}...")
    print(f"Loading parquet file from {parquet_path}...")
    print(f"Loaded {len(df)} rows from parquet file.\n")
    
    conn = psycopg2.connect(**creds)
    cur = conn.cursor()
    
    # 1. Initialize the schema
    print(f"Loading schema from {SQL_FILE}")
    with open(SQL_FILE, 'r') as f:
        schema_sql = f.read()
        cur.execute(schema_sql)
        conn.commit()
            
        # 2. Parse images and insert into table
        brands = ["ZARA", "Adidas", "Tommy Hilfiger", "Polo", "HnM", "Nike"]
        seasons = ["all-season", "summer", "winter"]
        category_options = ["tops", "bottoms"]
        
        inserts = 0

        print(f"Schema initialized.\n")
        print(f"Inserting {len(df)} items into the database...")

        for idx, row in df.iterrows():
            item_id = f"item_{idx+1:06d}"

            # Get category from parquet, fallback to random choice
            if 'category' in row.index and not pd.isna(row['category']):
                item_category = row['category']
            else:
                item_category = random.choice(category_options)

            # Get brand from parquet, fallback to random choice  
            if 'brand' in row.index and not pd.isna(row['brand']):
                brand = str(row['brand'])
            else:
                brand = random.choice(brands)

            # Get season from parquet, fallback to random choice
            if 'season' in row.index and not pd.isna(row['season']):
                season = str(row['season'])
            else:
                season = random.choice(seasons)

            # Get other fields with fallbacks
            price = float(row.get('price', random.randint(15, 150))) if 'price' in row.index else random.randint(15, 150)
            image_path = str(row.get('image_path', f"{item_category}/image_{idx+1}.jpg")) if 'image_path' in row.index else f"{item_category}/image_{idx+1}.jpg"
            view_count = int(row.get('view_count', random.randint(10, 500))) if 'view_count' in row.index else random.randint(10, 500)
            purchase_count = int(row.get('purchase_count', random.randint(0, 50))) if 'purchase_count' in row.index else random.randint(0, 50)
            stocks = int(row.get('stocks', random.randint(0, 100))) if 'stocks' in row.index else random.randint(0, 100)
            
            # Insert into database
            try:
                cur.execute("""
                    INSERT INTO fashion_system 
                    (item_id, category, brand, season, price, image_path, view_count, purchase_count, stocks) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (item_id, item_category, brand, season, price, image_path, view_count, purchase_count, stocks))
                
                inserts += 1

                # Optimization: COmmit every 10,000 rows to reduce transaction overhead (Chunking)
                if inserts % 10000 == 0:
                    conn.commit()
                    print(f"Progress: {inserts} items inserted...")   

            except Exception as e:
                print(f"Error inserting row {idx+1}: {e}")
                conn.rollback()  # Rollback on error to maintain data integrity
                continue  # Skip to next row

            # Final commit after all insertions                
            conn.commit()
            print(f"Successfully seeded {inserts} fashion items into the database!")

# Close database connection
    cur.close()
    conn.close()
    print("Database connection closed.")

# Usage
if __name__ == "__main__":
    seed_database_from_parquet()
