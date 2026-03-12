import psycopg2
import os
from dotenv import load_dotenv
from pathlib import Path

# Configuration
ENV_PATH = Path(__file__).parents[3] / '.env'
load_dotenv(ENV_PATH)

# Postgresql connection
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

def process_event(event):
    with conn.cursor() as cur:
        cur.execute("""
        INSERT INTO events(event_type, item_id)
        VALUES(%s, %s)
        """,
        (event["event_type"], event["item_id"])
        )

        conn.commit()