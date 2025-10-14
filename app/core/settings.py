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
    EMBED_ALLOWED_ORIGINS: str = os.environ.get(
        "EMBED_ALLOWED_ORIGINS", "https://app.colabe.*,https://studio.colabe.*"
    )
    EMBED_TOKEN_TTL_MIN: int = int(os.environ.get("EMBED_TOKEN_TTL_MIN", 15))
    SDK_NPM_REGISTRY_URL: str | None = os.environ.get("SDK_NPM_REGISTRY_URL")
    SDK_NPM_TOKEN: str | None = os.environ.get("SDK_NPM_TOKEN")
    SDK_PYPI_INDEX_URL: str | None = os.environ.get("SDK_PYPI_INDEX_URL")
    SDK_PYPI_USERNAME: str | None = os.environ.get("SDK_PYPI_USERNAME")
    SDK_PYPI_PASSWORD: str | None = os.environ.get("SDK_PYPI_PASSWORD")
    SDK_RELEASE_SIGNING_KEY: str | None = os.environ.get("SDK_RELEASE_SIGNING_KEY")
    ORG_EMAIL: str = os.environ.get("ORG_EMAIL", "contact@colabe.ai")
    TENANT_DEFAULT_REGION: str = os.environ.get("TENANT_DEFAULT_REGION", "eu-central-1")
    TENANT_MAX_DOMAINS_PER_TENANT: int = int(
        os.environ.get("TENANT_MAX_DOMAINS_PER_TENANT", 2)
    )
    THEME_SAFE_ACCENTS: str = os.environ.get(
        "THEME_SAFE_ACCENTS", "#00E5FF,#FF3CF7,#FFE600,#D8B76E"
    )
    DOMAIN_DNS_PROVIDER: str = os.environ.get("DOMAIN_DNS_PROVIDER", "cloud")
    ACME_EMAIL: str | None = os.environ.get("ACME_EMAIL")
    SSO_ENTERPRISE_ENABLED: bool = (
        os.environ.get("SSO_ENTERPRISE_ENABLED", "false").lower() == "true"
    )
    SCIM_ENABLED: bool = os.environ.get("SCIM_ENABLED", "false").lower() == "true"
    TRIAL_DAYS_DEFAULT: int = int(os.environ.get("TRIAL_DAYS_DEFAULT", 14))
    QUOTA_DEFAULTS_JSON: str = os.environ.get("QUOTA_DEFAULTS_JSON", "{}")
    COLABE_ID_ISSUER: str | None = os.environ.get("COLABE_ID_ISSUER")
    COLABE_JWKS_URL: str | None = os.environ.get("COLABE_JWKS_URL")
    COLABE_GATEWAY_AUDIENCE: str = os.environ.get(
        "COLABE_GATEWAY_AUDIENCE", "colabe.testlabo"
    )
    SESSION_COOKIE_NAME: str = os.environ.get("SESSION_COOKIE_NAME", "sid")
    SESSION_TTL_HOURS: int = int(os.environ.get("SESSION_TTL_HOURS", 8))
    SESSION_REDIS_PREFIX: str = os.environ.get("SESSION_REDIS_PREFIX", "ctl:sess:")
    CSRF_SECRET: str | None = os.environ.get("CSRF_SECRET")
    LOGIN_RATE_LIMIT_PER_MIN: int = int(os.environ.get("LOGIN_RATE_LIMIT_PER_MIN", 10))


settings = Settings()