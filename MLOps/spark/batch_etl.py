import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
# Load environment variables from .env file
load_dotenv(ENV_PATH)

spark = SparkSession.builder \
        .appName("batch-etl") \
        .getOrCreate()

df = spark.read.parquet(os.path.join(BASE_DIR, "data", "matched_fashion_dataset.parquet"))
print("\nDataframe Spark:")
print(df.show(15))