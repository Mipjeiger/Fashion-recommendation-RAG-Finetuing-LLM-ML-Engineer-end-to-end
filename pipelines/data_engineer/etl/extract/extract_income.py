import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file and create base_dir
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
dotenv_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=str(dotenv_path))

# Configure database connection parameters
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

# Validate required credentials
required_vars = ['DB_USER', 'DB_PASSWORD', 'DB_HOST', 'DB_PORT', 'DB_NAME']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# extract database from sql server
def extract_income():
    try:
        connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        engine = create_engine(connection_string)
        with engine.connect() as connection:
            query = text("SELECT * FROM fashion_system;")
            df = pd.read_sql(query, connection)
        return df
    except Exception as e:
        raise Exception(f"Error extracting data: {e}")


if __name__ == "__main__":
    try:
        print("Extracting data from fashion_system...")
        df = extract_income()
        print(f"Successfully extracted {len(df)} records")
        print(df)  # Print first 10 rows for verification
    except Exception as e:
        print(f"Error: {e}")