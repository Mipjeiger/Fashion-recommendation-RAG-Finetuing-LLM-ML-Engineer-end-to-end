import tensorflow as tf
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "tensorflow_training", "fashion_recommendation_model.keras")

def load_model():
    return tf.keras.models.load_model(MODEL_PATH)

def predict(model, features):
    prediction = model.predict([features])
    return prediction.tolist()