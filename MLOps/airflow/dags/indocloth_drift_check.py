"""
Drift detection DAG for IndoCloth Market.
"""
from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.sensors.http import HttpSensor
from datetime import datetime, timedelta
import os

# Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://backend:8000")
API_V1_PREFIX = "/api/v1"

default_args = {
    "owner": "indocloth",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="indocloth_drift_check",
    default_args=default_args,
    description="Periodic drift detection check for IndoCloth Market",
    schedule_interval="0 * * * *",  # Every hour
    start_date=datetime(2026, 2, 20),
    catchup=False,
    tags=["indocloth", "drift", "monitoring"],
) as dag:

    # Check backend health
    check_backend_health = HttpSensor(
        task_id="check_backend_health",
        http_conn_id="backend_api",
        endpoint="/health",
        method="GET",
        timeout=30,
        poke_interval=10,
    )

    # Note: Actual drift detection would be triggered via API endpoint
    # This is a placeholder - in production, you'd have a dedicated endpoint
    # that fetches recent embeddings and runs drift detection
    check_drift = SimpleHttpOperator(
        task_id="check_drift",
        http_conn_id="backend_api",
        endpoint=f"{API_V1_PREFIX}/drift/check",  # This endpoint would need to be created
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{}',
        response_check=lambda response: response.status_code == 200,
    )

    check_backend_health >> check_drift
