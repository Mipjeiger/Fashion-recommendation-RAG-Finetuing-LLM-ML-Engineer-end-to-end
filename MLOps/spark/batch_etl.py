import os
import hashlib
import psycopg2
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
# Load environment variables from .env file
load_dotenv(ENV_PATH)

RUN_ID = os.getenv("RUN_ID")
POSTGRES_URI = os.getenv("POSTGRES_URI")

# -------------------------------------------------------------------
# SPARK SESSION
# -------------------------------------------------------------------
spark = SparkSession.builder \
        .appName("batch-etl") \
        .getOrCreate()

# -------------------------------------------------------------------
# INPUT / OUTPUT PATH
# -------------------------------------------------------------------
input_path = BASE_DIR / "data" / "matched_fashion_dataset.parquet"
output_path = BASE_DIR / "data" / f"fashion_items_run_id={RUN_ID}"

df = spark.read.parquet(str(input_path))

if df.rdd.isEmpty():
    raise ValueError("Input dataset is empty")

row_count = df.count()
schema_hash = hashlib.md5(str(df.schema).encode()).hexdigest()

# -------------------------------------------------------------------
# WRITE DATA (IMMUTABLE, VERSIONED)
# -------------------------------------------------------------------
(
    df.write
    .mode("overwrite")
    .parquet(str(output_path))
)

# -------------------------------------------------------------------
# REGISTER DATASET IN POSTGRES
# -------------------------------------------------------------------
conn = psycopg2.connect(POSTGRES_URI)
cur = conn.cursor()

cur.execute("""
INSERT INTO data_registry
(dataset_name, dataset_version, path, row_count, schema_hash)
VALUES (%s, %s, %s, %s, %s)
""", (
    "matched_fashion_dataset",
    RUN_ID,
    str(output_path),
    row_count,
    schema_hash
))

conn.commit()
cur.close()
conn.close()

spark.stop()
print(f"[SUCCESS] Batch ETL completed | rows={row_count} | run_id={RUN_ID} | schema_hash={schema_hash}")