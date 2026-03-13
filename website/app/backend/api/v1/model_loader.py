import sys
from pathlib import Path

# add config & core to Python path so we can import settings and logger
sys.path.append(str(Path(__file__).parents[2]))

import httpx
from config.settings import settings
from core.logging import get_logger

logger = get_logger("services.model_loader")

class ModelLoader:
    """Class to manage ML model loading and inference."""
    async def run_inference(self, payload: dict):

        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    f"{settings.ML_SERVICE_URL}/product/recommend",
                    json=payload
                )
                response.raise_for_status()

                return response.json()
            
        except Exception as e:
            logger.error(f"Error during inference: {e}", exc_info=True)
            raise

# Usage example:
if __name__ == "__main__":
    import asyncio

    model_loader = ModelLoader()
    test_payload = {
        "user_id": "test_user",
        "session_id": "test_session",
        "product_id": "test_product",
        "context": {"device": "mobile", "location": "US"}
    }

    result = asyncio.run(model_loader.run_inference(test_payload))
    print(result)
