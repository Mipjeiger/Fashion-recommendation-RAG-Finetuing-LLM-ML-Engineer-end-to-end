import json
from kafka import KafkaConsumer
import os
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def get_consumer():
    return KafkaConsumer(
        "realtime-recommendation",
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )