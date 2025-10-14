import reflex as rx
from app.core.settings import settings
from app.orchestrator.tasks import enqueue_health_check


class BaseState(rx.State):
    """The base state for the app."""

    @rx.var
    def db_url(self) -> str:
        return (
            settings.DATABASE_URL.split("@")[1]
            if "@" in settings.DATABASE_URL
            else "Not configured"
        )

    @rx.var
    def redis_url(self) -> str:
        return settings.REDIS_URL