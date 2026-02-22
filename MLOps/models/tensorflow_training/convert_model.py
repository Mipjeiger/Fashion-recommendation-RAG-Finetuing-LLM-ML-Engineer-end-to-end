# MLOps/models/tensorflow_training/convert_model.py
import os
import tensorflow as tf
import tf2onnx
from pathlib import Path

# ─────────────────────────────────────────
# Paths
# ─────────────────────────────────────────
BASE_DIR          = Path(__file__).resolve().parent          # MLOps/models/tensorflow_training/
MODEL_RECOMMENDER = BASE_DIR / "fashion_recommendation_model.keras"
ONNX_PATH         = BASE_DIR / "fashion_recommendation_model.onnx"

# ─────────────────────────────────────────
# Load Model
# ─────────────────────────────────────────
print("[Convert] Loading model...")
model = tf.keras.models.load_model(MODEL_RECOMMENDER)
model.summary()

# ─────────────────────────────────────────
# Input Spec
# ─────────────────────────────────────────
spec = (
    tf.TensorSpec(shape=[None, 224, 224, 3], dtype=tf.float32, name="image"),
    tf.TensorSpec(shape=[None, 5],           dtype=tf.float32, name="numeric"),
    tf.TensorSpec(shape=[None, 1],           dtype=tf.int32,   name="category"),
    tf.TensorSpec(shape=[None, 1],           dtype=tf.int32,   name="subcategory"),
    tf.TensorSpec(shape=[None, 1],           dtype=tf.int32,   name="brand"),
    tf.TensorSpec(shape=[None, 1],           dtype=tf.int32,   name="sleeve_type"),
)

# ─────────────────────────────────────────
# Convert to ONNX
# ─────────────────────────────────────────
print("[Convert] Converting to ONNX...")
model_proto, _ = tf2onnx.convert.from_keras(
    model,
    input_signature = spec,
    opset           = 13,
    output_path     = str(ONNX_PATH),
)

print(f"[Convert] ✅ Converted: {ONNX_PATH}")