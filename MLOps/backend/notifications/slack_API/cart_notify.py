from notifications.slack_service import slack
import pandas as pd

def notify_cart_from_row(row: pd.Series):
    """
    Notify about pull values from dataset row to Slack channel."""
    slack.notify_add_to_cart(
        item_id = row["item_id"],
        category= row["category"],
        subcategory= row["subcategory"],
        brand= row["brand"],
        price= row["price"]
    )