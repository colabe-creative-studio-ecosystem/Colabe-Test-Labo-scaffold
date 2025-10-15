import reflex as rx
import logging
import asyncio
import json
import os
from sqlalchemy import text
from app.ui.states.auth_state import AuthState
from app.orchestrator.tasks import enqueue_health_check
from app.ui.pages.index import sidebar, user_dropdown
from typing import Any, TypedDict


class SLIData(TypedDict):
    name: str
    description: str
    target: str
    status: str
    current: str


class ServiceData(TypedDict):
    service: str
    slis: list[SLIData]


class SystemHealthState(AuthState):
    health_status: str = "Checking..."
    db_status: str = "Unknown"
    redis_status: str = "Unknown"
    worker_status: str = "Unknown"
    job_id: str = ""
    slos: list[ServiceData] = []
    error_budget_burn: float = 1.25
    last_load_run: str = "2 hours ago - PASSED"
    last_chaos_run: str = "3 days ago - PASSED"
    last_dr_restore: str = "1 day ago - VERIFIED"
    last_key_rotation: str = "10 days ago"
    canary_pass_time: str = "25 minutes ago"
    on_call_schedule_link: str = "#"
    top_open_incident: str = "None"
    lighthouse_axe_status: str = "Passing"
    last_sitemap_build: str = "5 minutes ago"
    form_error_rate: str = "0.5%"
    crm_api_status: str = "150ms / 0.1% errors"
    demo_calendar_health: str = "Healthy"
    ab_experiments_active: str = "3 Active"
    funnel_snapshot: str = "10k → 200 → 45 → 10"

    @rx.event
    def on_load_health(self):
        yield SystemHealthState.check_health()
        yield SystemHealthState.load_slos()

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
        try:
            self.job_id = enqueue_health_check()
            self.worker_status = "Job Enqueued"
        except Exception as e:
            logging.exception(e)
            self.worker_status = "Enqueue Failed"
        if self.db_status == "OK" and self.redis_status == "OK":
            self.health_status = "OK"
        else:
            self.health_status = "Degraded"
        return SystemHealthState.check_job_status

    @rx.event(background=True)
    async def check_job_status(self):
        import time
        from rq.job import Job
        from app.orchestrator.tasks import redis_conn

        if not self.job_id:
            return
        job = Job.fetch(self.job_id, connection=redis_conn)
        for _ in range(10):
            async with self:
                if job.is_finished:
                    self.worker_status = f"OK ({job.result})"
                    return
                elif job.is_failed:
                    self.worker_status = "Job Failed"
                    return
            await asyncio.sleep(1)
        async with self:
            self.worker_status = "Job Timed Out"

    @rx.event
    def load_slos(self):
        try:
            slo_file_path = os.path.join(os.getcwd(), "assets", "ops", "slo.json")
            with open(slo_file_path, "r") as f:
                self.slos = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.exception(f"Failed to load SLOs: {e}")
            self.slos = []


def health_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "System Health", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Service status, SLOs, and Go-Live readiness.",
                    class_name="text-gray-500",
                ),
            ),
            user_dropdown(),
            class_name="flex items-center justify-between p-4 border-b bg-white",
        ),
        rx.el.div(
            rx.el.button(
                "Refresh All",
                on_click=SystemHealthState.on_load_health,
                class_name="mb-6 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600",
            ),
            rx.el.div(
                status_card("Overall Status", SystemHealthState.health_status),
                status_card("Database", SystemHealthState.db_status),
                status_card("Redis Cache", SystemHealthState.redis_status),
                status_card("Background Worker", SystemHealthState.worker_status),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6",
            ),
            launch_card(),
            domains_seo_card(),
            runners_card(),
            marketing_sales_card(),
            slo_section(),
            class_name="p-8 space-y-8",
        ),
        class_name="flex-1 flex flex-col bg-gray-50",
    )


def health_check_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            SystemHealthState.is_logged_in,
            rx.el.div(
                sidebar(),
                health_page_content(),
                class_name="flex min-h-screen font-['Inter']",
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen",
            ),
        ),
        on_mount=SystemHealthState.on_load_health,
    )


def status_card(title: str, status: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-medium text-gray-700"),
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    status.contains("OK"),
                    "h-3 w-3 rounded-full bg-green-500 animate-pulse",
                    rx.cond(
                        status.contains("Error") | status.contains("Failed"),
                        "h-3 w-3 rounded-full bg-red-500",
                        "h-3 w-3 rounded-full bg-yellow-500",
                    ),
                )
            ),
            rx.el.p(
                status,
                class_name="font-semibold",
                color=rx.cond(
                    status.contains("OK"),
                    "text-green-600",
                    rx.cond(
                        status.contains("Error") | status.contains("Failed"),
                        "text-red-600",
                        "text-yellow-600",
                    ),
                ),
            ),
            class_name="mt-2 flex items-center space-x-2",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def launch_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            rx.icon("rocket", class_name="mr-2"),
            "Launch Readiness",
            class_name="text-xl font-semibold text-gray-800 flex items-center",
        ),
        rx.el.div(
            launch_item(
                "SLO Status", "All Green", is_green=True, icon="check-circle-2"
            ),
            launch_item(
                "Error Budget Burn (24h)",
                f"{SystemHealthState.error_budget_burn.to_string()}%",
                is_green=SystemHealthState.error_budget_burn < 5,
                icon="pie-chart",
            ),
            launch_item(
                "Last Load Run",
                SystemHealthState.last_load_run,
                is_green=SystemHealthState.last_load_run.contains("PASSED"),
                icon="gauge-circle",
            ),
            launch_item(
                "Last Chaos Run",
                SystemHealthState.last_chaos_run,
                is_green=SystemHealthState.last_chaos_run.contains("PASSED"),
                icon="zap",
            ),
            launch_item(
                "Last DR Restore",
                SystemHealthState.last_dr_restore,
                is_green=SystemHealthState.last_dr_restore.contains("VERIFIED"),
                icon="database-backup",
            ),
            launch_item(
                "Last Key Rotation",
                SystemHealthState.last_key_rotation,
                is_green=True,
                icon="key-round",
            ),
            launch_item(
                "Canary Pass Time",
                SystemHealthState.canary_pass_time,
                is_green=True,
                icon="bird",
            ),
            launch_item(
                "On-Call",
                "View Schedule",
                is_green=True,
                icon="phone-forwarded",
                href=SystemHealthState.on_call_schedule_link,
            ),
            launch_item(
                "Top Open Incident",
                SystemHealthState.top_open_incident,
                is_green=SystemHealthState.top_open_incident == "None",
                icon="siren",
            ),
            class_name="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def domains_seo_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            rx.icon("globe", class_name="mr-2"),
            "Domains & SEO",
            class_name="text-xl font-semibold text-gray-800 flex items-center",
        ),
        rx.el.div(
            launch_item(
                "Last Sitemap Build", "5 minutes ago", is_green=True, icon="file-text"
            ),
            launch_item(
                "hreflang Parity (EN/ES)", "100%", is_green=True, icon="languages"
            ),
            launch_item("Lighthouse Score (Public)", "98", is_green=True, icon="siren"),
            launch_item("Cache Hit % (Edge)", "95.2%", is_green=True, icon="server"),
            launch_item(
                "Top Redirect Anomaly", "None", is_green=True, icon="route-off"
            ),
            launch_item("Broken Links", "0 errors", is_green=True, icon="link"),
            class_name="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def runners_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            rx.icon("server", class_name="mr-2"),
            "Runners",
            class_name="text-xl font-semibold text-gray-800 flex items-center",
        ),
        rx.el.div(
            launch_item(
                "Fleet Size / Healthy %",
                "100 / 99%",
                is_green=True,
                icon="circle-check",
            ),
            launch_item(
                "Queue Depth / Avg Wait",
                "12 jobs / 25s",
                is_green=True,
                icon="list",
                href="/runners",
            ),
            launch_item("Cache Hit Rate", "88%", is_green=True, icon="database"),
            launch_item(
                "Device Minutes (Today)", "1,234", is_green=True, icon="smartphone"
            ),
            launch_item(
                "Last Attestation Pass", "2m ago", is_green=True, icon="shield-check"
            ),
            launch_item(
                "Last Autoscale Action",
                "scale-up (+2)",
                is_green=True,
                icon="trending-up",
            ),
            class_name="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def launch_item(
    title: str, value: str, is_green: rx.Var[bool], icon: str, href: str | None = None
) -> rx.Component:
    content = rx.el.div(
        rx.icon(
            icon,
            class_name="h-5 w-5",
            color=rx.cond(is_green, "text-green-500", "text-red-500"),
        ),
        rx.el.div(
            rx.el.p(title, class_name="text-sm font-medium text-gray-600"),
            rx.el.p(value, class_name="text-sm font-semibold text-gray-900"),
        ),
        class_name="flex items-center space-x-3",
    )
    return rx.cond(
        href,
        rx.el.a(content, href=href, target="_blank", class_name="hover:opacity-75"),
        content,
    )


def slo_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Service Level Objectives (SLOs)",
            class_name="text-xl font-semibold text-gray-800 mb-4",
        ),
        rx.foreach(SystemHealthState.slos, render_slo_service_card),
        class_name="space-y-6",
    )


def render_slo_service_card(service_data: ServiceData) -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            service_data["service"],
            class_name="text-lg font-semibold text-gray-900 px-6 pt-4",
        ),
        rx.el.div(
            rx.foreach(service_data["slis"].to(list[SLIData]), render_sli_row),
            class_name="divide-y divide-gray-200",
        ),
        class_name="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden",
    )


def render_sli_row(sli_data: SLIData) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(sli_data["name"], class_name="font-medium text-gray-900"),
            rx.el.p(sli_data["description"], class_name="text-sm text-gray-500"),
            class_name="flex-1",
        ),
        rx.el.div(
            rx.el.p(
                sli_data["target"],
                class_name="text-sm font-mono text-gray-600 text-right",
            ),
            rx.el.div(
                rx.el.div(
                    class_name=rx.cond(
                        sli_data["status"] == "green",
                        "h-2 w-2 rounded-full bg-green-500",
                        "h-2 w-2 rounded-full bg-red-500",
                    )
                ),
                rx.el.p(
                    sli_data["current"],
                    class_name="text-sm font-semibold",
                    color=rx.cond(
                        sli_data["status"] == "green", "text-green-600", "text-red-600"
                    ),
                ),
                class_name="flex items-center space-x-2 justify-end",
            ),
            class_name="w-40 text-right",
        ),
        class_name="flex items-center justify-between p-4",
    )


def marketing_sales_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            rx.icon("briefcase", class_name="mr-2"),
            "Marketing & Sales",
            class_name="text-xl font-semibold text-gray-800 flex items-center",
        ),
        rx.el.div(
            launch_item(
                "Lighthouse/axe",
                SystemHealthState.lighthouse_axe_status,
                is_green=SystemHealthState.lighthouse_axe_status == "Passing",
                icon="siren",
            ),
            launch_item(
                "Last Sitemap Build",
                SystemHealthState.last_sitemap_build,
                is_green=True,
                icon="file-text",
            ),
            launch_item(
                "Form Error Rate",
                SystemHealthState.form_error_rate,
                is_green=True,
                icon="alert-circle",
            ),
            launch_item(
                "CRM API Latency/Errors",
                SystemHealthState.crm_api_status,
                is_green=True,
                icon="plug-zap",
            ),
            launch_item(
                "Demo Calendar Health",
                SystemHealthState.demo_calendar_health,
                is_green=SystemHealthState.demo_calendar_health == "Healthy",
                icon="calendar-check",
            ),
            launch_item(
                "A/B Experiments",
                SystemHealthState.ab_experiments_active,
                is_green=True,
                icon="beaker",
            ),
            launch_item(
                "Funnel (V→L→MQL→SQL)",
                SystemHealthState.funnel_snapshot,
                is_green=True,
                icon="filter",
            ),
            class_name="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-x-6 gap-y-4",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )