"""
Model management endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.model_loader import model_loader
from core.logging import get_logger

logger = get_logger("api.models")
router = APIRouter()


@router.get("/")
async def get_models():
    """Get model metadata."""
    try:
        # Check if reload is needed
        if await model_loader.should_reload():
            await model_loader.load_models()
        
        metadata = await model_loader.get_model_metadata()
        return {"status": "success", "data": metadata}
    except Exception as e:
        logger.error(f"Failed to get models: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.post("/reload")
async def reload_models():
    """Force reload models."""
    try:
        await model_loader.load_models()
        return {"status": "success", "message": "Models reloaded"}
    except Exception as e:
        logger.error(f"Failed to reload models: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
