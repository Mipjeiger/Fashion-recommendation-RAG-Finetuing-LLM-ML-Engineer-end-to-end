import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
# Load environment variables from .env file
load_dotenv(ENV_PATH)

RUN_ID = os.getenv("RUN_ID")

# -------------------------------------------------------------------
# SPARK SESSION
# -------------------------------------------------------------------
spark = SparkSession.builder \
    .appName("feature-prep") \
    .getOrCreate()

# -------------------------------------------------------------------
# INPUT / OUTPUT PATH
# -------------------------------------------------------------------
input_path = BASE_DIR / "data" / "processed" / f"fashion_items_run_id={RUN_ID}"
output_path = BASE_DIR / "data" / "training"

# -------------------------------------------------------------------
# READ DATA
# -------------------------------------------------------------------
df = spark.read.parquet(str(input_path))

if df.rdd.isEmpty():
    raise ValueError("Input dataset is empty")

# -------------------------------------------------------------------
# FEATURE ENGINEERING
# -------------------------------------------------------------------
feature_df = (
    df
    .withColumn("run_id", lit(RUN_ID))
)

# -------------------------------------------------------------------
# WRITE TRAINING DATA (APPEND, PARTITIONED)
# -------------------------------------------------------------------
(
    feature_df.write
    .mode("append")
    .partitionBy("run_id")
    .parquet(str(output_path))
)

# Close spark connection 
spark.stop()
print(f"[SUCCESS] Feature prep completed | run_id={RUN_ID}")