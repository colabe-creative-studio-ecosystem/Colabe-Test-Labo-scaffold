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
    COLABE_TRIGGERBUS_BROKER_URL: str | None = os.environ.get(
        "COLABE_TRIGGERBUS_BROKER_URL"
    )
    TRIGGERBUS_CLIENT_ID: str | None = os.environ.get("TRIGGERBUS_CLIENT_ID")
    TRIGGERBUS_CLIENT_SECRET: str | None = os.environ.get("TRIGGERBUS_CLIENT_SECRET")
    TRIGGERBUS_PRODUCER_BATCH: int = int(
        os.environ.get("TRIGGERBUS_PRODUCER_BATCH", 200)
    )
    TRIGGERBUS_PRODUCER_FLUSH_MS: int = int(
        os.environ.get("TRIGGERBUS_PRODUCER_FLUSH_MS", 200)
    )
    TRIGGERBUS_CONSUMER_MAX_INFLIGHT: int = int(
        os.environ.get("TRIGGERBUS_CONSUMER_MAX_INFLIGHT", 32)
    )
    TRIGGERBUS_CONSUMER_RETRY_BACKOFF_MS: int = int(
        os.environ.get("TRIGGERBUS_CONSUMER_RETRY_BACKOFF_MS", 500)
    )
    TRIGGERBUS_DEADLETTER_TTL_DAYS: int = int(
        os.environ.get("TRIGGERBUS_DEADLETTER_TTL_DAYS", 7)
    )
    EVENT_SCHEMA_REGISTRY_URL: str | None = os.environ.get("EVENT_SCHEMA_REGISTRY_URL")
    EVENT_SCHEMA_STRICT: bool = (
        os.environ.get("EVENT_SCHEMA_STRICT", "true").lower() == "true"
    )


settings = Settings()