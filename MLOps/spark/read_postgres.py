import os
from pyspark.sql import SparkSession

# ================
# CONFIGURATION
# ================
POSTGRES_URI_SPARK = os.getenv("POSTGRES_URI_SPARK")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

TABLE_NAME = "fashion"
JDBC_DRIVER = "org.postgresql.Driver"

# =================
# SPARK SESSION
# =================
spark = (
    SparkSession.builder
    .appName("Fashion-Postgres-To-Spark")
    .getOrCreate()
)

# =================
# READ POSTGRESQL TABLE
# =================
df = (
    spark.read
    .format("jdbc")
    .option("url", POSTGRES_URI_SPARK)
    .option("dbtable", TABLE_NAME)
    .option("user", POSTGRES_USER)
    .option("password", POSTGRES_PASSWORD)
    .option("driver", JDBC_DRIVER)
    .load()
)

# =================
# VALIDATION
# =================
df.show(20, truncate=False)
df.printSchema()

# =================
# STOP SPARK SESSION
# =================
spark.stop()