import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *
from dotenv import load_dotenv
from pathlib import Path

# Create BASE_DIR and .env path
BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
# Load environment variables from .env file
load_dotenv(ENV_PATH)

# Create Spark session
spark = SparkSession.builder \
    .appName("streaming") \
    .getOrCreate()

# Define schema for incoming data
schema = StructType([
    StructField("user_id", StringType()),
    StructField("item_id", StringType()),
    StructField("event_type", StringType()),
    StructField("timestamp", LongType())
])

# Create streaming Dataframe from a socket source
df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "fashion.user.events")
    .load()
)

events = df.select(from_json(col("value").cast("string"), schema=schema).alias("e").select("e.*"))

# Write streaming Dataframe to console
events.writeStream \
    .format("parquet") \
    .option("path", os.path.join(BASE_DIR, "data", "streaming", "events")) \
    .option("checkpointLocation", os.path.join(BASE_DIR, "data", "checkpoints")) \
    .start() \
    .awaitTermination()