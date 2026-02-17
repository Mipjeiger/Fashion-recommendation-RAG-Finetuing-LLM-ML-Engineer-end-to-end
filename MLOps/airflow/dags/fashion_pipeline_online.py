from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.sdk import task
import os
import psycopg2
from datetime import datetime

"""Database connection for fashion pipeline Online - Airflow DAG.
This DAG orchestrates the batch ETL and feature preparation steps using Spark,
and then publishes the features to Redis for online serving."""

# Create BASE_DIR and CURATED_PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # MLOps/airflow/dags
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR)) # MLOps/


SPARK_DIR = os.path.join(PROJECT_ROOT, "spark")
INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "matched_fashion_dataset.parquet")
CURATED_PATH = os.path.join(PROJECT_ROOT, "data", "lakehouse", "fashion", "curated", "items")
FEATURE_PATH = os.path.join(PROJECT_ROOT, "data", "lakehouse", "fashion", "features", "offline")

with DAG(
    dag_id="fashion_pipeline_online",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fashion", "mlops", "online"],
) as dag:

    @task
    def record_start(**context):
        print(f"Pipeline started run_id={context.get('run_id')}")

    @task
    def validate_parquet(path: str):
        if not os.path.exists(path):
            raise RuntimeError(f"Input dataset not found at path: {path}")

    spark_batch_etl = SparkSubmitOperator(
        task_id="spark_batch_etl",
        application=os.path.join(SPARK_DIR, "batch_etl.py"),
        name="fashion-online-batch-etl",
        conn_id="spark_default",
        verbose=True,
        conf={
            "spark.master": "spark://localhost:7077"
        },
        env_vars={
            "RUN_ID": "{{ run_id }}",
            "PROCESS_DATE": datetime.now().strftime("%Y-%m-%d"),
            "INPUT_PATH": INPUT_PATH,
            "OUTPUT_PATH": CURATED_PATH,
        },
    )

    spark_feature_prep = SparkSubmitOperator(
        task_id="spark_feature_prep",
        application=os.path.join(SPARK_DIR, "feature_prep.py"),
        name="fashion-online-feature-prep",
        conn_id="spark_default",
        verbose=True,
        conf={
            "spark.master": "spark://localhost:7077"
        },
        env_vars={
            "CURATED_PATH": CURATED_PATH
        },
    )

    @task
    def publish_redis(**context):
        from airflow.task.publish_redis import publish_features_to_redis
        process_date = datetime.now().strftime("%Y-%m-%d")
        publish_features_to_redis(process_date=process_date)

    @task
    def record_success(**context):
        print(f"Pipeline completed successfully run_id={context.get('run_id')}")

    (
        record_start()
        >> spark_batch_etl
        >> validate_parquet(path=CURATED_PATH)
        >> spark_feature_prep
        >> publish_redis()
        >> record_success()
    )