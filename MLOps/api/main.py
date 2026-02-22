"""Create a FastAPI backend (calls serving, retrieval, DB)"""
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

# ========================
# Configure logging
# ========================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================
# Load environment variables from .env
# ========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '.env'))

# Ensure the .env is exist
if not os.path.exists(os.path.join(BASE_DIR, '..', '.env')):
    raise FileNotFoundError("The .env is not exist")
else:
    logger.info(".env file loaded successfully")

    