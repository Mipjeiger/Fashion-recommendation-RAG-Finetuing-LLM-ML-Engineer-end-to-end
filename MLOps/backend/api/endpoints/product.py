import sys
from pathlib import Path

# add MLOps/streaming to Python path so kafka_producer can be imported
sys.path.append(str(Path(__file__).parents[2]))

# API/endpoints/product.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from streaming.kafka_producer.producer import send_event
from notifications.slack_API.product_notify import notify_product_view
from model_serving.tf_serving_client import get_predictions

router = APIRouter()

# ---- Request Schema ----
class ProductRequest(BaseModel):
    item_id: str
    category: str
    subcategory: str
    brand: str
    price: float
    view_count: Optional[int] = 0
    purchase_count: Optional[int] = 0
    stocks: Optional[int] = 0

# List of keys we want to extract for the event
EVENT_FIELDS = ["item_id", "category", "subcategory", "brand", "price"]

# --- Endpoint to simulate product view and trigger recommendation ---
@router.post("/recommend")
def recommend_product(data: ProductRequest):
    """
    Simulate a product view and return recommendation.
    1. Get prediction from TF Serving
    2. Send Kafka event
    3. Notify Slack
    """
    try:
        payload = {"instances": [data.model_dump()]}  # Convert Pydantic model to dict and wrap in "instances"
        result = get_predictions(payload)
        prediction = result.get("predictions", [])

        if not prediction:
            return {
               "status": "⚠️ no predictions",
                "count":  0
            }

        # Loop: Extract data and trigger side effects
        for item in prediction:
            event_payload = {field: item.get(field) for field in EVENT_FIELDS}
            event_payload["event"] = "product_view"

            send_event(topic="fashion-events",
                       message=event_payload)

            # Notify slack with the product view details
            notify_product_view(
                item_id = item.get("item_id"),
                category = item.get("category"),
                subcategory = item.get("subcategory"),
                brand = item.get("brand"),
                price = item.get("price"),
                view_count = item.get("view_count", 0),
                click_count = item.get("click_count", 0)
            )

        return {"status": "success",
                "count": len(prediction)}
    
    except ConnectionError as e:
        return {"status": "TF serving unreachable", "error": str(e)}
    except Exception as e:
        return {"status": "error", "error": str(e)}