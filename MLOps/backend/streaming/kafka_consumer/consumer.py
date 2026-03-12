from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parents[2]))        # → MLOps/backend/streaming
sys.path.append(str(Path(__file__).parents[3]))        # → MLOps/backend


from kafka import KafkaConsumer
import json
import os
from streaming.streamer.stream_processor import process_event
from dotenv import load_dotenv

# Load environment variables
ENV_PATH = Path(__file__).parents[4] / '.env'
load_dotenv(ENV_PATH)

consumer = KafkaConsumer(
    os.getenv("KAFKA_TOPIC"),
    bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVER"),
    value_deserializer=lambda v: json.loads(v.decode('utf-8')),
    auto_offset_reset='earliest'
)


# Iterate consumer to read messages
for msg in consumer:
    print("Received event:", msg.value)
    event = msg.value
    process_event(event) # Process the event (e.g., send Slack notification, call TF Serving, etc.)
