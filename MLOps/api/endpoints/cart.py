# API/endpoints/cart.py
import os
import pandas as pd
from pathlib import Path
from MLOps.notifications.slack_API.cart_notify import notify_cart_from_row

DATABASE = Path(os.getenv("DATABASE_PATH", "/app/database/data/raw/matched_fashion_dataset.parquet"))

def add_to_cart(item_id: str):
    """
    Simulate adding an item to the cart and notify via Slack."""
    df = pd.read_parquet(DATABASE)
    row = df.loc[df["item_id"] == item_id]

    if row.empty:
        raise ValueError(f"Item ID {item_id} not found in dataset.")
    
    notify_cart_from_row(row.iloc[0])