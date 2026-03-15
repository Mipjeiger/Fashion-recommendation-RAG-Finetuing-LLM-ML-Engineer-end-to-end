import asyncio
import os
import hashlib
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.exc import OperationalError
import uvicorn

from config.settings import settings
from core.logging import setup_logging, get_logger
from core.middleware import LoggingMiddleware, ExceptionHandlerMiddleware
from api.v1 import router as api_router
from database.connection import init_db, close_db
from services.model_loader import model_loader

setup_logging()
logger = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting IndoCloth Market API")

    # Retry DB connection on startup with exponential backoff
    max_retries = 10
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            await init_db()
            logger.info("✅ Database initialized successfully")
            break
        except OperationalError as e:
            if attempt < max_retries - 1:
                wait_time = retry_delay * (2 ** attempt)
                logger.warning(f"⚠️  Database connection attempt {attempt + 1}/{max_retries} failed. Retrying in {wait_time}s... Error: {str(e)[:100]}")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"❌ Failed to connect to database after {max_retries} attempts")
                raise

    await model_loader.load_models()
    logger.info("✅ Models loaded successfully")

    yield

    # Shutdown
    logger.info("Shutting down IndoCloth Market API")
    await close_db()
    logger.info("✅ Database closed")


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

# Include routers
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


# ─── Static Files Configuration ───────────────────────────────
STATIC_IMAGES_DIR = os.getenv("STATIC_IMAGES_DIR", "/app/fashion_images/dataset_clean")

def serve_stable_random_image(category_dirs: list, image_name: str, static_base: str):
    """Returns a deterministic random image from valid category subdirectories."""
    if not Path(static_base).exists():
        return {"error": "Image directory not found"}

    h_dir = int(hashlib.md5((image_name + "_dir").encode()).hexdigest(), 16)
    chosen_dir = category_dirs[h_dir % len(category_dirs)]

    full_dir = os.path.join(static_base, chosen_dir)
    if os.path.exists(full_dir):
        images = [f for f in os.listdir(full_dir) if f.endswith(('.jpg', '.png', '.jpeg'))]
        if images:
            h_img = int(hashlib.md5(image_name.encode()).hexdigest(), 16)
            selected_image = images[h_img % len(images)]
            return FileResponse(os.path.join(full_dir, selected_image))

    return {"error": "Image not found"}


@app.get("/images/tops/{image_name}", tags=["images"])
async def get_tops_image(image_name: str):
    category_dirs = [d for d in os.listdir(STATIC_IMAGES_DIR) if os.path.isdir(os.path.join(STATIC_IMAGES_DIR, d)) and 'top' in d.lower()]
    return serve_stable_random_image(category_dirs, image_name, STATIC_IMAGES_DIR)


@app.get("/images/bottoms/{image_name}", tags=["images"])
async def get_bottoms_image(image_name: str):
    category_dirs = [d for d in os.listdir(STATIC_IMAGES_DIR) if os.path.isdir(os.path.join(STATIC_IMAGES_DIR, d)) and 'bottom' in d.lower()]
    return serve_stable_random_image(category_dirs, image_name, STATIC_IMAGES_DIR)


# Mount static files
if Path(STATIC_IMAGES_DIR).exists():
    app.mount("/images", StaticFiles(directory=STATIC_IMAGES_DIR), name="images")
    logger.info(f"✅ Mounted static images from: {STATIC_IMAGES_DIR}")
else:
    logger.warning(f"⚠️  Static images directory not found: {STATIC_IMAGES_DIR}")


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "IndoCloth Market API"}


@app.get("/")
async def root():
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )