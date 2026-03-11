from kafka import KafkaConsumer
import json
import psycopg2
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
load_dotenv(env_path)

# Retrieve database connection parameters
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

consumer = KafkaConsumer(
    "fashion-events",
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# Iterate consumer to read messages
for msg in consumer:
    print("Received event:", msg.value)
    event = msg.value
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE fashion_system
            SET view_count = view_count + 1
            WHERE item_id = %s
            """, (event["item_id"],))
        conn.commit()
        print(f"Rows affected:", cur.rowcount)