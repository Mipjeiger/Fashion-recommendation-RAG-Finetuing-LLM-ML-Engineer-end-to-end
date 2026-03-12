"""
IndoCloth Market - Main FastAPI application // Integrated Website Backend.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import settings
from core.logging import setup_logging, get_logger
from core.middleware import LoggingMiddleware, ExceptionHandlerMiddleware
from api.v1 import router as api_router
from database.connection import init_db, close_db
from services.model_loader import model_loader

# Setup logging
setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting IndoCloth Market API")
    await init_db()
    logger.info("Database initialized")
    await model_loader.load_models() # wait for models loaded
    logger.info("Models loaded")
    
    yield
    
    # Shutdown
    logger.info("Shutting down IndoCloth Market API")
    await close_db() # Close connection database
    logger.info("Database closed")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered fashion recommendation platform",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add middleware
app.add_middleware(ExceptionHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import hashlib

# Include routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

import os

# Mount static files for images
static_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "fashion_images", "dataset_clean")

def serve_stable_random_image(category_dirs: list, image_name: str, static_base: str):
    """Returns a deterministic random image from valid category subdirectories."""
    h_dir = int(hashlib.md5((image_name + "_dir").encode()).hexdigest(), 16)
    chosen_dir = category_dirs[h_dir % len(category_dirs)]
    
    full_dir = os.path.join(static_base, chosen_dir)
    if os.path.exists(full_dir):
        files = sorted([f for f in os.listdir(full_dir) if f.endswith(('.jpg', '.png', '.jpeg'))])
        if files:
            h_file = int(hashlib.md5(image_name.encode()).hexdigest(), 16)
            return FileResponse(os.path.join(full_dir, files[h_file % len(files)]))
            
    return {"error": "Image not found"}

@app.get("/images/tops/{image_name}", tags=["images"])
async def get_tops_image(image_name: str):
    """"Intercept requests to /images/tops/ and map them dynamically."""
    tops_dirs = ["casual_shirts", "formal_shirts", "printed_hoodies", "printed_tshirts", "solid_tshirts"]
    return serve_stable_random_image(tops_dirs, image_name, static_path)

@app.get("/images/bottoms/{image_name}", tags=["images"])
async def get_bottoms_image(image_name: str):
    """"Intercept requests to /images/bottoms/ and map them dynamically."""
    bottoms_dirs = ["formal_pants", "jeans", "men_cargos"]
    return serve_stable_random_image(bottoms_dirs, image_name, static_path)

app.mount("/images", StaticFiles(directory=static_path), name="images")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to IndoCloth Market API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
