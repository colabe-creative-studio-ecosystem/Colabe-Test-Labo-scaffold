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
    STRIPE_SECRET_KEY: str | None = os.environ.get(
        "STRIPE_SECRET_KEY"
    ) or os.environ.get("STRIPE_API_KEY")
    STRIPE_WEBHOOK_SECRET: str | None = os.environ.get("STRIPE_WEBHOOK_SECRET")
    DOMAIN: str = os.environ.get("DOMAIN", "http://localhost:3000")
    
    # Outbound Messaging Guardrail Settings
    MAX_MESSAGES_PER_CONVERSATION_WINDOW: int = int(
        os.environ.get("MAX_MESSAGES_PER_CONVERSATION_WINDOW", "4")
    )
    CONVERSATION_WINDOW_SECONDS: int = int(
        os.environ.get("CONVERSATION_WINDOW_SECONDS", "60")
    )
    DEFAULT_CONTACT_COOLDOWN_SECONDS: int = int(
        os.environ.get("DEFAULT_CONTACT_COOLDOWN_SECONDS", "300")
    )
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = int(
        os.environ.get("CIRCUIT_BREAKER_FAILURE_THRESHOLD", "10")
    )
    CIRCUIT_BREAKER_WINDOW_MINUTES: int = int(
        os.environ.get("CIRCUIT_BREAKER_WINDOW_MINUTES", "10")
    )
    CIRCUIT_BREAKER_RECOVERY_SECONDS: int = int(
        os.environ.get("CIRCUIT_BREAKER_RECOVERY_SECONDS", "300")
    )
    ADMIN_NOTIFICATION_COOLDOWN_MINUTES: int = int(
        os.environ.get("ADMIN_NOTIFICATION_COOLDOWN_MINUTES", "60")
    )


settings = Settings()