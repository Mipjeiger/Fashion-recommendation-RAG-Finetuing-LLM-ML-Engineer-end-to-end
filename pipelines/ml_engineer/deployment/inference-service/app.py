from fastapi import FastAPI
from pydantic import BaseModel
import requests
import numpy as np
import time
from prometheus_client import start_http_server

from metrics import (
    REQUEST_COUNT,
    REQUEST_LATENCY,
    OUTPUT_0_MEAN,
    OUTPUT_1_MEAN,
    DRIFT_SCORE
)
from drift import compute_drift

app = FastAPI()

# Service name from docker-compose
TF_SERVING_URL = "http://tensorflow-serving:8501/v1/models/fashion_model:predict"

class InferenceRequest(BaseModel):
    input_1: list

# Create endpoint for inference
@app.on_event("startup")
def startup_event():
    start_http_server(8001) # Prometheus metrics server

@app.post("/predict")
def predict(request: InferenceRequest):

    REQUEST_COUNT.inc()  # Increment request count metric
    start_time = time.time()

    input_array = np.array(request.input_1, dtype=np.float32)

    payload = {
        "instances": input_array.tolist()
    }

    response = requests.post(TF_SERVING_URL, json=payload)
    response.raise_for_status()

    predictions = response.json()["predictions"]

    latency = time.time() - start_time
    REQUEST_LATENCY.observe(latency)  # Observe latency metric

    output_0 = np.array([pred[0] for pred in predictions])
    output_1 = np.array([pred[1] for pred in predictions])

    OUTPUT_0_MEAN.observe(output_0.mean())
    OUTPUT_1_MEAN.observe(output_1.mean())

    drift_score = compute_drift(output_0)
    DRIFT_SCORE.observe(drift_score)

    return {
        "output_0": output_0.tolist(),
        "output_1": output_1.tolist(),
        "latency": latency,
        "drift_score": drift_score
    }