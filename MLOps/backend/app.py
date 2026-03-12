import sys
from pathlib import Path

# Add MLOps/streaming to Python path so kafka_producer can be imported
sys.path.append(str(Path(__file__).parent))

from fastapi import FastAPI
from api.main import api_router

app = FastAPI(title="Fashion Recommendation API")
app.include_router(api_router)