import reflex as rx
from app.ui.pages.index import index
from app.ui.pages.health import health_check_page
from app.ui.pages.auth import login_page, register_page
from app.ui.pages.audit import audit_log_page
from app.ui.pages.security import security_page
from app.ui.pages.quality import quality_page
from app.ui.pages.policies import policies_page
from app.ui.pages.billing import billing_page
from app.ui.pages.api_docs import api_docs_page
from app.ui.pages.terms import terms_page
from app.ui.pages.privacy import privacy_page
from app.ui.pages.projects import projects_page
from app.ui.pages.test_plans import test_plans_page
from app.ui.pages.runs import runs_page
from app.ui.pages.diffs import diffs_page
from app.ui.pages.settings import settings_page
from app.ui.pages.performance import performance_page
from app.ui.pages.accessibility import accessibility_page
from app.ui.states.auth_state import AuthState
from app.ui.states.billing_state import BillingState
from app.ui.states.project_state import ProjectState
from app.ui.states.test_plan_state import TestPlanState
from app.ui.states.run_state import RunState
from app.ui.states.security_state import SecurityState
from app.ui.states.policy_state import PolicyState
from app.ui.states.diff_state import DiffState
from app.ui.states.settings_state import SettingsState
from app.ui.states.audit_state import AuditState
from app.ui.states.api_docs_state import ApiDocsState
from app.ui.states.health_state import HealthState
from app.ui.states.quality_state import QualityState
from app.core.settings import settings
from app.integrations.webhook_handler import stripe_webhook
from app.core.db_init import initialize_db

initialize_db()


def api_routes(api):
    api.add_route("/api/webhook/stripe", stripe_webhook, methods=["POST"])
    return api


app = rx.App(
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
    theme=rx.theme(appearance="light"),
    stylesheets=["/colabe.css"],
    api_transformer=api_routes,
)
sidebar_load_events = [AuthState.check_login, BillingState.load_wallet]
app.add_page(index, route="/", on_load=sidebar_load_events)
app.add_page(
    health_check_page,
    route="/health",
    on_load=sidebar_load_events + [HealthState.check_health],
)
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(
    audit_log_page,
    route="/audits",
    on_load=sidebar_load_events + [AuditState.load_audit_logs],
)
app.add_page(
    security_page,
    route="/security",
    on_load=sidebar_load_events + [SecurityState.load_security_data],
)
app.add_page(
    quality_page,
    route="/quality",
    on_load=sidebar_load_events + [QualityState.load_initial_data],
)
app.add_page(
    policies_page,
    route="/policies",
    on_load=sidebar_load_events + [PolicyState.load_policy],
)
app.add_page(
    billing_page,
    route="/billing",
    on_load=sidebar_load_events + [BillingState.check_payment_status],
)
app.add_page(
    api_docs_page,
    route="/api-docs",
    on_load=sidebar_load_events + [ApiDocsState.generate_openapi_spec],
)
app.add_page(
    projects_page,
    route="/projects",
    on_load=sidebar_load_events + [ProjectState.load_projects],
)
app.add_page(
    test_plans_page,
    route="/test-plans",
    on_load=sidebar_load_events + [TestPlanState.load_data],
)
app.add_page(
    runs_page, route="/runs", on_load=sidebar_load_events + [RunState.load_data]
)
app.add_page(
    diffs_page, route="/diffs", on_load=sidebar_load_events + [DiffState.load_data]
)
app.add_page(
    settings_page,
    route="/settings",
    on_load=sidebar_load_events + [SettingsState.load_settings],
)
app.add_page(performance_page, route="/performance", on_load=sidebar_load_events)
app.add_page(accessibility_page, route="/accessibility", on_load=sidebar_load_events)
app.add_page(terms_page, route="/terms")
app.add_page(privacy_page, route="/privacy")