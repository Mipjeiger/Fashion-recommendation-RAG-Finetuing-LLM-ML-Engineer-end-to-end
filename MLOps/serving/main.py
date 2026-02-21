from fastapi import FastAPI
from model_loader import load_model, predict
from metrics import MODEL_LATENCY
from prometheus_client import start_http_server
import time

app = FastAPI()
model = load_model()

# Start Prometheus metrics server
start_http_server(8001)

@app.post("/predict")
def inference(payload: dict):
    with MODEL_LATENCY.time():
        result = predict(model, payload["features"])
    return {"prediction": result}