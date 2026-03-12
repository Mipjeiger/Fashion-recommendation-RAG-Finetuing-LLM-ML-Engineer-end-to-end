from kafka import KafkaProducer
import json
import os
from dotenv import load_dotenv
from pathlib import Path

# Configuration
ENV_PATH = Path(__file__).parents[2] / '.env'
load_dotenv(ENV_PATH)

producer = KafkaProducer(
    bootstrap_server=os.getenv("KAFKA_BOOTSTRAP_SERVER"),
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)

def send_event(data):
    producer.send(os.getenv("KAFKA_TOPIC"), value=data)
    producer.flush()