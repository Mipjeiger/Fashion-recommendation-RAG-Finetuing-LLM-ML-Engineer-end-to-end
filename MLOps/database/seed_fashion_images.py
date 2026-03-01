import os
import random
import psycopg2
from dotenv import load_dotenv

# Path mapping for configuration and data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ENV_PATH = os.path.join(BASE_DIR, "website", ".env")
IMAGE_DIR = os.path.join(BASE_DIR, "fashion_images", "dataset_clean")
SQL_FILE = os.path.join(BASE_DIR, "MLOps", "database", "fashion_system.sql")

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

def seed_database():
    creds = get_connection_db()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not found in website/.env")
        return
    
    limit = 250000 # Limit to 250k items for testing
    
    print(f"Connecting to database {creds['dbname']} at {creds['host']}...")
    try:
        conn = psycopg2.connect(**creds)
        cur = conn.cursor()
        
        # 1. Initialize the schema
        print(f"Loading schema from {SQL_FILE}")
        with open(SQL_FILE, 'r') as f:
            schema_sql = f.read()
            cur.execute(schema_sql)
            conn.commit()
            
        # 2. Parse images and insert into table
        brands = ["IndoCloth", "StyleGen", "UrbanWear", "ClassicFit"]
        seasons = ["Summer", "Winter", "Spring", "Fall"]
        
        item_counter = 1
        inserts = 0
        
        print(f"Scanning images in {IMAGE_DIR}...")

        for category in sorted(os.listdir(IMAGE_DIR)):
            if inserts >= limit: break # Stop if we've reached the limit

            cat_path = os.path.join(IMAGE_DIR, category)
            if os.path.isdir(cat_path):
                for img in sorted(os.listdir(cat_path)):
                    if inserts >= limit: break

                    if img.endswith('.jpg'):
                        item_id = f"item_{item_counter:04d}"
                        brand = random.choice(brands)
                        season = random.choice(seasons)
                        price = random.randint(15, 150)
                        image_path = f"{category}/{img}"
                        view_count = random.randint(10, 500)
                        purchase_count = random.randint(0, 50)
                        stocks = random.randint(10, 100)
                        
                        cur.execute("""
                            INSERT INTO fashion_system 
                            (item_id, category, brand, season, price, image_path, view_count, purchase_count, stocks) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (item_id, category, brand, season, price, image_path, view_count, purchase_count, stocks))
                        
                        item_counter += 1
                        inserts += 1

                        # Optimization: COmmit every 10,000 rows to reduce transaction overhead
                        if inserts % 10000 == 0:
                            conn.commit()
                            print(f"Progress: {inserts}/{limit} items inserted...")
                        
        conn.commit()
        print(f"Successfully seeded {inserts} fashion items into the database!")
        
    except Exception as e:
        print(f"Database error occurred: {e}")
        if 'conn' in locals(): conn.rollback() # Rollback on error
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    seed_database()
