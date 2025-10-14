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
    LOAD_MAX_VUS: int = int(os.environ.get("LOAD_MAX_VUS", 500))
    LOAD_STAGE_MULTIPLIER: int = int(os.environ.get("LOAD_STAGE_MULTIPLIER", 2))
    CHAOS_ENABLED: bool = os.environ.get("CHAOS_ENABLED", "true").lower() == "true"
    CHAOS_MAX_CONCURRENT: int = int(os.environ.get("CHAOS_MAX_CONCURRENT", 2))
    DR_VERIFY_WINDOW_DAYS: int = int(os.environ.get("DR_VERIFY_WINDOW_DAYS", 7))
    SLO_WINDOW_DAYS: int = int(os.environ.get("SLO_WINDOW_DAYS", 30))
    ERROR_BUDGET_ALERT_FAST: float = float(
        os.environ.get("ERROR_BUDGET_ALERT_FAST", 0.02)
    )
    ERROR_BUDGET_ALERT_SLOW: float = float(
        os.environ.get("ERROR_BUDGET_ALERT_SLOW", 0.05)
    )
    KEY_ROTATION_DAYS: int = int(os.environ.get("KEY_ROTATION_DAYS", 90))
    ONCALL_PAGER_WEBHOOK_URL: str | None = os.environ.get("ONCALL_PAGER_WEBHOOK_URL")
    STATUS_PAGE_BASE_URL: str | None = os.environ.get("STATUS_PAGE_BASE_URL")
    GPT_HUB_ENABLED: bool = os.environ.get("GPT_HUB_ENABLED", "true").lower() == "true"
    GPT_MODEL_DEFAULT_SUMMARY: str = os.environ.get(
        "GPT_MODEL_DEFAULT_SUMMARY", "claude-3-haiku-20240307"
    )
    GPT_MODEL_DEFAULT_PR_REVIEW: str = os.environ.get(
        "GPT_MODEL_DEFAULT_PR_REVIEW", "claude-3-sonnet-20240229"
    )
    GPT_TEMPERATURE: float = float(os.environ.get("GPT_TEMPERATURE", 0.1))
    GPT_TOP_P: float = float(os.environ.get("GPT_TOP_P", 0.9))
    PUBLIC_BASE_URL: str = os.environ.get("PUBLIC_BASE_URL", "https://colabe.app")
    PUBLIC_LOCALES: str = os.environ.get("PUBLIC_LOCALES", "en,es")
    EDGE_REGION_DEFAULT: str = os.environ.get("EDGE_REGION_DEFAULT", "eu")
    EDGE_STALE_WHILE_REVALIDATE_SECONDS: int = int(
        os.environ.get("EDGE_STALE_WHILE_REVALIDATE_SECONDS", 600)
    )
    EDGE_CACHE_MAXAGE_SECONDS: int = int(
        os.environ.get("EDGE_CACHE_MAXAGE_SECONDS", 1800)
    )
    OG_IMAGE_FUNCTION_URL: str = os.environ.get("OG_IMAGE_FUNCTION_URL", "")
    SEO_SITEMAP_CHUNK_SIZE: int = int(os.environ.get("SEO_SITEMAP_CHUNK_SIZE", 1000))
    SEO_PROGRAMMATIC_PAGES_ENABLED: bool = (
        os.environ.get("SEO_PROGRAMMATIC_PAGES_ENABLED", "true").lower() == "true"
    )
    SEO_TENANT_PROFILES_ENABLED: bool = (
        os.environ.get("SEO_TENANT_PROFILES_ENABLED", "true").lower() == "true"
    )
    TRACKING_CONSENT_REQUIRED: bool = (
        os.environ.get("TRACKING_CONSENT_REQUIRED", "true").lower() == "true"
    )
    ANON_COOKIE_TTL_DAYS: int = int(os.environ.get("ANON_COOKIE_TTL_DAYS", 30))
    REDIRECTS_JSON: str = os.environ.get(
        "REDIRECTS_JSON", "content/_data/redirects.json"
    )


settings = Settings()