import os
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from pathlib import Path

# Create BASE_DIR and MODEL_PATH
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL = MODEL_DIR / "fashion_recommender_model.keras"

# Create function to load data
def 