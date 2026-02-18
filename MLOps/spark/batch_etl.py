import os
import hashlib
import psycopg2
from dotenv import load_dotenv


from pyspark.sql.functions import lit
from pyspark.sql import SparkSession
from pathlib import Path

# Load .env path
BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH)

# ----------------------------------------------------
# CONTRACT (FAIL FAST)
# ----------------------------------------------------
REQUIRED_ENV = ["RUN_ID", "PROCESS_DATE", "INPUT_PATH", "OUTPUT_PATH"]
missing = [e for e in REQUIRED_ENV if not os.getenv(e)]
if missing:
    raise RuntimeError(f"Missing required environment variables: {missing}")

RUN_ID = os.getenv("RUN_ID")
PROCESS_DATE = os.getenv("PROCESS_DATE")
INPUT_PATH = os.getenv("INPUT_PATH")
OUTPUT_PATH = os.getenv("OUTPUT_PATH")

# ----------------------------------------------------
# SPARK SESSION
# ----------------------------------------------------
spark = SparkSession.builder \
    .appName("fashion-batch-etl") \
    .getOrCreate()
spark.sparkContext.setLogLevel("WARN") # Set log level to WARN to reduce verbosity

# ----------------------------------------------------
# READ INPUT DATA
# ----------------------------------------------------
df = spark.read.parquet(INPUT_PATH)
if df.rdd.isEmpty():
    raise RuntimeError(f"Input dataset is empty at path: {INPUT_PATH}")

row_count = df.count()
schema_hash = hashlib.md5(str(df.schema).encode()).hexdigest()

# ----------------------------------------------------
# TRANSFORM
# ----------------------------------------------------
df_out = (
    df
    .withColumn("run_id", lit(RUN_ID))
    .withColumn("dt", lit(PROCESS_DATE))
    .dropDuplicates()
)

# ----------------------------------------------------
# WRITE IMMUTABLE PARQUET (APPEND, PARTITIONED)
# ----------------------------------------------------
(
    df_out
    .write
    .mode("append")
    .partitionBy("dt")
    .parquet(OUTPUT_PATH)
)

spark.stop()
print(
    f"[SUCCESS] rows={row_count} | run_id={RUN_ID}"
    f"dt={PROCESS_DATE} | schema_hash={schema_hash}"
)