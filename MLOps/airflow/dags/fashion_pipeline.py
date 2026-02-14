from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    dag_id='fashion_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False
) as dag:
    
    spark_etl = BashOperator(
    task_id="spark_batch_etl",
    bash_command="spark-submit /opt/project/spark/batch_etl.py"
    )

    spark_features = BashOperator(
    task_id="spark_features_rep",
    bash_command="spark-submit /opt/project/spark/feature_rep.py"
    )

    train = BashOperator(
    task_id="pytorch_training",
    bash_command="python /opt/project/training/train.py"
    )

    spark_etl >> spark_features >> train