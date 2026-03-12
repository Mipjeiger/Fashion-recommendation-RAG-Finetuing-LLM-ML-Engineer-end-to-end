from notifications.slack_service.slack import send_slack_message
import pandas as pd

def notify_product_view(row: pd.Series):
    """
    Notify pull values from a DataFrame row to Slack."""
    send_slack_message(
        item_id=row['item_id'],
        category=row['category'],
        subcategory=row['subcategory'],
        brand=row['brand'],
        price=row['price'],
        click_count=row['click_count']
    )