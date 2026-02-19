from fastapi import FastAPI
from api.fastapi_app.inference import run_inference

app = FastAPI(title="MLOps Inference API")

@app.post("/inference")
async def inference(payload: dict):
    """
    Production inference endpoint"""
    return run_inference(payload), 200

@app.get("/health")
def health_check():
    return {"status": "ok"}, 200