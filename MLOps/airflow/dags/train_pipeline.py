from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    "fashion_training",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    schedule=None # Concern this schedule, we can change flexibly according to our needs
) as dag:
    
    train_task = BashOperator(
        task_id="train_model",
        bash_command="python3 /app/MLOps/training/train_recommender.py"
    )