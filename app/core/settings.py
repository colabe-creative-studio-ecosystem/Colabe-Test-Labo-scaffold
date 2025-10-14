from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    """Application configuration loaded from the environment."""

    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/colabe_db"
    )
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "a_very_secret_key")
    CSRF_SECRET_KEY: str = os.environ.get("CSRF_SECRET_KEY", "another_secret_for_csrf")
    SESSION_TIMEOUT: timedelta = timedelta(hours=1)
    S3_ENDPOINT_URL: Optional[str] = os.environ.get("S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID: Optional[str] = os.environ.get("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: Optional[str] = os.environ.get("S3_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME: str = os.environ.get("S3_BUCKET_NAME", "colabe-artifacts")
    ANTHROPIC_API_KEY: Optional[str] = os.environ.get("ANTHROPIC_API_KEY")

    @property
    def session_timeout_seconds(self) -> int:
        """Return the session timeout as a whole number of seconds."""

        return int(self.SESSION_TIMEOUT.total_seconds())

    @property
    def is_s3_configured(self) -> bool:
        """Whether all S3 settings are present."""

        return all(
            [self.S3_ENDPOINT_URL, self.S3_ACCESS_KEY_ID, self.S3_SECRET_ACCESS_KEY]
        )


settings = Settings()
