# MLOps/notifications/slack_API/training_notify.py
from MLOps.notifications.slack_service import slack
import os

MODEL_NAME = os.getenv("MODEL_NAME", "fashion_recommendation_model")

def notify_start(epochs: int):
    slack.notify_training_start(
        model_name = MODEL_NAME,
        epochs     = epochs,
    )

def notify_success(val_loss: float, val_mae: float):
    slack.notify_training_success(
        model_name = MODEL_NAME,
        val_loss   = val_loss,
        val_mae    = val_mae,
    )

def notify_failed(error: Exception):
    slack.notify_training_failed(
        model_name = MODEL_NAME,
        error      = str(error),
    )