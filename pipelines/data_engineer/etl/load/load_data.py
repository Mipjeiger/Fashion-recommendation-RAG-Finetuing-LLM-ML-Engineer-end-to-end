import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

import pandas as pd
import os
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

from pipelines.data_engineer.etl.extract.extract_income import extract_income

def load_data():
    dtype_map = {
        'item_id': types.Text(),
        'purchase_count': types.Integer(),
        'price': types.Numeric(10, 2),
        'stocks': types.Integer(),
    }

    try:
        df = extract_income()

        # Select only column names that match the dtype_map keys
        df_load = df[['item_id', 'purchase_count', 'price', 'stocks']].head(100000)

        print(f"Extracted rows: {len(df_load)}")
        print(df_load.head())  # Print first 5 rows for verification

        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            df_load.to_sql('loss_profit', con=connection, if_exists='append', index=False, dtype=dtype_map)
            connection.commit()
            print(f"Successfully loaded {len(df_load)} records into loss_profit table")

            # Verify the load by querying the table
            result = connection.execute(text("SELECT COUNT(*) FROM loss_profit;"))
            print(f"Total records in loss_profit after load: {result.scalar()}")

    except Exception as e:
        print(f"Error loading data: {e}")

if __name__ == "__main__":
    load_data()