from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.decorators import task
import os
import psycopg2
from datetime import datetime

"""Database connection for fashion pipeline Online - Airflow DAG. 
This DAG orchestrates the batch ETL and feature preparation steps using Spark, 
and then publishes the features to Redis for online serving."""

# Create BASE_DIR and CURATED_PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CURATED_PATH = os.path.join(BASE_DIR, "data", "lakehouse", "fashion", "curated", "items")
INPUT_PATH = os.path.join(BASE_DIR, "data", "raw", "matched_fashion_dataset.parquet")

# ---------------------------------------------------
# AIRFLOW DAG DEFINITION
# ---------------------------------------------------
with DAG(
    dag_id='fashion_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fashion", "mlops"]
) as dag:
    
    # ----------------------------------------------------
    # PIPELINE STAT: START
    # ----------------------------------------------------
    @task
    def record_start(run_id: str):
        print(f"Pipeline started run_id={run_id}")

    @task
    def validate_parquet(path: str):
        if not os.path.exists(path=path):
            raise RuntimeError(f"Input dataset not found at path: {path}")
    
    # ----------------------------------------------------
    # SPARK BATCH ETL TASK
    # ----------------------------------------------------
    spark_batch_etl = SparkSubmitOperator(
        task_id="spark_batch_etl",
        application="/opt/project/spark/batch_etl.py",
        name="fashion-batch-etl",
        conn_id="spark_default",
        env_vars={
            "RUN_ID": "{{run_id}}",
            "PROCESS_DATE": "{{ ds }}",
            "INPUT_PATH": INPUT_PATH,
            "OUTPUT_PATH": CURATED_PATH
        },
        verbose=True
    )
    
    spark_feature_prep = SparkSubmitOperator(
        task_id="spark_feature_prep",
        application="/opt/project/spark/feature_prep.py",
        name="fashion-feature-prep",
        conn_id="spark_default",
        env_vars={
            "PROCESS_DATE": "{{ ds }}",
            "CURATED_PATH": CURATED_PATH
        },
        verbose=True
    )

    @task
    def publish_redis(ds: str):
        from airflow.task.publish_redis import publish_features_to_redis
        publish_features_to_redis(process_date=ds)

    @task
    def record_success(run_id: str):
        print(f"Pipeline completed successfully run_id={run_id}")

    (
        record_start(run_id="{{run_id}}")
        >> spark_batch_etl
        >> validate_parquet(path=CURATED_PATH)
        >> spark_feature_prep
        >> publish_redis(ds="{{ ds }}")
        >> record_success(run_id="{{run_id}}")
    )