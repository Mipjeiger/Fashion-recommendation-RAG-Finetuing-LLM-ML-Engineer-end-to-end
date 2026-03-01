"""
Configuration settings for IndoCloth Market backend.
"""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # App
    APP_NAME: str = "IndoCloth Market API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False, env="DEBUG")
    ENVIRONMENT: str = Field(default="production", env="ENVIRONMENT")
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database (required - must come from environment)
    DATABASE_URL: str = Field(
        ...,
        env="DATABASE_URL",
    )
    DB_POOL_SIZE: int = Field(default=10, env="DB_POOL_SIZE")
    DB_MAX_OVERFLOW: int = Field(default=20, env="DB_MAX_OVERFLOW")
    
    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(
        default="localhost:9092",
        env="KAFKA_BOOTSTRAP_SERVERS"
    )
    KAFKA_TOPIC_RECOMMENDATIONS: str = "realtime-recommendations"
    KAFKA_TOPIC_EVENTS: str = "fashion-events"
    KAFKA_CONSUMER_GROUP: str = "indocloth-backend"
    KAFKA_MAX_RETRIES: int = 3
    KAFKA_RETRY_DELAY: int = 1
    
    # Model
    MODEL_BASE_PATH: Path = Field(
        default=Path(__file__).parent.parent.parent.parent.parent / "MLOps" / "models",
        env="MODEL_BASE_PATH"
    )
    INFERENCE_SERVICE_URL: str = Field(
        default="http://localhost:8002/inference",
        env="INFERENCE_SERVICE_URL"
    )
    MODEL_RELOAD_INTERVAL: int = Field(default=300, env="MODEL_RELOAD_INTERVAL")  # 5 minutes
    
    # Slack
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
    SLACK_CHANNEL_ALERTS: str = "#ml-alerts"
    SLACK_CHANNEL_REPORTS: str = "#business-reports"
    SLACK_CHANNEL_DRIFT: str = "#data-drift"
    
    # Business Metrics
    METRICS_RETENTION_DAYS: int = 90
    DAILY_REPORT_HOUR: int = 8  # 8 AM UTC
    WEEKLY_REPORT_DAY: int = 1  # Monday
    
    # Drift Detection
    DRIFT_THRESHOLD: float = 0.15  # 15% distribution shift
    DRIFT_CHECK_INTERVAL: int = 3600  # 1 hour
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    LOG_FORMAT: str = "json"  # json or text
    
    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        env="CORS_ORIGINS"
    )
    
    # Security (required - must come from environment)
    SECRET_KEY: str = Field(
        ...,
        env="SECRET_KEY",
    )
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        # Load environment variables from website/.env so all app services
        # can share a single configuration file.
        env_file = str(Path(__file__).resolve().parents[3] / ".env")
        case_sensitive = True
        # Ignore extra env vars (e.g. old Django/Airflow settings) instead of failing.
        extra = "ignore"


settings = Settings()
