"""
API v1 router.
"""
from fastapi import APIRouter
from api.v1 import models, recommendations, metrics, kafka, slack

router = APIRouter()

router.include_router(models.router, prefix="/models", tags=["models"])
router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])
router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
router.include_router(kafka.router, prefix="/kafka", tags=["kafka"])
router.include_router(slack.router, prefix="/slack", tags=["slack"])
