from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

with DAG(
    dag_id='fashion_pipeline',
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False
) as dag:
    
    spark_conf = {
        "spark.executor.memory": "512m",
        "spark.driver.memory": "512m",
        "spark.sql.shuffle.partitions": "4"
    }

    spark_etl = SparkSubmitOperator(
        task_id="spark_batch_etl",
        application="/opt/project/spark/batch_etl.py",
        name="fashion-batch-etl",
        conn_id="spark_default",
        conf=spark_conf,
        verbose=True
        
    )