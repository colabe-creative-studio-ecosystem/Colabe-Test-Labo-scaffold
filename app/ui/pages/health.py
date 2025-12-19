import reflex as rx
import logging
import asyncio
from sqlalchemy import text
from app.ui.components.footer import footer
from app.ui.states.auth_state import AuthState
from app.orchestrator.tasks import enqueue_health_check
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style


class HealthState(rx.State):
    health_status: str = "Checking..."
    db_status: str = "Unknown"
    redis_status: str = "Unknown"
    worker_status: str = "Unknown"
    job_id: str = ""

    @rx.event
    def check_health(self):
        try:
            with rx.session() as session:
                session.exec(text("SELECT 1"))
            self.db_status = "OK"
        except Exception as e:
            logging.exception(e)
            self.db_status = "Error"
        try:
            import redis
            from app.core.settings import settings

            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            self.redis_status = "OK"
        except Exception as e:
            logging.exception(e)
            self.redis_status = "Error"
        job_id = enqueue_health_check()
        if job_id:
            self.job_id = job_id
            self.worker_status = "Job Enqueued"
        else:
            self.job_id = ""
            if self.redis_status == "Error":
                self.worker_status = "Redis Unavailable"
            else:
                self.worker_status = "Enqueue Failed"
        if self.db_status == "OK" and self.redis_status == "OK":
            self.health_status = "OK"
        else:
            self.health_status = "Degraded"
        if self.job_id:
            return HealthState.check_job_status

    @rx.event(background=True)
    async def check_job_status(self):
        import time
        from rq.job import Job
        from app.orchestrator.tasks import redis_conn

        if not self.job_id:
            return
        for _ in range(10):
            job = Job.fetch(self.job_id, connection=redis_conn)
            if job.is_finished:
                async with self:
                    self.worker_status = f"OK ({job.result})"
                return
            elif job.is_failed:
                async with self:
                    self.worker_status = "Job Failed"
                return
            await asyncio.sleep(1)
        async with self:
            self.worker_status = "Job Timed Out"


def health_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "System Health",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p("Status of system components.", class_name="text-[#A9B3C1]"),
            ),
            user_dropdown(),
            class_name="flex items-center justify-between p-4 border-b border-white/10",
        ),
        rx.el.div(
            rx.el.button(
                "Refresh",
                on_click=HealthState.check_health,
                class_name="mb-6 px-4 py-2 bg-[#00E5FF] text-[#0A0F14] font-semibold rounded-lg hover:opacity-90",
            ),
            rx.el.div(
                status_card("Overall Status", HealthState.health_status),
                status_card("Database", HealthState.db_status),
                status_card("Redis Cache", HealthState.redis_status),
                status_card("Background Worker", HealthState.worker_status),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6",
            ),
            class_name="p-8",
        ),
        class_name="flex-1 flex flex-col",
        on_mount=HealthState.check_health,
    )


def health_check_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    health_page_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def status_card(title: str, status: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-medium text-[#E8F0FF]"),
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    status.contains("OK"),
                    "h-3 w-3 rounded-full bg-green-500",
                    rx.cond(
                        status.contains("Error") | status.contains("Failed"),
                        "h-3 w-3 rounded-full bg-red-500",
                        "h-3 w-3 rounded-full bg-yellow-500",
                    ),
                )
            ),
            rx.el.p(
                status,
                class_name=rx.cond(
                    status.contains("OK"),
                    "text-green-600 font-semibold",
                    rx.cond(
                        status.contains("Error") | status.contains("Failed"),
                        "text-red-600 font-semibold",
                        "text-yellow-600 font-semibold",
                    ),
                ),
            ),
            class_name="mt-2 flex items-center space-x-2",
        ),
        class_name="bg-[#0E1520] p-6 rounded-xl border border-white/10 shadow-sm",
    )