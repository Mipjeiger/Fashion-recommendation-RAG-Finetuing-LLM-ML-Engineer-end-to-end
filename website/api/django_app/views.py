from django.http import JsonResponse
from streaming.kafka.producer import publish_recommendation
from django.conf import settings
from api.fastapi_app.inference import run_inference

def recommend_view(request):
    """
    Entry point:
    - Receives request from client
    - Calls FastAPI inference endpoint
    - Publishes result to Kafka
    - Returns JSON"""
    
    # Call inference (FastAPI or internal)
    response = request.post(
        settings.FASTAPI_INFERENCE_URL,
        json=request.body.decode("utf-8") if request.body else {}
    ).json()

    # push to kafka
    publish_recommendation(response)

    # Return API response
    return JsonResponse(response, status=200)