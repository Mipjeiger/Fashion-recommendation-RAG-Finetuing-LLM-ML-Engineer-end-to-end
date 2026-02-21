import os
import pandas as pd
import tensorflow as tf
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models" / "tensorflow_training"
MODEL_RECOMMENDER = MODEL_DIR / "fashion_recommendation_model.keras"
MODEL_PRODUCTION = MODEL_DIR / "fashion_recommendation_model_prod.keras"
IMAGE_METADATA    = MODEL_DIR / "image_metadata.pkl"
DATABASE          = BASE_DIR / "database" / "data" / "raw" / "matched_fashion_dataset.parquet"

# Load encoders (fit once, reuse)
cat_encoder = LabelEncoder()
sub_encoder = LabelEncoder()
brand_encoder = LabelEncoder()
sleeve_encoder = LabelEncoder()

# Load data
def load_data():
    df = pd.read_parquet(DATABASE)

    # Encode categorical features
    df["category_enc"] = cat_encoder.fit_transform(df["category"])
    df["subcategory_enc"] = sub_encoder.fit_transform(df["subcategory"])
    df["brand_enc"] = brand_encoder.fit_transform(df["brand"])
    df["sleeve_enc"] = sleeve_encoder.fit_transform(df["sleeve_type"])

    # Numeric features (must match shape (None, 5))
    numeric_cols = ["price", "view_count", "click_count", "purchase_count", "length_cm"]
    X_numeric = df[numeric_cols].values.astype("float32")

    # Categorical inputs features
    X_category = df["category_enc"].values.astype("int32")
    X_subcategory = df["subcategory_enc"].values.astype("int32")
    X_brand = df["brand_enc"].values.astype("int32")
    X_sleeve = df["sleeve_enc"].values.astype("int32")

    # Load image arrays from metadata
    with open(IMAGE_METADATA, "rb") as f:
        metadata = pickle.load(f)

    images = np.array([metadata[p] for p in df["image_path"]], dtype="float32")

    # Tarfet: Compute recommended_score from engagement
    y = (
        df["view_count"] * 0.2 +
        df["click_count"] * 0.3 +
        df["purchase_count"] * 0.5
    ) / df["purchase_count"].max()
    y = y.values.astype("float32")

    return images, X_numeric, X_category, X_subcategory, X_brand, X_sleeve, y

# Train model
def train():
    print("Loading data...")
    images, X_num, X_cat, X_sub, X_brand, X_sleeve, y = load_data()

    # Split
    idx = np.arange(len(y))
    idx_train, idx_val = train_test_split(idx, test_size=0.2, random_state=42)

    def subset(arr, idx): return arr[idx]

    # Define X_train and X_val as dicts for Keras
    X_train = {
        "image": subset(images, idx_train),
        "numeric": subset(X_num, idx_train),
        "category": subset(X_cat, idx_train),
        "subcategory": subset(X_sub, idx_train),
        "brand": subset(X_brand, idx_train),
        "sleeve_type": subset(X_sleeve, idx_train),
    }
    X_val = {
        "image": subset(images, idx_val),
        "numeric": subset(X_num, idx_val),
        "category": subset(X_cat, idx_val),
        "subcategory": subset(X_sub, idx_val),
        "brand": subset(X_brand, idx_val),
        "sleeve_type": subset(X_sleeve, idx_val),
    }
    y_train, y_val = y[idx_train], y[idx_val]

    # Load existing model
    print("Loading model...")
    model = tf.keras.models.load_model(MODEL_RECOMMENDER)
    model.summary()

    # Continue training on fit
    model.fit(
        X_train, y_train,
        epochs=10,
        batch_size=32,
        validation_data=(X_val, y_val),
        callbacks=[
            tf.keras.callbacks.EarlyStopping(patience=3, restore_best_weights=True),
            tf.keras.callbacks.ModelCheckpoint(MODEL_RECOMMENDER, 
                                               save_best_only=True,
                                               monitor="val_loss",
                                               verbose=1)
        ]
    )

    print(f"Production model saved to: {MODEL_PRODUCTION}")