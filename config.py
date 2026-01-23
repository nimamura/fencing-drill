"""Application configuration from environment variables."""
import os
from dataclasses import dataclass

from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()


@dataclass
class Settings:
    """Application settings loaded from environment variables."""

    session_limit: int = 100
    session_timeout_minutes: int = 30
    log_level: str = "INFO"
    base_url: str = ""

    def __init__(self):
        """Initialize settings from environment variables."""
        self.session_limit = int(os.getenv("SESSION_LIMIT", "100"))
        self.session_timeout_minutes = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.base_url = os.getenv("BASE_URL", "")


# Global settings instance
settings = Settings()
