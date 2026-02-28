import sqlite3
import pandas as pd
from pathlib import Path

# 1. Get the directory where the script lives
# pipelines/data_engineer/etl/extract/
CURRENT_DIR = Path(__file__).resolve().parent 

# 2. Go up to 'data_engineer' folder (2 levels up from 'extract')
# Go from 'extract' -> 'etl' -> 'data_engineer'
BASE_DIR = CURRENT_DIR.parents[1] 

# 3. Define the path to the DB
DB_PATH = BASE_DIR / "database" / "loss_profit.db"

print(f"Checking path: {DB_PATH}")

if not DB_PATH.exists():
    print("❌ File still not found! Check if the 'database' folder name is correct.")
else:
    print("✅ Database found. Connecting...")
    connection = sqlite3.connect(str(DB_PATH))
    # ... rest of your code ...
cursor = connection.cursor()

# Execute a query to fetch all data from the loss_profit table
query = "SELECT * FROM loss_profit"

try:
    cursor.execute(query)

    rows = cursor.fetchall()
    for row in rows:
        print(row)

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

df = pd.read_sql_query("SELECT * FROM loss_profit", connection)
df.to_csv("loss_profit_export.csv", index=False)
print("Data exported to loss_profit_export.csv")
print(df.head())

# Close the database connection
connection.close()