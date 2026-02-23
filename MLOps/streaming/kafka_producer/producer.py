from kafka import KafkaProducer
import json

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer = lambda v: json.dumps(v).encode('utf-8')
)

def send_event(data):
    print("Sending event:", data)
    producer.send("fashion-events", value=data)
    producer.flush()  # Ensure the event is sent immediately
    print("Event sent successfully")