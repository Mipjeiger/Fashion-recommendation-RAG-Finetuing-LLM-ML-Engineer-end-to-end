from notifications.slack_service import slack
import pandas as pd

def notify_click_from_row(row: pd.Series):
    """
    Notify pull values from a DataFrame row to Slack."""
    slack.notify_product_click(
        item_id=row['item_id'],
        category=row['category'],
        subcategory=row['subcategory'],
        brand=row['brand'],
        price=row['price'],
        click_count=row['click_count']
    )