import os
import pickle
import sys
import numpy as np
import pandas as pd
import tensorflow as tf
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from MLOps.notifications.slack_API.training_notify import (
    notify_start,
    notify_success,
    notify_failed,
)

# ─────────────────────────────────────────
# Paths from .env
# ─────────────────────────────────────────
BASE_DIR = Path(os.getenv("BASE_DIR", PROJECT_ROOT / "MLOps"))

MODEL_DIR         = BASE_DIR / "models" / "tensorflow_training"
MODEL_RECOMMENDER = MODEL_DIR / "fashion_recommendation_model.keras"
MODEL_PRODUCTION  = MODEL_DIR / "fashion_recommendation_model_prod.keras"
IMAGE_METADATA    = MODEL_DIR / "image_metadata.pkl"

DATABASE = BASE_DIR / "database" / "data" / "raw" / "matched_fashion_dataset.parquet"

EPOCHS     = int(os.getenv("TRAIN_EPOCHS", 10))
BATCH_SIZE = int(os.getenv("TRAIN_BATCH_SIZE", 32))

# Safety check
if not DATABASE.exists():
    raise FileNotFoundError(f"Dataset not found at: {DATABASE}")

# ─────────────────────────────────────────
# Encoders
# ─────────────────────────────────────────
cat_encoder    = LabelEncoder()
sub_encoder    = LabelEncoder()
brand_encoder  = LabelEncoder()
sleeve_encoder = LabelEncoder()

# ─────────────────────────────────────────
# Load Data
# ─────────────────────────────────────────
def load_data():
    print("[Data] Loading dataset...")
    df = pd.read_parquet(DATABASE)
    print(f"[Data] Shape: {df.shape}")

    # Encode categoricals
    df["category_enc"]    = cat_encoder.fit_transform(df["category"])
    df["subcategory_enc"] = sub_encoder.fit_transform(df["subcategory"])
    df["brand_enc"]       = brand_encoder.fit_transform(df["brand"])
    df["sleeve_enc"]      = sleeve_encoder.fit_transform(df["sleeve_type"])

    # Numeric features → matches model input (None, 5)
    numeric_cols  = ["price", "view_count", "click_count", "purchase_count", "length_cm"]
    X_numeric     = df[numeric_cols].values.astype("float32")
    X_category    = df["category_enc"].values.astype("int32")
    X_subcategory = df["subcategory_enc"].values.astype("int32")
    X_brand       = df["brand_enc"].values.astype("int32")
    X_sleeve      = df["sleeve_enc"].values.astype("int32")

    # Load images from metadata
    print("[Data] Loading image metadata...")
    with open(IMAGE_METADATA, "rb") as f:
        metadata = pickle.load(f)
    images = np.array([metadata[p] for p in df["image_path"]], dtype="float32")

    # Target: recommended_score derived from engagement
    y = (
        df["view_count"]     * 0.2 +
        df["click_count"]    * 0.3 +
        df["purchase_count"] * 0.5
    ) / df["purchase_count"].max()
    y = y.values.astype("float32")

    print("[Data] Done loading.")
    return images, X_numeric, X_category, X_subcategory, X_brand, X_sleeve, y


# ─────────────────────────────────────────
# Prepare Inputs
# ─────────────────────────────────────────
def prepare_inputs(images, X_num, X_cat, X_sub, X_brand, X_sleeve, idx):
    return {
        "image"      : images[idx],
        "numeric"    : X_num[idx],
        "category"   : X_cat[idx],
        "subcategory": X_sub[idx],
        "brand"      : X_brand[idx],
        "sleeve_type": X_sleeve[idx],
    }


# ─────────────────────────────────────────
# Train
# ─────────────────────────────────────────
def train():
    notify_start(epochs=EPOCHS)

    try:
        # Load
        images, X_num, X_cat, X_sub, X_brand, X_sleeve, y = load_data()

        # Split
        idx                = np.arange(len(y))
        idx_train, idx_val = train_test_split(idx, test_size=0.2, random_state=42)

        X_train = prepare_inputs(images, X_num, X_cat, X_sub, X_brand, X_sleeve, idx_train)
        X_val   = prepare_inputs(images, X_num, X_cat, X_sub, X_brand, X_sleeve, idx_val)
        y_train = y[idx_train]
        y_val   = y[idx_val]

        # Load existing model
        print("[Model] Loading model...")
        model = tf.keras.models.load_model(MODEL_RECOMMENDER)
        model.summary()

        # Train
        print("[Model] Training started...")
        history = model.fit(
            X_train, y_train,
            epochs          = EPOCHS,
            batch_size      = BATCH_SIZE,
            validation_data = (X_val, y_val),
            callbacks       = [
                tf.keras.callbacks.EarlyStopping(
                    patience             = 3,
                    restore_best_weights = True,
                    monitor              = "val_loss",
                ),
                tf.keras.callbacks.ModelCheckpoint(
                    MODEL_PRODUCTION,
                    save_best_only = True,
                    monitor        = "val_loss",
                    verbose        = 1,
                ),
            ]
        )

        # Best metrics
        val_loss = min(history.history["val_loss"])
        val_mae  = min(history.history["val_mae"])

        print(f"[Model] Training complete — val_loss: {val_loss:.4f} | val_mae: {val_mae:.4f}")
        print(f"[Model] Production model saved at: {MODEL_PRODUCTION}")

        notify_success(val_loss=val_loss, val_mae=val_mae)

    except Exception as e:
        print(f"[Model] Training failed: {e}")
        notify_failed(error=e)
        raise


if __name__ == "__main__":
    train()

    
"""
**Flow inside this file:**
```
train()
   │
   ├── notify_start()          ← Slack: "Training started"
   │
   ├── load_data()             ← parquet → encode → images → y
   │       │
   │       └── prepare_inputs()  ← dict with 6 named inputs for model
   │
   ├── load_model()            ← loads existing .keras (not build new)
   │
   ├── model.fit()
   │       ├── EarlyStopping   ← stops if val_loss not improving
   │       └── ModelCheckpoint ← saves best to _prod.keras
   │
   ├── notify_success()        ← Slack: "val_loss: 0.02 | val_mae: 0.01"
   │
   └── notify_failed()         ← Slack: only if exception raised
"""