"""Create router API endpoints for product-related operations."""
import logging
import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, APIRouter
from api.endpoints.product import router as product_router
from api.endpoints.cart import router as cart_router

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

# Create router and include endpoints
router = APIRouter()

router.include_router(product_router, prefix="/product")
router.include_router(cart_router, prefix="/cart")