from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.decorators import task
import os
import psycopg2
from datetime import datetime

POSTGRES_URI = os.getenv("POSTGRES_URI")

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
    def mark_pipeline_start(run_id: str, dag_id: str):
        conn = psycopg2.connect(POSTGRES_URI)
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO pipeline_runs (run_id, dag_id, status, started_at)
        VALUES (%s, %s, %s, now())
        ON CONFLICT (run_id)
        DO UPDATE SET status = EXCLUDED.status
        """, (run_id, dag_id, "RUNNING"))

        conn.commit()
        cur.close()
        conn.close()
    
    # ----------------------------------------------------
    # SPARK BATCH ETL TASK
    # ----------------------------------------------------
    spark_etl = SparkSubmitOperator(
        task_id="spark_batch_etl",
        application="/opt/project/spark/batch_etl.py",
        name="fashion-batch-etl",
        conn_id="spark_default",
        env_vars={
            "RUN_ID": "{{run_id}}"
        },
        verbose=True
    )
    
    spark_feature_prep = SparkSubmitOperator(
        task_id="spark_feature_prep",
        application="/opt/project/spark/feature_prep.py",
        name="fashion-feature-prep",
        conn_id="spark_default",
        env_vars={
            "RUN_ID": "{{run_id}}"
        },
        verbose=True
    )

    # ---------------------------------------------------------------
    # PIPELINE STATE: SUCCESS
    # ---------------------------------------------------------------
    @task
    def mark_pipeline_success(run_id: str):
        conn = psycopg2.connect(POSTGRES_URI)
        cur = conn.cursor()

        cur.execute("""
        UPDATE pipeline_runs
        SET status = %s, finished_at = now()
        WHERE run_id = %s
        """, ("SUCCESS", run_id))

        conn.commit()
        cur.close()
        conn.close()

    # ---------------------------------------------------------------
    # DEPENDENCIES
    # ---------------------------------------------------------------
    start = mark_pipeline_start(
        run_id="{{run_id}}",
        dag_id="{{dag.dag_id}}"
    )

    success = mark_pipeline_success(run_id="{{run_id}}")

    start >> spark_etl >> spark_feature_prep >> success