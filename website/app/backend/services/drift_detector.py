"""
Drift detection service for model monitoring.
"""
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database.models import DriftEvent
from config.settings import settings
from core.logging import get_logger

logger = get_logger("drift_detector")


class DriftDetector:
    """Detects data and concept drift."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.reference_distribution: Optional[np.ndarray] = None
    
    def set_reference_distribution(self, embeddings: List[List[float]]) -> None:
        """Set reference distribution for comparison."""
        self.reference_distribution = np.array(embeddings)
        logger.info(f"Reference distribution set with {len(embeddings)} samples")
    
    def calculate_distribution_shift(
        self,
        current_embeddings: List[List[float]],
        method: str = "kl_divergence"
    ) -> float:
        """Calculate distribution shift between reference and current."""
        if self.reference_distribution is None:
            logger.warning("No reference distribution set")
            return 0.0
        
        current = np.array(current_embeddings)
        
        if method == "kl_divergence":
            # Simplified KL divergence calculation
            # In production, use proper statistical tests
            ref_mean = np.mean(self.reference_distribution, axis=0)
            ref_std = np.std(self.reference_distribution, axis=0) + 1e-8
            
            current_mean = np.mean(current, axis=0)
            current_std = np.std(current, axis=0) + 1e-8
            
            # Calculate normalized difference
            mean_diff = np.mean(np.abs(ref_mean - current_mean))
            std_diff = np.mean(np.abs(ref_std - current_std))
            
            drift_score = (mean_diff + std_diff) / 2.0
            
        elif method == "wasserstein":
            # Simplified Wasserstein distance
            ref_mean = np.mean(self.reference_distribution, axis=0)
            current_mean = np.mean(current, axis=0)
            drift_score = np.mean(np.abs(ref_mean - current_mean))
        else:
            drift_score = 0.0
        
        return float(drift_score)
    
    async def detect_drift(
        self,
        current_embeddings: List[List[float]],
        drift_type: str = "data_drift",
        model_version: Optional[str] = None
    ) -> Dict[str, Any]:
        """Detect drift and store event if threshold exceeded."""
        try:
            drift_score = self.calculate_distribution_shift(current_embeddings)
            
            is_drift = drift_score > settings.DRIFT_THRESHOLD
            
            result = {
                "drift_detected": is_drift,
                "drift_score": drift_score,
                "threshold": settings.DRIFT_THRESHOLD,
                "drift_type": drift_type,
                "model_version": model_version,
            }
            
            if is_drift:
                logger.warning(
                    f"Drift detected: score={drift_score:.4f}, threshold={settings.DRIFT_THRESHOLD}"
                )
                
                # Store drift event
                drift_event = DriftEvent(
                    drift_type=drift_type,
                    drift_score=drift_score,
                    threshold=settings.DRIFT_THRESHOLD,
                    model_version=model_version,
                    detected_at=datetime.utcnow(),
                )
                self.db.add(drift_event)
                await self.db.commit()
                
                result["event_id"] = str(drift_event.id)
            
            return result
            
        except Exception as e:
            logger.error(f"Drift detection failed: {e}", exc_info=True)
            await self.db.rollback()
            raise
