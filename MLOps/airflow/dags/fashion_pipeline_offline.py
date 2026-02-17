from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.sdk import task
from datetime import datetime
import os
import psycopg2

"""Database connection for fashion pipeline Offline - Airflow DAG.
This DAG orchestrates the batch ETL and feature preparation steps using Spark,
and then stores the features in the data use PostgreSQL for offline training."""

# CONFIGURATION
POSTGRES_URI = os.getenv("POSTGRES_URI")

# Create BASE_DIR and CURATED_PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # MLOps/airflow/dags
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR)) # MLOps/


SPARK_DIR = os.path.join(PROJECT_ROOT, "spark")
INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "matched_fashion_dataset.parquet")
CURATED_PATH = os.path.join(PROJECT_ROOT, "data", "lakehouse", "fashion", "curated", "items")
FEATURE_PATH = os.path.join(PROJECT_ROOT, "data", "lakehouse", "fashion", "features", "offline")

with DAG(
    dag_id="fashion_pipeline_offline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["fashion", "mlops", "offline"],
) as dag:

    @task
    def mark_start(**context):
        run_id = context.get("run_id")
        dag_id = context.get("dag").dag_id
        print(f"Starting offline pipeline: dag_id={dag_id}, run_id={run_id}")
        if not POSTGRES_URI:
            print("[WARNING] POSTGRES_URI not set, skipping DB write")
            return
        with psycopg2.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO pipeline_runs (run_id, dag_id, status, started_at)
                VALUES (%s, %s, 'RUNNING', now())
                ON CONFLICT (run_id) DO UPDATE SET status='RUNNING'
                """, (run_id, dag_id))

    @task
    def mark_success(**context):
        run_id = context.get("run_id")
        print(f"Marking offline pipeline as SUCCESS: run_id={run_id}")
        if not POSTGRES_URI:
            print("[WARNING] POSTGRES_URI not set, skipping DB write")
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
        application=os.path.join(SPARK_DIR, "batch_etl.py"),
        conn_id="spark_default",
        name="fashion-offline-batch-etl",
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
        conn_id="spark_default",
        name="fashion-offline-feature-prep",
        verbose=True,
        conf={
            "spark.master": "spark://localhost:7077"
        },
        env_vars={
            "RUN_ID": "{{ run_id }}",
            "CURATED_PATH": CURATED_PATH,
            "PROCESS_DATE": datetime.now().strftime("%Y-%m-%d"),
            "FEATURE_PATH": FEATURE_PATH,
        },
    )

    mark_start() >> spark_batch_etl >> spark_feature_prep >> mark_success()