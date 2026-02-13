import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from .env file
load_dotenv(ENV_PATH)

# Create Spark session
spark = SparkSession.builder \
    .appName("feature-prep") \
    .getOrCreate()

df = spark.read.parquet(os.path.join(BASE_DIR, "data", "matched_fashion_dataset.parquet"))

try:
    output_path = os.path.join(BASE_DIR, "data", "training", "fashion_items.parquet")
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Use PySpark's write method (not pandas' to_parquet)
    df.write.mode("overwrite").parquet(output_path)
    
    print(f"Dataframe saved to {output_path}")
except Exception as e:
    print(f"Error saving dataframe: {e}")