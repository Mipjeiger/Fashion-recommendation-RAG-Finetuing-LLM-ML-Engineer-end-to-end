"""Create a SlackService class to send notifications to Slack channels."""
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

ICONS = {
    "success" : "✅",
    "error"   : "❌",
    "warning" : "⚠️",
    "info"    : "ℹ️",
    "start"   : "🚀",
    "cart"    : "🛒",
    "click"   : "👆",
    "revenue" : "💰",
    "learning": "🧠",
}

# Create a SlackService class
class SlackService:
    def __init__(self):
        self.webhook_url = SLACK_WEBHOOK_URL

    def _post(self, blocks: list):
        if not self.webhook_url:
            print("[Slack] SLACK_WEBHOOK_URL not set. Cannot send notification.")
            return
        try:
            response = requests.post(self.webhook_url, json={"blocks": blocks})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"[Slack] Failed to send notification: {e}")


    # ─────────────────────────────────────────
    # 1. ADD TO CART
    # ─────────────────────────────────────────
    def notify_add_to_cart(self, item_id: str, category: str, subcategory: str, brand: str, price: float):
        self._post([
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{ICONS['cart']} Item Added to Cart!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Item ID:*\n{item_id}"},
                    {"type": "mrkdwn", "text": f"*Brand:*\n{brand}"},
                    {"type": "mrkdwn", "text": f"*Category:*\n{category} > {subcategory}"},
                    {"type": "mrkdwn", "text": f"*Price:*\n${price:.2f}"}
                ]
            },
            {"type": "divider"}
        ])
    
    # ─────────────────────────────────────────
    # 2. CLICK PRODUCT
    # ─────────────────────────────────────────
    def notify_product_click(self, item_id: str, category: str, subcategory: str,
                              brand: str, price: int, click_count: int):
        self._post([
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{ICONS['click']} Product Clicked!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Item ID:*\n{item_id}"},
                    {"type": "mrkdwn", "text": f"*Brand:*\n{brand}"},
                    {"type": "mrkdwn", "text": f"*Category:*\n{category} > {subcategory}"},
                    {"type": "mrkdwn", "text": f"*Price:*\nRp {price:,}"},
                    {"type": "mrkdwn", "text": f"*Total Clicks:*\n{click_count:,}"},
                ]

            },
            {"type": "divider"}
        ])
    
    # ─────────────────────────────────────────
    # 3. DAILY REVENUE REPORT
    # ─────────────────────────────────────────
    def notify_daily_revenue(self, total_revenue: int, total_orders: int,
                             top_items: list[dict], date: str = None):
        date = date or datetime.now().strftime("%Y-%m-%d")
        top_text = "\n".join([
            f"{i+1}. '{item['item_id']} - {item['subcategory']} | {item['brand']} | $ {item['revenue']:,}"
            for i, item in enumerate(top_items[:5])
        ])
        self._post([
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{ICONS['revenue']} Daily Revenue Report — {date}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Revenue:*\nRp {total_revenue:,}"},
                    {"type": "mrkdwn", "text": f"*Total Orders:*\n{total_orders:,}"},
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*🏆 Top Products:*\n{top_text}"}
            },
            {"type": "divider"}
        ])

    # ─────────────────────────────────────────
    # 4. WEEKLY REVENUE REPORT
    # ─────────────────────────────────────────
    def notify_weekly_revenue(self, total_revenue: int, total_orders: int,
                               top_items: list[dict], week: str = None):
        week     = week or f"Week {datetime.now().isocalendar()[1]}"
        top_text = "\n".join([
            f"{i+1}. `{item['item_id']}` — {item['subcategory']} | {item['brand']} | Rp {item['revenue']:,}"
            for i, item in enumerate(top_items[:5])
        ])
        self._post([
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{ICONS['revenue']} Weekly Revenue Report — {week}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Revenue:*\nRp {total_revenue:,}"},
                    {"type": "mrkdwn", "text": f"*Total Orders:*\n{total_orders:,}"},
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*🏆 Top Products:*\n{top_text}"}
            },
            {"type": "divider"}
        ])

    # ─────────────────────────────────────────
    # 5. WEEKLY NEW LEARNINGS
    # ─────────────────────────────────────────
    def notify_weekly_learnings(self, learnings: list[dict], week: str = None):
        week            = week or f"Week {datetime.now().isocalendar()[1]}"
        learning_blocks = []
        for i, l in enumerate(learnings[:5]):
            learning_blocks.append({
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*#{i+1} Insight:*\n{l['insight']}"},
                    {"type": "mrkdwn", "text": f"*Item:*\n`{l['item_id']}` — {l['brand']}"},
                    {"type": "mrkdwn", "text": f"*Category:*\n{l['category']} › {l['subcategory']}"},
                    {"type": "mrkdwn", "text": f"*Support:*\n{l.get('support', 'N/A')}  |  *Confidence:* {l.get('confidence', 'N/A')}"},
                ]
            })
            learning_blocks.append({"type": "divider"})

        self._post([
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{ICONS['learning']} Weekly New Learnings — {week}"}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": "Here's what the recommendation engine discovered this week:"}
            },
            {"type": "divider"},
            *learning_blocks
        ])
    # ─────────────────────────────────────────
    # 6. TRAINING START
    # ─────────────────────────────────────────
    def notify_training_start(self, model_name: str, epochs: int):
        self._post([
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{ICONS['start']} Training Started: {model_name}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Model Name:*\n{model_name}"},
                    {"type": "mrkdwn", "text": f"*Epochs:*\n{epochs}"},
                ]
            },
            {"type": "divider"}
        ])
    # ─────────────────────────────────────────
    # 7. TRAINING SUCCESS
    # ─────────────────────────────────────────
    def notify_training_success(self, model_name: str, val_loss: float, val_mae: float):
        self._post([
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{ICONS['success']} Training Succeeded: {model_name}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Model Name:*\n{model_name}"},
                    {"type": "mrkdwn", "text": f"*Validation Loss:*\n{val_loss:.4f}"},
                    {"type": "mrkdwn", "text": f"*Validation MAE:*\n{val_mae:.4f}"},
                ]
            },
            {"type": "divider"}
        ])

    # ─────────────────────────────────────────
    # 8. TRAINING FAILED
    # ─────────────────────────────────────────
    def notify_training_failed(self, model_name: str, error: str):
        self._post([
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"{ICONS['error']} Training Failed: {model_name}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Model Name:*\n{model_name}"},
                    {"type": "mrkdwn", "text": f"*Error:*\n{error}"},
                ]
            },
            {"type": "divider"}
        ])