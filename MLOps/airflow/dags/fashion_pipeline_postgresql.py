from dotenv.parser import parse_unquoted_value
import os
import psycopg2
import psycopg2.extras
import pandas as pd
import pyarrow.parquet as pq
from datetime import datetime
from airflow import DAG
from airflow.sdk import task

""""Database connection for PostgreSQL - Airflow DAG.
This DAG is a demonstration of how to connect to a PostgreSQL database from an Airflow",
and storing the pipeline run status in a table."""

# CONFIGURATION
POSTGRES_URI = os.getenv("POSTGRES_URI")

# Create BASE_DIR and CURATED_PATH
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # MLOps/airflow/dags
PROJECT_ROOT = os.path.dirname(os.path.dirname(BASE_DIR)) # MLOps/

# Path to the source data
INPUT_PATH = os.path.join(PROJECT_ROOT, "data", "raw", "matched_fashion_dataset.parquet")


# ----------------------------------------------------
# DAG DEFINITION
# ----------------------------------------------------
with DAG(
    dag_id="database_fashion_pipeline",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    is_paused_upon_creation=False,
    tags=["fashion", "mlops", "database"]
) as dag:

    @task
    def mark_start(**context):
        """Logs the start of the pipeline run to the pipeline_runs table."""
        run_id = context.get("run_id")
        dag_id = context.get("dag").dag_id
        print(f"Starting database pipeline: dag_id={dag_id}, run_id={run_id}")
        
        if not POSTGRES_URI:
            print("[WARNING] POSTGRES_URI is not set. Skipping DB logging.")
            return
        with psycopg2.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                INSERT INTO pipeline_runs (run_id, dag_id, status, started_at)
                VALUES (%s, %s, 'RUNNING', now())
                ON CONFLICT (run_id) DO UPDATE SET status='RUNNING', started_at=now();
                """, (run_id, dag_id))


    @task
    def load_fashion_data(**context):
        """Streams fashion data from Parquet and loads into PostgreSQL in chunks."""
        if not POSTGRES_URI:
            raise ValueError("POSTGRES_URI is not set. Skipping DB logging.")
        
        if not os.path.exists(INPUT_PATH):
            raise FileNotFoundError(f"Input file not found at: {INPUT_PATH}")

        required_columns = [
            "item_id", "category", "subcategory", "sleeve_type", 
            "season", "fabric", "occasion", "formality_level", 
            "size_range", "brand", "view_count", "click_count", 
            "purchase_count", "length_cm", "price", "stocks"
        ]

        # Use SQL with %s for execute_values
        insert_query = """INSERT INTO fashion (
            item_id, category, subcategory, sleeve_type, 
            season, fabric, occasion, formality_level, 
            size_range, brand, view_count, click_count, 
            purchase_count, length_cm, price, stocks
        )
        VALUES %s
        ON CONFLICT (item_id) DO UPDATE SET
            category = EXCLUDED.category,
            subcategory = EXCLUDED.subcategory,
            sleeve_type = EXCLUDED.sleeve_type,
            season = EXCLUDED.season,
            fabric = EXCLUDED.fabric,
            occasion = EXCLUDED.occasion,
            formality_level = EXCLUDED.formality_level,
            size_range = EXCLUDED.size_range,
            brand = EXCLUDED.brand,
            view_count = EXCLUDED.view_count,
            click_count = EXCLUDED.click_count,
            purchase_count = EXCLUDED.purchase_count,
            length_cm = EXCLUDED.length_cm,
            price = EXCLUDED.price,
            stocks = EXCLUDED.stocks;
        """

        print(f"Streaming data from {INPUT_PATH} using pyarrow...")
        
        # Open the Parquet file as a stream
        parquet_file = pq.ParquetFile(INPUT_PATH)
        
        # Connect and insert in batches to save memory
        with psycopg2.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                batch_count = 0
                total_loaded = 0

                # Stream the file in batches of 5000 rows chunksize
                for batch in parquet_file.iter_batches(batch_size=5000, columns=required_columns):
                    batch_count += 1
                    df_batch = batch.to_pandas()
                    data_tuples = [tuple(x) for x in df_batch.to_numpy()]
                    
                    print(f"Loading batch {batch_count} ({len(data_tuples)} rows)...")
                    
                    psycopg2.extras.execute_values(
                        cur, 
                        insert_query, 
                        data_tuples
                    )
                    total_loaded += len(data_tuples)
                
                conn.commit()
                print(f"Successfully loaded {total_loaded} rows into PostgreSQL 'fashion' table.")
    @task
    def mark_success(**context):
        """Logs the completion of the pipeline run."""
        run_id = context.get("run_id")
        dag_id = context.get("dag").dag_id
        print(f"Marking database pipeline as SUCCESS: dag_id={dag_id}, run_id={run_id}")
        if not POSTGRES_URI:
            print("[WARNING] POSTGRES_URI is not set")
            return
        with psycopg2.connect(POSTGRES_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                UPDATE pipeline_runs
                SET status='SUCCESS', finished_at=now()
                WHERE run_id=%s
                """, (run_id,))


    # Define DAG flow
    mark_start() >> load_fashion_data() >> mark_success()   