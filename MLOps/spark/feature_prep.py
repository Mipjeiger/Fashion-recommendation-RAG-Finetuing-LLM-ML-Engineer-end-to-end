import os
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent  # MLOps/
ENV_PATH = BASE_DIR / ".env"

# Load environment variables from .env file
load_dotenv(ENV_PATH)

# ----------------------------------------------------
# CONTRACT (FAIL FAST)
# ----------------------------------------------------
REQUIRED_ENV = ["RUN_ID", "CURATED_PATH", "FEATURE_PATH"]
missing = [e for e in REQUIRED_ENV if not os.getenv(e)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {missing}")

RUN_ID = os.getenv("RUN_ID")
CURATED_PATH = os.getenv("CURATED_PATH")   # ← passed from Airflow DAG
FEATURE_PATH = os.getenv("FEATURE_PATH")   # ← passed from Airflow DAG

# -------------------------------------------------------------------
# SPARK SESSION
# -------------------------------------------------------------------
spark = SparkSession.builder \
    .appName("feature-prep") \
    .getOrCreate()

# -------------------------------------------------------------------
# INPUT / OUTPUT PATH
# -------------------------------------------------------------------
input_path = Path(CURATED_PATH)    # ← reads from where batch_etl.py wrote
output_path = Path(FEATURE_PATH)   # ← writes to feature store path

# -------------------------------------------------------------------
# READ DATA
# -------------------------------------------------------------------
df = spark.read.parquet(str(input_path))
if df.rdd.isEmpty():
    raise ValueError(f"Input dataset is empty at path: {input_path}")

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

spark.stop()
print(f"[SUCCESS] Feature prep completed | run_id={RUN_ID}")