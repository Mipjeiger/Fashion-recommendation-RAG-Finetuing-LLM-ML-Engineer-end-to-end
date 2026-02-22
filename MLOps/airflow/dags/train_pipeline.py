# MLOps/airflow/dags/train_pipeline.py
import os
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from MLOps.notifications.slack_API.revenue_notify  import notify_daily_revenue_from_df
from MLOps.notifications.slack_API.revenue_notify  import notify_weekly_revenue_from_df
from MLOps.notifications.slack_API.learning_notify import notify_weekly_learnings_from_df
from notifications.slack_service                   import slack

DATABASE = Path(os.getenv("DATABASE_PATH", "/app/database/data/raw/matched_fashion_dataset.parquet"))

def on_failure(context):
    slack.notify_pipeline_failed(
        dag_id  = context["dag"].dag_id,
        task_id = context["task"].task_id,
        error   = context["exception"],
    )

default_args = {
    "owner"              : "MLOps",
    "retries"            : 1,
    "retry_delay"        : timedelta(minutes=5),
    "on_failure_callback": on_failure,
}

# ── Task Functions ──────────────────────────────
def run_daily_revenue():
    df = pd.read_parquet(DATABASE)
    notify_daily_revenue_from_df(df)

def run_weekly_revenue():
    df   = pd.read_parquet(DATABASE)
    week = f"Week {datetime.now().isocalendar()[1]}"
    notify_weekly_revenue_from_df(df, week=week)

def run_weekly_learnings():
    df   = pd.read_parquet(DATABASE)
    week = f"Week {datetime.now().isocalendar()[1]}"
    notify_weekly_learnings_from_df(df, week=week)

# ── DAG ────────────────────────────────────────
with DAG(
    "fashion_training",
    default_args = default_args,
    start_date   = datetime(2026, 1, 1),
    catchup      = False,
    schedule     = None,
) as dag:

    train_task = BashOperator(
        task_id      = "train_model",
        bash_command = "python3 /app/MLOps/training/train_recommender.py",
    )

    daily_revenue_task = PythonOperator(
        task_id         = "notify_daily_revenue",
        python_callable = run_daily_revenue,
    )

    weekly_revenue_task = PythonOperator(
        task_id         = "notify_weekly_revenue",
        python_callable = run_weekly_revenue,
    )

    weekly_learnings_task = PythonOperator(
        task_id         = "notify_weekly_learnings",
        python_callable = run_weekly_learnings,
    )

    # ── Task Order ─────────────────────────────
    train_task >> daily_revenue_task >> weekly_revenue_task >> weekly_learnings_task