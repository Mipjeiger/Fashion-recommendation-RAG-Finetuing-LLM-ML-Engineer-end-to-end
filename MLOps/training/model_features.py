"""Load models to know features used in training and ensure with dataset exists"""
import os
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
import pickle
from pathlib import Path

# Create BASE_DIR and MODEL_PATH
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL_EMBEDDING = MODEL_DIR / "tensorflow_training" / "fashion_embedding_model.keras"
MODEL_RECOMMENDER = MODEL_DIR / "tensorflow_training" / "fashion_recommendation_model.keras"
IMAGE_METADATA = MODEL_DIR / "tensorflow_training" / "image_metadata.pkl"
DATABASE = BASE_DIR / "database" / "data" / "raw" / "matched_fashion_dataset.parquet"

# Create function to load data
def load_data():
    df = pd.read_parquet(DATABASE)
    df.head()
    return df

# Create function to load models
def load_models():
    embedding_model = tf.keras.models.load_model(MODEL_EMBEDDING)
    recommender_model = tf.keras.models.load_model(MODEL_RECOMMENDER)
    return embedding_model, recommender_model


# Usage
df = load_data()
embedding_model, recommender_model = load_models()

# ---- Dataset features ----
print("== Dataset Features ==")
print(f"Dataset shape: {df.shape}")
print(f"Dataset columns: {df.columns.tolist()}")
print(f"Dataset types:\n{df.dtypes}")

# ---- Embedding model ----
print("\n== Embedding Model ==")
embedding_model.summary()
print(f"Input embedding model shape: {embedding_model.input_shape}")
print(f"Output embedding model shape: {embedding_model.output_shape}")

# ---- Recommender model ----
print("\n== Recommender Model ==")
recommender_model.summary()
print(f"Input recommender model shape: {recommender_model.input_shape}")
print(f"Output recommender model shape: {recommender_model.output_shape}")

# ---- Load image metadata ----
print("\n== Image Metadata ==")
with open(IMAGE_METADATA, "rb") as f:
    image_metadata = pickle.load(f)


print("\n== Image Metadata ==")
print(type(image_metadata))
if isinstance(image_metadata, dict):
    print(f"Keys: {list(image_metadata.keys())}")
elif isinstance(image_metadata, pd.DataFrame):
    print(f"Columns: {image_metadata.columns.tolist()}")