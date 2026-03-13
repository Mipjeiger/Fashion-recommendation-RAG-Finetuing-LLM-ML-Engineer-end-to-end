"""
Configuration settings for IndoCloth Market backend.
"""
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_env_file() -> str | None:
    current = Path(__file__).resolve()

    # local: website/app/backend/config/settings.py -> parents[3] = website
    try:
        local_env = current.parents[3] / ".env"
        if local_env.exists():
            return str(local_env)
    except IndexError:
        pass

    # docker: rely on docker-compose env/env_file
    return None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_NAME: str = "IndoCloth Market API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8030

    # Security
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    KAFKA_TOPIC_RECOMMENDATIONS: str = "realtime-recommendations"
    KAFKA_TOPIC_EVENTS: str = "fashion-events"
    KAFKA_CONSUMER_GROUP: str = "indocloth-backend"
    KAFKA_MAX_RETRIES: int = 3
    KAFKA_RETRY_DELAY: int = 1

    # Services
    INFERENCE_SERVICE_URL: str = Field(default="http://inference-service:8002/inference", env="INFERENCE_SERVICE_URL")
    ML_SERVICE_URL: str = Field(default="http://inference-service:8000", env="ML_SERVICE_URL")
    MODEL_BASE_PATH: str = Field(default="/app/models", env="MODEL_BASE_PATH")
    MODEL_RELOAD_INTERVAL: int = 300

    # Slack
    SLACK_BOT_TOKEN: Optional[str] = Field(default=None, env="SLACK_BOT_TOKEN")
    SLACK_WEBHOOK_URL: Optional[str] = Field(default=None, env="SLACK_WEBHOOK_URL")
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

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()