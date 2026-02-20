"""
Daily ingestion DAG for IndoCloth Market.
"""
from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.operators.python import PythonOperator
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
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="indocloth_daily_ingestion",
    default_args=default_args,
    description="Daily data ingestion and processing for IndoCloth Market",
    schedule_interval="0 2 * * *",  # Daily at 2 AM UTC
    start_date=datetime(2026, 2, 20),
    catchup=False,
    tags=["indocloth", "ingestion", "daily"],
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

    # Trigger daily metrics calculation
    calculate_daily_metrics = SimpleHttpOperator(
        task_id="calculate_daily_metrics",
        http_conn_id="backend_api",
        endpoint=f"{API_V1_PREFIX}/metrics/daily",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{"date": null}',
        response_check=lambda response: response.status_code == 200,
    )

    # Send daily report to Slack
    send_daily_report = SimpleHttpOperator(
        task_id="send_daily_report",
        http_conn_id="backend_api",
        endpoint=f"{API_V1_PREFIX}/slack/notify",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='''{
            "notification_type": "daily_report",
            "data": {
                "ai_revenue_share": "{{ ti.xcom_pull(task_ids='calculate_daily_metrics')['data']['ai_revenue_share'] }}",
                "avg_cart_uplift": "{{ ti.xcom_pull(task_ids='calculate_daily_metrics')['data']['avg_cart_uplift'] }}",
                "top_recommended_item": "{{ ti.xcom_pull(task_ids='calculate_daily_metrics')['data']['top_recommended_item'] }}",
                "conversion_delta": "{{ ti.xcom_pull(task_ids='calculate_daily_metrics')['data']['conversion_delta'] }}"
            }
        }''',
        response_check=lambda response: response.status_code == 200,
    )

    check_backend_health >> calculate_daily_metrics >> send_daily_report
