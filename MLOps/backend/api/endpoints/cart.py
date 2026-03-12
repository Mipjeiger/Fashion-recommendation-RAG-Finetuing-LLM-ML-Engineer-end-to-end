from fastapi import APIRouter
from streaming.kafka_producer.producer import send_event
from notifications.slack_API.cart_notify import notify_cart

router = APIRouter()

# Creaete cart event endpoint
@router.post("/add")
def add_to_cart(data: dict):
    """
    Simulate adding a product to cart and trigger effects."""

    send_event({
        "event": "add_to_cart",
        "item_id": data.get("item_id"),
    })
    notify_cart(data.get("item_id"))
    return {"status": "success",
            "message": f"Product {data.get('item_id')} added to cart and event sent."}