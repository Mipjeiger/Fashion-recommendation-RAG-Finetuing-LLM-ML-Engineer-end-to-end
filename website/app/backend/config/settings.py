"""
Configuration settings for IndoCloth Market backend.
"""
from pathlib import Path
from typing import Optional, ClassVar
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parents[3] / ".env"),
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "IndoCloth Market API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="production")

    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8030)

    # Database
    DATABASE_URL: str = Field(...)
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092")
    KAFKA_TOPIC_RECOMMENDATIONS: str = "realtime-recommendations"
    KAFKA_TOPIC_EVENTS: str = "fashion-events"
    KAFKA_CONSUMER_GROUP: str = "indocloth-backend"
    KAFKA_MAX_RETRIES: int = 3
    KAFKA_RETRY_DELAY: int = 1

    # Model & Services
    MODEL_BASE_PATH: Path = Field(
        default=Path(__file__).parent.parent.parent.parent.parent / "MLOps" / "models"
    )
    INFERENCE_SERVICE_URL: str = Field(default="http://localhost:8000/inference")
    ML_SERVICE_URL: str = Field(default="http://localhost:8000")
    MODEL_RELOAD_INTERVAL: int = Field(default=300)

    # Slack
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None)
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None)
    SLACK_CHANNEL_ALERTS: str = "#ml-alerts"
    SLACK_CHANNEL_REPORTS: str = "#business-reports"
    SLACK_CHANNEL_DRIFT: str = "#data-drift"

    # Business Metrics
    METRICS_RETENTION_DAYS: int = 90
    DAILY_REPORT_HOUR: int = 8
    WEEKLY_REPORT_DAY: int = 1

    # Drift
    DRIFT_THRESHOLD: float = 0.15
    DRIFT_CHECK_INTERVAL: int = 3600

    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FORMAT: str = Field(default="json")

    # CORS
    CORS_ORIGINS: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )

    # Security
    SECRET_KEY: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


# Instantiate settings object to be used across the app
settings = Settings()