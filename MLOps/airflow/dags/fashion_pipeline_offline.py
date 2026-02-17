from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.decorators import task
from datetime import datetime
import os
import psycopg2

"""Database connection for fashion pipeline Offline - Airflow DAG.
This DAG orchestrates the batch ETL and feature preparation steps using Spark, 
and then stores the features in the data use PostgreSQL for offline training."""

# CONFIGURATION
POSTGRES_URI = os.getenv("POSTGRES_URI")

CURATED_PATH = "/data/lakehouse/fashion/curated/items"
FEATURE_PATH = "/data/lakehouse/fashion/features/offline"
INPUT_PATH = "/data/raw/matched_fashion_dataset.parquet"

with DAG(
    dag_id="fashion_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fashion", "mlops"],
) as dag:

    @task
    def mark_start(run_id=None, dag_id=None):
        print(f"Starting pipeline: dag_id={dag_id}, run_id={run_id}")
        if not POSTGRES_URI:
            print(f"[WARNING] POSTGRES_URI not set, skipping DB write")
            return
        with psycopg2.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO pipeline_runs (run_id, dag_id, status, started_at)
                VALUES (%s, %s, 'RUNNING', now())
                ON CONFLICT (run_id) DO UPDATE SET status='RUNNING'
                """, (run_id, dag_id))

    @task
    def validate_path(path: str):
        if not os.path.exists(path):
            raise RuntimeError(f"Missing output path: {path}")

    @task
    def mark_success(run_id=None):
        if not POSTGRES_URI:
            print(f"[WARNING] POSTGRES_URI not set, skipping DB write")
            return
        with psycopg2.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE pipeline_runs
                SET status='SUCCESS', finished_at=now()
                WHERE run_id=%s
                """, (run_id,))

    spark_batch_etl = SparkSubmitOperator(
        task_id="spark_batch_etl",
        application="/opt/project/spark/batch_etl.py",
        conn_id="spark_default",
        env_vars={
            "RUN_ID": "{{ run_id }}",
            "PROCESS_DATE": "{{ ds }}",
            "INPUT_PATH": INPUT_PATH,
            "OUTPUT_PATH": CURATED_PATH,
        },
    )

    spark_feature_prep = SparkSubmitOperator(
        task_id="spark_feature_prep",
        application="/opt/project/spark/feature_prep.py",
        conn_id="spark_default",
        env_vars={
            "RUN_ID": "{{ run_id }}",
            "PROCESS_DATE": "{{ ds }}",
            "CURATED_PATH": CURATED_PATH,
            "FEATURE_PATH": FEATURE_PATH,
        },
    )

    (
        mark_start("{{ run_id }}", "{{ dag.dag_id }}")
        >> spark_batch_etl
        >> validate_path(CURATED_PATH)
        >> spark_feature_prep
        >> validate_path(FEATURE_PATH)
        >> mark_success("{{ run_id }}")
    )