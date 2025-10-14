import os
from dotenv import load_dotenv
from datetime import timedelta
import json
import logging

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
    ORG_LEGAL_NAME: str = os.environ.get("ORG_LEGAL_NAME", "Colabe Test Labo SL")
    ORG_ADDRESS_LINE1: str = os.environ.get(
        "ORG_ADDRESS_LINE1", "Carrer de la Tecnologia 1"
    )
    ORG_ADDRESS_LINE2: str | None = os.environ.get("ORG_ADDRESS_LINE2")
    ORG_CITY: str = os.environ.get("ORG_CITY", "Barcelona")
    ORG_POSTAL_CODE: str = os.environ.get("ORG_POSTAL_CODE", "08001")
    ORG_COUNTRY: str = os.environ.get("ORG_COUNTRY", "Spain")
    ORG_EMAIL: str = os.environ.get("ORG_EMAIL", "contact@colabe.ai")
    DPO_EMAIL: str | None = os.environ.get("DPO_EMAIL")
    ORG_VAT: str | None = os.environ.get("ORG_VAT", "ESB12345678")
    GOVERNING_LAW: str = os.environ.get("GOVERNING_LAW", "Spain")
    VENUE_CITY: str = os.environ.get("VENUE_CITY", "Barcelona")
    CONTACT_FORM_URL: str = os.environ.get("CONTACT_FORM_URL", "/contact")
    _subprocessors_json_str = os.environ.get("SUBPROCESSORS_JSON", "[]")
    try:
        SUBPROCESSORS_JSON: list[dict[str, str]] = json.loads(_subprocessors_json_str)
    except json.JSONDecodeError as e:
        logging.exception(f"Error decoding SUBPROCESSORS_JSON: {e}")
        SUBPROCESSORS_JSON: list[dict[str, str]] = []


settings = Settings()
REQUIRED_ORG_VARS = [
    "ORG_LEGAL_NAME",
    "ORG_ADDRESS_LINE1",
    "ORG_CITY",
    "ORG_POSTAL_CODE",
    "ORG_COUNTRY",
    "ORG_EMAIL",
    "GOVERNING_LAW",
    "VENUE_CITY",
    "CONTACT_FORM_URL",
]