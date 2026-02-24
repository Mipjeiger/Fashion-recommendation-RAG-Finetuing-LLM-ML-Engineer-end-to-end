import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# Database path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
db_path = BASE_DIR / 'database' / 'loss_profit.db'

# Load data base .db and check tables
engine = create_engine(f'sqlite:///{db_path}')

# Get all tables in the database
with engine.connect() as connection:
    result = connection.execute(text("SELECT name FROM sqlite_master WHERE type='table';"))
    tables = result.fetchall()
    print(f"Database: {db_path.name}")
    print("\nTables in the database:")
    for table in tables:
        print(f" - {table[0]}")
    print()


# Load data from the database into a DataFrame
if tables:
    for table_name in tables:
        table = table_name[0]
        print(f"Table: {table}")
        with engine.connect() as connection:
            query = text(f"SELECT * FROM {table};")
            df = pd.read_sql(query, connection)
            print(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nData:\n{df}")

else:
    print("No tables found in the database.")