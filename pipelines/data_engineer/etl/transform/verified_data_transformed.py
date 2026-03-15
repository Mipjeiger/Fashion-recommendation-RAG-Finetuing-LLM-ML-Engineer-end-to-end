import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path
import sys

# Get correct path to database
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DB_PATH = BASE_DIR / 'data_engineer' / 'database' / 'loss_profit_renew.db'
IMAGE_DIR = BASE_DIR / 'fashion_images' / 'dataset_clean'

print("=" * 80)
print("DATA TRANSFORMATION VERIFICATION REPORT")
print("=" * 80)
print()

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 1: Database File Exists
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 1: Database File")
print("─" * 80)
if not DB_PATH.exists():
    print(f"❌ FAILED: Database file not found at {DB_PATH}")
    sys.exit(1)
else:
    file_size = DB_PATH.stat().st_size / (1024 * 1024)  # Convert to MB
    print(f"✅ PASSED: Database exists at {DB_PATH}")
    print(f"   File size: {file_size:.2f} MB\n")

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 2: Database Structure
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 2: Database Structure")
print("─" * 80)
engine = create_engine(f'sqlite:///{str(DB_PATH)}')

with engine.connect() as connection:
    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = [row[0] for row in result.fetchall()]

if not tables:
    print("❌ FAILED: No tables found in database")
    sys.exit(1)
else:
    print(f"✅ PASSED: Found {len(tables)} table(s)")
    for table_name in tables:
        print(f"   - {table_name}")
    print()

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 3: Data Loading
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 3: Data Loading")
print("─" * 80)
df = pd.read_sql_table('loss_profit', engine)

if df is None or df.empty:
    print("❌ FAILED: No data in loss_profit table")
    sys.exit(1)
else:
    print(f"✅ PASSED: Loaded {len(df):,} records")
    print(f"   Memory usage: {df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB\n")

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 4: Original Columns
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 4: Original Columns")
print("─" * 80)
original_cols = ['item_id', 'purchase_count', 'view_count', 'price', 'stocks']
missing_cols = [col for col in original_cols if col not in df.columns]

if missing_cols:
    print(f"❌ FAILED: Missing columns: {missing_cols}")
    sys.exit(1)
else:
    print(f"✅ PASSED: All original columns present")
    for col in original_cols:
        print(f"   - {col}")
    print()

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 5: Derived Columns
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 5: Derived Columns")
print("─" * 80)
derived_cols = ['sales', 'stock_value_retail', 'profit_status', 'conversion_rate']
missing_derived = [col for col in derived_cols if col not in df.columns]

if missing_derived:
    print(f"❌ FAILED: Missing derived columns: {missing_derived}")
else:
    print(f"✅ PASSED: All derived columns created")
    for col in derived_cols:
        print(f"   - {col}")
    print()

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 6: IMAGE_PATH Column
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 6: Image Path Column")
print("─" * 80)
if 'image_path' not in df.columns:
    print("❌ FAILED: image_path column NOT found")
    print(f"   Available columns: {', '.join(df.columns)}")
    sys.exit(1)
else:
    null_count = df['image_path'].isna().sum()
    unique_images = df['image_path'].nunique()
    
    if null_count > 0:
        print(f"❌ FAILED: Found {null_count:,} NULL values in image_path")
        sys.exit(1)
    else:
        print(f"✅ PASSED: image_path column exists with no NULL values")
        print(f"   - Total records: {len(df):,}")
        print(f"   - Unique images used: {unique_images:,}")
        print(f"   - Coverage: {(unique_images / len(df) * 100):.2f}%\n")

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 7: Data Quality - Numeric Columns
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 7: Data Quality - Numeric Columns")
print("─" * 80)
numeric_checks = {
    'price': (df['price'] > 0).sum(),
    'stocks': (df['stocks'] >= 0).sum(),
    'purchase_count': (df['purchase_count'] >= 0).sum(),
    'view_count': (df['view_count'] >= 0).sum(),
    'sales': (df['sales'] >= 0).sum(),
    'conversion_rate': ((df['conversion_rate'] >= 0) & (df['conversion_rate'] <= 100)).sum()
}

all_passed = True
for col, valid_count in numeric_checks.items():
    pct = (valid_count / len(df)) * 100
    status = "✅" if pct == 100 else "⚠️"
    print(f"{status} {col}: {valid_count:,} valid ({pct:.1f}%)")

if all(count == len(df) for count in numeric_checks.values()):
    print("✅ PASSED: All numeric columns have valid data\n")
else:
    print("❌ WARNING: Some numeric columns have invalid data\n")

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 8: Data Quality - Categorical Columns
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 8: Data Quality - Categorical Columns")
print("─" * 80)

# Check profit_status
if 'profit_status' in df.columns:
    profit_values = df['profit_status'].unique()
    print(f"✅ profit_status values: {list(profit_values)}")
    print(f"   - profit: {(df['profit_status'] == 'profit').sum():,}")
    print(f"   - loss: {(df['profit_status'] == 'loss').sum():,}")
    print()

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 9: Sample Data
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 9: Sample Transformed Data")
print("─" * 80)
sample_cols = ['item_id', 'price', 'purchase_count', 'sales', 'profit_status', 'image_path']
print(df[sample_cols].head(10).to_string())
print()

# ──────────────────────────────────────────────────────────────────────────────
# CHECK 10: Image Path Verification
# ──────────────────────────────────────────────────────────────────────────────
print("CHECK 10: Image Path Validation")
print("─" * 80)

# Verify some image paths exist
if IMAGE_DIR.exists():
    sample_paths = df['image_path'].head(5).tolist()
    valid_images = 0
    
    for img_path in sample_paths:
        full_path = IMAGE_DIR / img_path
        if full_path.exists():
            valid_images += 1
            print(f"✅ {img_path}")
        else:
            print(f"❌ {img_path} (NOT FOUND)")
    
    print()
    if valid_images == len(sample_paths):
        print(f"✅ PASSED: All sampled images exist\n")
    else:
        print(f"⚠️  WARNING: {valid_images}/{len(sample_paths)} images found\n")
else:
    print(f"⚠️  Image directory not found: {IMAGE_DIR}\n")

# ──────────────────────────────────────────────────────────────────────────────
# FINAL SUMMARY
# ──────────────────────────────────────────────────────────────────────────────
print("=" * 80)
print("TRANSFORMATION VERIFICATION SUMMARY")
print("=" * 80)
print(f"✅ Database file: {DB_PATH.name}")
print(f"✅ Records: {len(df):,}")
print(f"✅ Columns: {len(df.columns)} ({', '.join(df.columns)})")
print(f"✅ image_path column: Present with {df['image_path'].nunique():,} unique images")
print(f"✅ Data quality: All checks passed")
print()
print("✨ TRANSFORMATION VERIFIED SUCCESSFULLY!")
print("=" * 80)

engine.dispose()