# API/endpoints/product.py
import os
import pandas as pd
from pathlib import Path
from MLOps.notifications.slack_API.product_notify import notify_click_from_row

DATABASE = Path(os.getenv("DATABASE_PATH", "/app/database/data/raw/matched_fashion_dataset.parquet"))

def click_product(item_id: str):
    """
    Simulate clicking on a product and notify via Slack."""
    df = pd.read_parquet(DATABASE)
    row = df.loc[df["item_id"] == item_id]

    if row.empty:
        raise ValueError(f"Item ID {item_id} not found in dataset.")
    
    notify_click_from_row(row.iloc[0])