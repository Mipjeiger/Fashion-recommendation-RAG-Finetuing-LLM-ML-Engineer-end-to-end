import requests

TF_serving_url = "http://tensorflow-serving:8501/v1/models/fashion_model:predict"

# create function to send data to TF Serving and get predictions
def get_predictions(data):
    try:
        payload = requests.post(TF_serving_url, json=data)
        payload.raise_for_status()
        return payload.json()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to TF Serving: {e}")
        raise e
    
# Example usage
if __name__ == "__main__":
    sample_data = {
        "instances": [
            {
                "item_id": "item_000001",
                "category": "dress",
                "brand": "brand_a",
                "season": "summer",
                "price": 49.99,
                "view_count": 150,
                "purchase_count": 10,
                "stocks": 20
            }
        ]
    }
    predictions = get_predictions(sample_data)
    print("Predictions from TF Serving:", predictions)