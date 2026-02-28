from prometheus_client import Counter, Histogram, Gauge

REQUEST_COUNT = Counter(
    "model_requests_total",
    "Total Inference Requests",
)

REQUEST_LATENCY = Histogram(
    "model_request_latency_seconds",
    "Inference latency in seconds",
)

OUTPUT_0_MEAN = Gauge(
    "model_output_0_mean",
    "Mean of the first output_0",
)

OUTPUT_1_MEAN = Gauge(
    "model_output_1_mean",
    "Mean of the second output_1",
)

DRIFT_SCORE = Gauge(
    "model_input_drift_score",
    "Drift score for model inputs",
)