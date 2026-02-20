"""
Model loading and management service.
"""
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import httpx

from config.settings import settings
from core.logging import get_logger
from core.exceptions import ModelLoadError, InferenceError

logger = get_logger("model_loader")


class ModelLoader:
    """Manages model loading and inference."""
    
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.model_metadata: Dict[str, Dict[str, Any]] = {}
        self.last_reload: Optional[datetime] = None
        self._lock = asyncio.Lock()
    
    async def load_models(self) -> None:
        """Load models from MLOps/models directory."""
        async with self._lock:
            try:
                model_path = Path(settings.MODEL_BASE_PATH)
                
                if not model_path.exists():
                    logger.warning(f"Model directory not found: {model_path}")
                    return
                
                # Scan for model files
                model_files = list(model_path.glob("*.keras")) + list(model_path.glob("*.pkl"))
                
                if not model_files:
                    logger.warning(f"No model files found in {model_path}")
                    return
                
                logger.info(f"Found {len(model_files)} model files")
                
                # Store model metadata
                for model_file in model_files:
                    model_name = model_file.stem
                    self.model_metadata[model_name] = {
                        "path": str(model_file),
                        "size": model_file.stat().st_size,
                        "modified": datetime.fromtimestamp(model_file.stat().st_mtime),
                        "loaded": False,
                    }
                    logger.info(f"Registered model: {model_name}")
                
                self.last_reload = datetime.utcnow()
                logger.info("Model loading completed")
                
            except Exception as e:
                logger.error(f"Failed to load models: {e}", exc_info=True)
                raise ModelLoadError(f"Model loading failed: {e}")
    
    async def get_model_metadata(self) -> Dict[str, Any]:
        """Get metadata for all models."""
        return {
            "models": self.model_metadata,
            "last_reload": self.last_reload.isoformat() if self.last_reload else None,
            "model_path": str(settings.MODEL_BASE_PATH),
        }
    
    async def should_reload(self) -> bool:
        """Check if models should be reloaded."""
        if not self.last_reload:
            return True
        
        elapsed = (datetime.utcnow() - self.last_reload).total_seconds()
        return elapsed >= settings.MODEL_RELOAD_INTERVAL
    
    async def run_inference(
        self,
        payload: Dict[str, Any],
        timeout: float = 30.0
    ) -> Dict[str, Any]:
        """Run inference using the inference service."""
        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    settings.INFERENCE_SERVICE_URL,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.TimeoutException:
            logger.error("Inference service timeout")
            raise InferenceError("Inference service timeout")
        except httpx.HTTPStatusError as e:
            logger.error(f"Inference service error: {e}")
            raise InferenceError(f"Inference service error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Inference failed: {e}", exc_info=True)
            raise InferenceError(f"Inference failed: {e}")


# Global model loader instance
model_loader = ModelLoader()
