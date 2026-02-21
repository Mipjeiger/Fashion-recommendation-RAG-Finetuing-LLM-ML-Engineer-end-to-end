from kafka import KafkaConsumer
import json
import psycopg2
import os
from sqlalchemy import create_engine

# Create connection to PostgreSQL
DATABASE_URL = os.getenv("POSTGRES_URI")
engine = create_engine(DATABASE_URL)

consumer = KafkaConsumer(
    "fashion-events",
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda v: json.loads(v.decode('utf-8'))
)

conn = psycopg2.connect(DATABASE_URL)

# Iterate consumer to read messages
for msg in consumer:
    event = msg.value
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE fashion_system
            SET view_count = view_count + 1
            WHERE item_id = %s
            """, (event["item_id"],))
        conn.commit()