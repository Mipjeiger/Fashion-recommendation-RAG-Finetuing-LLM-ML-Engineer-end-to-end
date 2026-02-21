from prometheus_client import Histogram

MODEL_LATENCY = Histogram(
    "model_inference_latency_seconds",
    "Model inference latency"
)