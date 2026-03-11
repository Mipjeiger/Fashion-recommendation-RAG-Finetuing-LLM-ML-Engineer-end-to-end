from kafka import KafkaProducer
import json
import os

KAFKA_BROKER_URL = os.getenv("KAFKA_BOOTSTRAP_SERVERS")

# init - only create producer once and reuse for all events
_producer = None

def get_producer() -> KafkaProducer:
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BROKER_URL,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer = lambda k: k.encode('utf-8') if k else None
        )
    return _producer

def send_event(topic: str, message: dict, key: str = None) -> None:
    """
    Send event to Kafka topic.
    Args:
        topic (str): Kafka topic name
        message (dict): Event data as a dictionary
        key (str, optional): Optional key for partitioning. Defaults to None.
    """
    try:
        producer = get_producer()
        future = producer.send(topic, value=message, key=key)
        result = future.get(timeout=10)  # Block until send is successful or timeout
        producer.flush()  # Ensure all messages are sent
        print(f"Event sent to topic '{topic}': {message}")
    except Exception as e:
        print(f"Failed to send event to Kafka: {e}")
        raise e