"""
Kafka endpoints.
"""
from fastapi import APIRouter

from kafka_client.consumer import kafka_consumer
from core.logging import get_logger

logger = get_logger("api.kafka")
router = APIRouter()


@router.get("/health")
async def kafka_health():
    """Check Kafka consumer health."""
    try:
        health = await kafka_consumer.health_check()
        return {"status": "success", "data": health}
    except Exception as e:
        logger.error(f"Kafka health check failed: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
