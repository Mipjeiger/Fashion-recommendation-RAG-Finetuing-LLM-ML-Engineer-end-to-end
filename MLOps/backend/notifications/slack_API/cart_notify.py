from notifications.slack_service.slack import send_slack_message
import pandas as pd

def notify_cart(row: pd.Series):
    """
    Notify about pull values from dataset row to Slack channel."""
    send_slack_message(
        item_id = row["item_id"],
        category= row["category"],
        subcategory= row["subcategory"],
        brand= row["brand"],
        price= row["price"]
    )