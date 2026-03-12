import requests
from config.settings import settings

def request_recommendation(payload):
    url = f"{settings.ML_SERVICE_URL}/product/recommend"
    response = requests.post(url, json=payload, timeout=5)
    response.raise_for_status()
    return response.json()