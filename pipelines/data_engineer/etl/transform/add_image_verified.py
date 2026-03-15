import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path
import os
import hashlib
import sys

print("=" * 80)
print("ADDING IMAGE_PATH COLUMN TO EXISTING DATABASE")
print("=" * 80)
print()

# Paths - FIX: Go up 4 levels to project root, not 3
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
DB_PATH = BASE_DIR / 'data_engineer' / 'database' / 'loss_profit_renew.db'
IMAGE_DIR = BASE_DIR / 'fashion_images' / 'dataset_clean'

print(f"📁 Project root: {BASE_DIR}")
print(f"📁 Database: {DB_PATH}")
print(f"📁 Images: {IMAGE_DIR}\n")

# Check files exist
if not DB_PATH.exists():
    print(f"❌ Database not found at {DB_PATH}")
    print(f"   Expected: {DB_PATH}")
    sys.exit(1)

if not IMAGE_DIR.exists():
    print(f"❌ Image directory not found at {IMAGE_DIR}")
    print(f"   Expected: {IMAGE_DIR}")
    
    # Try to find the correct path
    print(f"\n🔍 Searching for fashion_images/dataset_clean...\n")
    for path in BASE_DIR.rglob('dataset_clean'):
        if path.is_dir():
            print(f"   Found at: {path}")
            IMAGE_DIR = path
            break
    
    if not IMAGE_DIR.exists():
        print("❌ Still not found!")
        sys.exit(1)

print("✅ Files verified\n")

# Step 1: Scan all images
print("=" * 80)
print("STEP 1: SCANNING IMAGES")
print("=" * 80)
all_images = []
category_count = {}

for category_folder in sorted(os.listdir(IMAGE_DIR)):
    category_path = IMAGE_DIR / category_folder
    
    if not category_path.is_dir():
        continue
    
    jpg_files = sorted([f for f in os.listdir(category_path) if f.lower().endswith('.jpg')])
    
    if jpg_files:
        for jpg in jpg_files:
            all_images.append(f"{category_folder}/{jpg}")
        
        category_count[category_folder] = len(jpg_files)
        print(f"  ✓ {category_folder}: {len(jpg_files)} images")

print(f"\n✅ Found {len(all_images):,} total images")
print(f"✅ Found {len(category_count)} categories\n")

if not all_images:
    print("❌ No images found!")
    sys.exit(1)

# Step 2: Load database
print("=" * 80)
print("STEP 2: LOADING DATABASE")
print("=" * 80)
engine = create_engine(f'sqlite:///{str(DB_PATH)}')
df = pd.read_sql_table('loss_profit', engine)

print(f"✅ Loaded {len(df):,} records")
print(f"📋 Columns before: {', '.join(df.columns)}\n")

# Step 3: Create image_path column with deterministic mapping
print("=" * 80)
print("STEP 3: CREATING IMAGE_PATH COLUMN")
print("=" * 80)

def get_deterministic_image(item_id, all_images):
    """Use deterministic hashing to assign consistent image to each item_id."""
    hash_value = int(hashlib.md5(str(item_id).encode()).hexdigest(), 16)
    image_index = hash_value % len(all_images)
    return all_images[image_index]

print(f"Mapping {len(df):,} rows to {len(all_images):,} images...")
df['image_path'] = df['item_id'].apply(lambda x: get_deterministic_image(x, all_images))

print(f"✅ Image paths created")
print(f"✅ NULL values: {df['image_path'].isna().sum()}")
print(f"✅ Unique images: {df['image_path'].nunique():,}\n")

# Step 4: Save back to database
print("=" * 80)
print("STEP 4: SAVING TO DATABASE")
print("=" * 80)
print("Overwriting loss_profit table...")
df.to_sql('loss_profit', engine, if_exists='replace', index=False)

print(f"✅ Saved {len(df):,} records")
print(f"📋 Columns after: {', '.join(df.columns)}\n")

# Step 5: Verify
print("=" * 80)
print("STEP 5: VERIFICATION")
print("=" * 80)
df_verify = pd.read_sql_table('loss_profit', engine)

if 'image_path' not in df_verify.columns:
    print("❌ FAILED: image_path column not found!")
    sys.exit(1)

null_count = df_verify['image_path'].isna().sum()
if null_count > 0:
    print(f"❌ FAILED: Found {null_count:,} NULL values")
    sys.exit(1)

print(f"✅ Database verified successfully")
print(f"✅ Records: {len(df_verify):,}")
print(f"✅ Columns: {len(df_verify.columns)}")
print(f"✅ image_path: Present with {df_verify['image_path'].nunique():,} unique images\n")

# Show sample
print("SAMPLE DATA:")
print("─" * 80)
sample_cols = ['item_id', 'price', 'sales', 'profit_status', 'image_path']
print(df_verify[sample_cols].head(10).to_string())

# Verify some actual images exist
print("\n" + "=" * 80)
print("STEP 6: IMAGE FILE VALIDATION")
print("=" * 80)
sample_paths = df_verify['image_path'].head(10).tolist()
found_count = 0

for img_path in sample_paths:
    full_path = IMAGE_DIR / img_path
    if full_path.exists():
        found_count += 1
        status = "✅"
    else:
        status = "❌"
    print(f"{status} {img_path}")

print()
if found_count == len(sample_paths):
    print(f"✅ All sampled images exist!")
else:
    print(f"⚠️  {found_count}/{len(sample_paths)} images found")

engine.dispose()

print("\n" + "=" * 80)
print("✨ IMAGE_PATH COLUMN SUCCESSFULLY ADDED!")
print("=" * 80)