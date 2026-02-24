import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

import os
import pandas as pd
from sqlalchemy import create_engine, text, types
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=str(dotenv_path))

# Configure database connection parameters
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

from pipelines.data_engineer.etl.load.load_data import load_data

# Transform data from loss_profit table into loss_proft.db
def transform_data():
    try:
        # Read from PostgreSQL
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        pg_engine = create_engine(connection_string)

        with pg_engine.connect() as connection:
            df = pd.read_sql(text("SELECT * FROM loss_profit;"), connection)
            print(f"Extracted {len(df)} records from loss_profit table")
            print(df.head())  # Print first 5 rows for verification 

        # Transform: calculate profit and loss per item
        df['total_revenue'] = df['price'] * df['purchase_count']
        df['stock_value'] = df['price'] * df['stocks']
        df['profit_status'] = df['total_revenue'].apply(lambda x: 'profit' if x > 0 else 'loss')

        print("\nTransformed Data:")
        print(df.head())

        # Save to SQLite .db file
        db_path = BASE_DIR / 'loss_profit.db'
        sqlite_engine = create_engine(f"sqlite:///{db_path}")
        df.to_sql('loss_profit', con=sqlite_engine, if_exists='replace', index=False)
        print(f"\nSuccessfully saved {len(df)} records to {db_path}")
    
    except Exception as e:
        print(f"Error during transformation: {e}")


if __name__ == "__main__":
    transform_data()