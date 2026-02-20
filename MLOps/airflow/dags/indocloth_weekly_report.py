"""
Weekly reporting DAG for IndoCloth Market.
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
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
}

with DAG(
    dag_id="indocloth_weekly_report",
    default_args=default_args,
    description="Weekly business insights report for IndoCloth Market",
    schedule_interval="0 8 * * 1",  # Every Monday at 8 AM UTC
    start_date=datetime(2026, 2, 20),
    catchup=False,
    tags=["indocloth", "reporting", "weekly"],
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

    # Calculate weekly insights
    calculate_weekly_insights = SimpleHttpOperator(
        task_id="calculate_weekly_insights",
        http_conn_id="backend_api",
        endpoint=f"{API_V1_PREFIX}/metrics/weekly",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='{}',
        response_check=lambda response: response.status_code == 200,
    )

    # Send weekly report to Slack
    send_weekly_report = SimpleHttpOperator(
        task_id="send_weekly_report",
        http_conn_id="backend_api",
        endpoint=f"{API_V1_PREFIX}/slack/notify",
        method="POST",
        headers={"Content-Type": "application/json"},
        data='''{
            "notification_type": "weekly_report",
            "data": {
                "insights": "{{ ti.xcom_pull(task_ids='calculate_weekly_insights')['data']['insights'] }}"
            }
        }''',
        response_check=lambda response: response.status_code == 200,
    )

    check_backend_health >> calculate_weekly_insights >> send_weekly_report
