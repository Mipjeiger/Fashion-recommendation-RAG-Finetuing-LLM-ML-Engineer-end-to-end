"""
Custom exception classes.
"""
from typing import Optional


class IndoClothException(Exception):
    """Base exception for IndoCloth Market."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class ModelLoadError(IndoClothException):
    """Raised when model loading fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class InferenceError(IndoClothException):
    """Raised when inference fails."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)


class KafkaError(IndoClothException):
    """Raised when Kafka operations fail."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class DatabaseError(IndoClothException):
    """Raised when database operations fail."""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)


class SlackError(IndoClothException):
    """Raised when Slack operations fail."""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)
