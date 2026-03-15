import sys
import os
from pathlib import Path

# Get correct paths FIRST
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
ENV_PATH = BASE_DIR / '.env'

# Add to path
sys.path.insert(0, str(BASE_DIR))

import pandas as pd
import numpy as np
import hashlib
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

print(f"📁 BASE_DIR: {BASE_DIR}")
print(f"📄 ENV_PATH: {ENV_PATH}")
print(f"✅ ENV exists: {ENV_PATH.exists()}\n")

if not ENV_PATH.exists():
    print(f"❌ .env file not found at {ENV_PATH}")
    sys.exit(1)

# Load environment
load_dotenv(dotenv_path=str(ENV_PATH))

DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    print("❌ Database credentials missing!")
    print(f"DB_USER: {DB_USER}")
    print(f"DB_PASSWORD: {DB_PASSWORD}")
    print(f"DB_HOST: {DB_HOST}")
    print(f"DB_PORT: {DB_PORT}")
    print(f"DB_NAME: {DB_NAME}")
    sys.exit(1)

print(f"✅ Loaded credentials from {ENV_PATH}\n")

def get_available_images():
    """Scan fashion_images/dataset_clean and return flat list of all jpg images."""
    image_dir = BASE_DIR / 'fashion_images' / 'dataset_clean'
    all_images = []
    category_map = {}

    print(f"🔍 Scanning for images at: {image_dir}")
    print(f"✅ Image dir exists: {image_dir.exists()}\n")
    
    if not image_dir.exists():
        print(f"❌ Image directory not found!")
        return all_images, category_map
    
    # Walk through all category folders
    for category_folder in sorted(os.listdir(image_dir)):
        category_path = image_dir / category_folder
        
        if not category_path.is_dir():
            continue

        # Find all .jpg files
        jpg_files = sorted([f for f in os.listdir(category_path) if f.lower().endswith('.jpg')])
        
        if jpg_files:
            category_map[category_folder] = jpg_files
            
            # Add to flat list with category prefix
            for jpg in jpg_files:
                all_images.append(f"{category_folder}/{jpg}")
            
            print(f"  ✓ {category_folder}: {len(jpg_files)} images")

    total_images = len(all_images)
    print(f"\n✅ Found {total_images} images across {len(category_map)} categories\n")
    
    return all_images, category_map

def transform_data():
    """Transform data and add image_path column."""
    try:
        # Step 1: Get images
        print("=" * 70)
        print("STEP 1: SCANNING IMAGES")
        print("=" * 70)
        all_images, category_map = get_available_images()
        
        if not all_images:
            print("❌ No images found. Exiting.")
            return
        
        # Step 2: Connect to PostgreSQL
        print("=" * 70)
        print("STEP 2: LOADING DATA FROM POSTGRESQL")
        print("=" * 70)
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        print(f"Connecting to: {DB_HOST}:{DB_PORT}/{DB_NAME}")
        
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df = pd.read_sql(text("SELECT * FROM loss_profit;"), connection)

        if df is None or df.empty:
            print("❌ No data loaded from PostgreSQL.")
            return

        print(f"✅ Loaded {len(df):,} records from PostgreSQL\n")

        # Step 3: Clean numeric columns
        print("=" * 70)
        print("STEP 3: CLEANING DATA")
        print("=" * 70)
        numeric_cols = ['price', 'stocks', 'purchase_count', 'view_count']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
        print("✅ Cleaned numeric columns\n")

        # Step 4: Create derived columns
        print("=" * 70)
        print("STEP 4: CREATING DERIVED COLUMNS")
        print("=" * 70)
        df['sales'] = df['price'] * df['purchase_count']
        df['stock_value_retail'] = df['price'] * df['stocks']
        df['profit_status'] = df['sales'].apply(lambda x: 'profit' if x > 0 else 'loss')
        df['conversion_rate'] = np.where(df['view_count'] > 0, (df['purchase_count'] / df['view_count']) * 100, 0)
        print("✅ Created derived columns\n")

        # Step 5: Add image_path column
        print("=" * 70)
        print("STEP 5: ADDING IMAGE_PATH COLUMN")
        print("=" * 70)
        print(f"📊 Mapping {len(df):,} rows to {len(all_images):,} images...\n")

        def get_deterministic_image(item_id, all_images):
            """Use deterministic hashing to assign consistent image to each item_id."""
            hash_value = int(hashlib.md5(str(item_id).encode()).hexdigest(), 16)
            image_index = hash_value % len(all_images)
            return all_images[image_index]
        
        # Apply image assignment
        df['image_path'] = df['item_id'].apply(lambda x: get_deterministic_image(x, all_images))
        
        print(f"✅ Assigned image paths to {df['image_path'].notna().sum():,} records.\n")

        # Step 6: Statistics
        print("=" * 70)
        print("STEP 6: IMAGE DISTRIBUTION STATISTICS")
        print("=" * 70)
        image_usage = df['image_path'].value_counts()
        print(f"  - Unique images used: {len(image_usage):,}")
        print(f"  - Avg rows per image: {len(df) / len(image_usage):.1f}")
        print(f"  - Min rows per image: {image_usage.min()}")
        print(f"  - Max rows per image: {image_usage.max()}\n")

        print("Sample transformed data:")
        print(df[['item_id', 'sales', 'profit_status', 'image_path']].head(10))
        print()

        # Step 7: Save to SQLite
        print("=" * 70)
        print("STEP 7: SAVING TO SQLITE")
        print("=" * 70)
        db_path = BASE_DIR / 'data_engineer' / 'database' / 'loss_profit_renew.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)

        print(f"Saving to: {db_path}")
        sqlite_engine = create_engine(f"sqlite:///{db_path}")
        df.to_sql('loss_profit', con=sqlite_engine, if_exists='replace', index=False)
        
        print(f"✅ Successfully saved {len(df):,} records")
        print(f"📋 Columns: {', '.join(df.columns)}\n")

        # Step 8: Verify
        print("=" * 70)
        print("STEP 8: VERIFICATION")
        print("=" * 70)
        df_verify = pd.read_sql_table('loss_profit', sqlite_engine)
        print(f"✅ Verified {len(df_verify):,} records in SQLite")
        print(f"✅ image_path column exists: {'image_path' in df_verify.columns}")
        
        if 'image_path' in df_verify.columns:
            print(f"\n✅ Sample image paths:")
            print(df_verify[['item_id', 'image_path']].head(10))
        
        sqlite_engine.dispose()
        print("\n" + "=" * 70)
        print("✅ TRANSFORMATION COMPLETE!")
        print("=" * 70)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    transform_data()