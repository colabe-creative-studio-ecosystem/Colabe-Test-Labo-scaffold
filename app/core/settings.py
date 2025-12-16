import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Settings:
    DATABASE_URL: str = os.environ.get(
        "DATABASE_URL", "postgresql://user:password@localhost:5432/colabe_db"
    )
    REDIS_URL: str = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "a_very_secret_key")
    CSRF_SECRET_KEY: str = os.environ.get("CSRF_SECRET_KEY", "another_secret_for_csrf")
    SESSION_TIMEOUT: timedelta = timedelta(hours=1)
    S3_ENDPOINT_URL: str | None = os.environ.get("S3_ENDPOINT_URL")
    S3_ACCESS_KEY_ID: str | None = os.environ.get("S3_ACCESS_KEY_ID")
    S3_SECRET_ACCESS_KEY: str | None = os.environ.get("S3_SECRET_ACCESS_KEY")
    S3_BUCKET_NAME: str = os.environ.get("S3_BUCKET_NAME", "colabe-artifacts")
    ANTHROPIC_API_KEY: str | None = os.environ.get("ANTHROPIC_API_KEY")


settings = Settings()