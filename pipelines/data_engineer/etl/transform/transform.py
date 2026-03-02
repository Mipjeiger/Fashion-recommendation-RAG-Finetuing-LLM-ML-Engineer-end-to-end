import sys
from pathlib import Path

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = BASE_DIR / '.env'

# Add project root to Python path
sys.path.insert(0, str(BASE_DIR.parent))

import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

if not ENV_PATH.exists():
    print(f".env file not found at {ENV_PATH}")
    sys.exit(1)

load_dotenv(dotenv_path=str(ENV_PATH))

# Configure database connection parameters
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME]):
    print("Database credentials missing!")
    sys.exit(1)

print(f"✅ Loaded credentials from {ENV_PATH}")

def transform_data():
    try:
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df = pd.read_sql(text("SELECT * FROM loss_profit;"), connection)

        if df is None or df.empty:
            print("❌ No data loaded. Skipping transformation.")
            return

        print(f"✅ Loaded {len(df)} records from loss_profit table.")

        # Clean NULL values
        numeric_cols = ['price', 'stocks', 'purchase_count', 'view_count']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

        # Transform: calculate derived columns (OUTSIDE the loop!)
        df['sales'] = df['price'] * df['purchase_count']
        df['stock_value_retail'] = df['price'] * df['stocks']
        df['profit_status'] = df['sales'].apply(lambda x: 'profit' if x > 0 else 'loss')
        df['conversion_rate'] = np.where(df['view_count'] > 0, (df['purchase_count'] / df['view_count']) * 100, 0)

        print("\n✅ Transformed Data (sample):")
        print(df[['sales', 'profit_status', 'conversion_rate', 'stock_value_retail']].head(10))

        # Save to SQLite .db file
        db_path = BASE_DIR / 'data_engineer'  / 'database' / 'loss_profit_renew.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)

        sqlite_engine = create_engine(f"sqlite:///{db_path}")
        df.to_sql('loss_profit', con=sqlite_engine, if_exists='replace', index=False)
        print(f"\n✅ Successfully saved {len(df)} records to {db_path}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    transform_data()