import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, LongType
from pyspark.sql.functions import from_json, col
from dotenv import load_dotenv
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
# Load environment variables from .env file
load_dotenv(ENV_PATH)

# ---------------------------------------------------
# SPARK SESSION
# ---------------------------------------------------
spark = SparkSession.builder \
    .appName("streaming") \
    .getOrCreate()


# ---------------------------------------------------
# SCHEMA FOR INCOMING STREAMING DATA
# ---------------------------------------------------
schema = StructType([
    StructField("user_id", StringType()),
    StructField("item_id", StringType()),
    StructField("event_type", StringType()),
    StructField("timestamp", LongType())
])

# ---------------------------------------------------
# READ STREAMING DATA FROM KAFKA
# ---------------------------------------------------
raw_stream = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "fashion.user.events")
    .option("startingOffsets", "latest")
    .load()
)

events = (
    raw_stream
    .selectExpr("CAST(value AS STRING)")
    .select(from_json(col("value"), schema=schema).alias("e"))
    .select("e.*")
)

# -------------------------------------------------------------------
# SINK (PARQUET + CHECKPOINT)
# -------------------------------------------------------------------
output_path = BASE_DIR / "data" / "streaming" / "events"
checkpoint_path = BASE_DIR / "data" / "checkpoints" / "fashion_events"

# Write streaming Dataframe to console
query = (
    events.writeStream
    .format("parquet")
    .outputMode("append")
    .option("path", str(output_path))
    .option("checkpointLocation", str(checkpoint_path))
    .start()
)

query.awaitTermination()