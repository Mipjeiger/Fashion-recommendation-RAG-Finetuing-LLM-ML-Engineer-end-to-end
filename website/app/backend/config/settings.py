"""
Configuration settings for IndoCloth Market backend.
"""
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _get_env_file() -> str | None:
    current = Path(__file__).resolve()

    try:
        local_env = current.parents[3] / ".env"
        if local_env.exists():
            return str(local_env)
    except IndexError:
        pass

    return None


def _is_docker() -> bool:
    return Path("/.dockerenv").exists()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_get_env_file(),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    APP_NAME: str = "IndoCloth Market API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8030

    DATABASE_URL: str = Field(...)
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_RECOMMENDATIONS: str = "realtime-recommendations"
    KAFKA_TOPIC_EVENTS: str = "fashion-events"
    KAFKA_CONSUMER_GROUP: str = "indocloth-backend"
    KAFKA_MAX_RETRIES: int = 3
    KAFKA_RETRY_DELAY: int = 1

    MODEL_BASE_PATH: Path = Path("/app/models")

    # local run -> localhost
    # docker run -> service name
    ML_SERVICE_URL: str = "http://inference-service:8000" if _is_docker() else "http://localhost:8000"
    INFERENCE_SERVICE_URL: str = "http://inference-service:8000" if _is_docker() else "http://localhost:8000"

    MODEL_RELOAD_INTERVAL: int = 300

    SLACK_BOT_TOKEN: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None

    METRICS_RETENTION_DAYS: int = 90
    DAILY_REPORT_HOUR: int = 8
    WEEKLY_REPORT_DAY: int = 1

    DRIFT_THRESHOLD: float = 0.15
    DRIFT_CHECK_INTERVAL: int = 3600

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    SECRET_KEY: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()