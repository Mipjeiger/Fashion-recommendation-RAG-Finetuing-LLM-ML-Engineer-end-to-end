from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app=app)

TF_SERVING_URL = "http://localhost:8501"

# Create endpoint
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    res = requests.post(f"{TF_SERVING_URL}/v1/models/fashion_model:predict", json=data)
    return jsonify(res.json())

@app.route('/status', methods=['GET'])
def status():
    res = requests.get(f"{TF_SERVING_URL}/v1/models/fashion_model")
    return jsonify(res.json())


# Usage
if __name__ == '__main__':
    app.run(port=5015)