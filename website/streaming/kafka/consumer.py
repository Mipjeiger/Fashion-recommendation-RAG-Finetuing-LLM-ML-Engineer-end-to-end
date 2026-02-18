import json
from kafka import KafkaConsumer

def get_consumer():
    return KafkaConsumer(
        "realtime-recommendation",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8"))
    )