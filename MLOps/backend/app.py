import sys
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel

# Add MLOps/streaming to Python path so kafka_producer can be imported
sys.path.append(str(Path(__file__).parents[1] / "streaming"))

# Import works correctly after adding to path
from notifications.slack_service import slack
from kafka_producer.producer import send_event

app = FastAPI(
    title='Fashion Recommendation System API',
    description='FastAPI backend + kafka + slack Notifications for fashion recommendation system + Tensorflow serving client',
)