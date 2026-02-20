"""
Recommendation endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from database.connection import get_db
from database.models import RecommendationLog, EventLog
from services.model_loader import model_loader
from kafka_client.producer import kafka_producer
from core.logging import get_logger
import uuid

logger = get_logger("api.recommendations")
router = APIRouter()


class RecommendationRequest(BaseModel):
    """Request model for recommendations."""
    user_id: str = "anonymous"
    session_id: str = None
    product_id: str = None
    context: Dict[str, Any] = {}


@router.post("/recommend")
async def get_recommendations(
    request: RecommendationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Get product recommendations."""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Prepare inference payload
        inference_payload = {
            "user_id": request.user_id,
            "session_id": session_id,
            "product_id": request.product_id,
            "context": request.context,
        }
        
        # Run inference
        inference_result = await model_loader.run_inference(inference_payload)
        
        # Log recommendation
        recommendation_log = RecommendationLog(
            user_id=request.user_id,
            session_id=session_id,
            product_id=request.product_id or inference_result.get("recommended_product_id"),
            recommendation_score=inference_result.get("models", {}).get("tensorflow_recommender", {}).get("intent_score", 0.0),
            model_version=inference_result.get("model_version", "unknown"),
        )
        db.add(recommendation_log)
        
        # Log event
        event_log = EventLog(
            event_type="recommendation_requested",
            user_id=request.user_id,
            session_id=session_id,
            event_data={
                "product_id": request.product_id,
                "inference_result": inference_result,
            }
        )
        db.add(event_log)
        
        await db.commit()
        
        # Publish to Kafka
        kafka_event = {
            "event_type": "recommendation",
            "user_id": request.user_id,
            "session_id": session_id,
            "recommendations": inference_result,
            "timestamp": inference_result.get("system_metadata", {}).get("timestamp"),
        }
        await kafka_producer.publish_recommendation(kafka_event)
        
        return {
            "status": "success",
            "session_id": session_id,
            "recommendations": inference_result,
        }
        
    except Exception as e:
        logger.error(f"Recommendation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/click")
async def log_click(
    recommendation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Log recommendation click."""
    try:
        stmt = select(RecommendationLog).where(RecommendationLog.id == recommendation_id)
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        
        if log:
            log.clicked = True
            await db.commit()
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="Recommendation not found")
            
    except Exception as e:
        logger.error(f"Failed to log click: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/purchase")
async def log_purchase(
    recommendation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Log recommendation purchase."""
    try:
        stmt = select(RecommendationLog).where(RecommendationLog.id == recommendation_id)
        result = await db.execute(stmt)
        log = result.scalar_one_or_none()
        
        if log:
            log.purchased = True
            await db.commit()
            return {"status": "success"}
        else:
            raise HTTPException(status_code=404, detail="Recommendation not found")
            
    except Exception as e:
        logger.error(f"Failed to log purchase: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
