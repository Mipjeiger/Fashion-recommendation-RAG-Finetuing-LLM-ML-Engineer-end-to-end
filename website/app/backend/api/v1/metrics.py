"""
Business metrics endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from database.connection import get_db
from business_logic.metrics import BusinessMetricsService
from core.logging import get_logger

logger = get_logger("api.metrics")
router = APIRouter()


@router.get("/kpi")
async def get_kpi_summary(db: AsyncSession = Depends(get_db)):
    """Get KPI summary."""
    try:
        service = BusinessMetricsService(db)
        kpi = await service.get_kpi_summary()
        return {"status": "success", "data": kpi}
    except Exception as e:
        logger.error(f"Failed to get KPI: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.post("/daily")
async def calculate_daily_metrics(
    date: str = None,
    db: AsyncSession = Depends(get_db)
):
    """Calculate daily metrics."""
    try:
        service = BusinessMetricsService(db)
        target_date = datetime.fromisoformat(date) if date else None
        metrics = await service.calculate_daily_metrics(target_date)
        return {"status": "success", "data": metrics}
    except Exception as e:
        logger.error(f"Failed to calculate daily metrics: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@router.post("/weekly")
async def calculate_weekly_insights(db: AsyncSession = Depends(get_db)):
    """Calculate weekly insights."""
    try:
        service = BusinessMetricsService(db)
        insights = await service.calculate_weekly_insights()
        return {"status": "success", "data": insights}
    except Exception as e:
        logger.error(f"Failed to calculate weekly insights: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}
