import os
import random
from matplotlib import category
import psycopg2
import pandas as pd
from dotenv import load_dotenv

"""Script to seed the fashion_system table with 300k items from a parquet file. 
(Retrieves data from matched_fashion_dataset_300k_rows.parquet and inserts into PostgreSQL database)"""

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

def scan_image_directory():
    """Scan fashion_images directory and return a list of image paths with their categories."""
    image_map = {}

    if not os.path.exists(IMAGE_DIR):
        print(f"Image directory not found at {IMAGE_DIR}. Please check the path.")
        return image_map
    
    print(f"Scanning image directory at {IMAGE_DIR}...")

    # Wwalk through all subdirectories and collect image paths
    for category_folder in os.listdir(IMAGE_DIR):
        category_path = os.path.join(IMAGE_DIR, category_folder)
        if not os.path.isdir(category_path):
            continue  # Skip files, we only want directories

        # Find all .jpg files in the category folder
        jpg_files = sorted([f for f in os.listdir(category_path) if f.lower().endswith('.jpg')])

        if jpg_files:
            image_map[category_folder] = jpg_files
            print(f"{category_folder}: {len(jpg_files)} images found")

    total_images = sum(len(files) for files in image_map.values())
    print(f"Total images found: {total_images}")
    return image_map

def seed_database_from_parquet():
    """Load 300k rows directly from parquet file"""
    creds = get_connection_db()
    parquet_path = os.path.join(BASE_DIR, "MLOps", "database", "data", "raw", "matched_fashion_dataset_300k_rows.parquet")
    
    # Scan available images
    image_map = scan_image_directory()
    if not image_map:
        raise ValueError("No images found in the specified directory. Please ensure the dataset is correctly placed.")
    
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
        
    inserts = 0
    print(f"Schema initialized.\n")
    print(f"Inserting {len(df)} items into the database...")

    for idx, row in df.iterrows():
        item_id = f"item_{idx+1:06d}"

        # Get category from parquet, fallback to random choice
        if 'category' in row.index and not pd.isna(row['category']):
            item_category = row['category']
        else:
            item_category = random.choice(list(image_map.keys()))


        # If category not in image_map, find closet match or use random category
        if item_category not in image_map:
            matching_categories = [cat for cat in image_map.keys() if item_category in cat.lower()]
            if matching_categories:
                item_category = random.choice(matching_categories)
            else:
                item_category = random.choice(list(image_map.keys()))

        # Get actual image from the category folder
        available_images = image_map[item_category]
        image_filename = random.choice(available_images)
        image_path = f"{item_category}/{image_filename}"

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
                print(f"Progress: {inserts}/{len(df)} items inserted...")   

        except Exception as e:
            print(f"Error inserting row {idx+1}: {e}")
            conn.rollback()  # Rollback on error to maintain data integrity
            continue  # Skip to next row

        # Apply item limit if set
        if ITEM_LIMIT and inserts >= ITEM_LIMIT:
            break

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
