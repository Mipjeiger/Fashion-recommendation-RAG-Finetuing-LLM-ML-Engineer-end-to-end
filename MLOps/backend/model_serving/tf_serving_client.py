import requests
import os
import numpy as np
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parents[2] / '.env')

# Configuration for TF Serving
TF_SERVING_HOST = os.getenv("TF_SERVING_HOST")
TF_SERVING_PORT = os.getenv("TF_SERVING_PORT")
TF_SERVING_MODEL_NAME = os.getenv("TF_SERVING_MODEL_NAME")

# Configuration -> docker-compose command config file
TF_SERVING_URL = f"http://{TF_SERVING_HOST}:{TF_SERVING_PORT}/v1/models/{TF_SERVING_MODEL_NAME}:predict"
TF_HEALTH_URL = f"http://{TF_SERVING_HOST}:{TF_SERVING_PORT}/v1/models/{TF_SERVING_MODEL_NAME}"

print(f"TF Serving URL: {TF_SERVING_URL}")
print(f"TF Health URL: {TF_HEALTH_URL}")
print(f"TF Serving Host: {TF_SERVING_HOST}")

# --- Encoding maps must match your training preprocessing ---
CATEGORY_MAP = {"tops": 0, "bottoms": 1}
BRAND_MAP = {"ZARA": 0, "H&M": 1, "Tommy Hilfiger": 2}

# Create function to preprocess input data
def preprocess(item: dict) -> list[float]:
    """Convert raw item data into the format expected by the model."""
    return [
        float(CATEGORY_MAP.get(item["category"], -1)),
        float(BRAND_MAP.get(item["brand"], -1)),
        float(item["price"]),
        float(item["view_count"]),
        float(item["purchase_count"]),
        float(item["stocks"])
    ]

# Create function to check health of TF Serving
def health_check() -> bool:
    """Check the health of the TF Serving model."""
    try:
        response = requests.get(TF_HEALTH_URL, timeout=5)
        if response.status_code == 200:
            model_status = response.json()
            state = model_status.get("model_version_status", [{}])[0].get("state", "UNKNOWN")
            print(f"Model state: {state}")
            return True
        else:
            print(f"Health check failed with status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"""
❌ TF Serving not reachable at {TF_SERVING_HOST}:{TF_SERVING_PORT}

Fix options:
  1. Start Docker stack:
     cd pipelines/ml_engineer/deployment/monitoring
     docker-compose up tensorflow-serving

  2. Override host for local testing:
     export TF_SERVING_HOST=localhost

  3. Check docker-compose ports:
     ports:
       - "8501:8501"   ← host:container mapped ✅
        """)
        return False
    

# Create function to send prediction request to TF Serving
def get_predictions(data: dict) -> dict:
    """
Send a prediction request to TF Serving and return the response."""
    # if not health_check():
    #     raise ConnectionError(
    #         f"TF serving is not healthy at {TF_SERVING_HOST}:{TF_SERVING_PORT}. Please check the connection and try again."
    #     )
    
    # Check model metadata to see expected inputs
    metadata_url = f"http://{TF_SERVING_HOST}:{TF_SERVING_PORT}/v1/models/{TF_SERVING_MODEL_NAME}/metadata"
    try:
        meta_resp = requests.get(metadata_url)
        if meta_resp.status_code == 200:
            print("Model Metadata:", meta_resp.json())
    except Exception as e:
        print(f"Could not fetch metadata: {e}")

    # Preprocess the input data
    instances = [preprocess(item) for item in data["instances"]]
    
    # The model expects shape (-1, 30, 4)
    # Each instance currently has 6 features. We need to:
    # 1. Select the correct 4 features (assuming the first 4 for now, but need to verify)
    # 2. Pad or repeat to reach sequence length 30
    
    processed_instances = []
    for inst in instances:
        features = inst[:4]
        sequence = [features] * 30
        processed_instances.append(sequence)

    payload = {"instances": processed_instances}
    print(f"Sending payload to TF Serving: {payload}")

    response = requests.post(TF_SERVING_URL, json=payload, timeout=30)
    if response.status_code != 200:
        print(f"Error Response Body: {response.text}")
    response.raise_for_status()  # Raise an error for bad responses
    result = response.json()
    print(f"Received response from TF Serving: {result}")
    return result


# Example usage
if __name__ == "__main__":
    sample_data = {
        "instances": [{
            "item_id": "item_000001",
            "category": "tops",
            "brand": "ZARA",
            "price": 284314,
            "view_count": 100,
            "purchase_count": 10,
            "stocks": 20
        }]
    }

    print(f"\n{'='*55}")
    print(f"  TF Serving Client Test")
    print(f"  Host  : {TF_SERVING_HOST}:{TF_SERVING_PORT}")
    print(f"  Model : {TF_SERVING_MODEL_NAME}")
    print(f"{'='*55}\n")

    predictions = get_predictions(sample_data)
    print("✅ Predictions:", predictions)