import reflex as rx
import reflex_enterprise as rxe
from app.ui.pages.index import index
from app.ui.pages.health import health_check_page
from app.ui.pages.auth import login_page, register_page
from app.ui.pages.audit import audit_log_page
from app.ui.pages.security import security_page
from app.ui.pages.quality import quality_page
from app.ui.pages.policies import policies_page
from app.ui.pages.billing import billing_page
from app.ui.pages.api_docs import api_docs_page
from app.ui.pages.privacy_policy import privacy_policy_page
from app.ui.pages.terms_and_conditions import terms_and_conditions_page
from app.ui.states.auth_state import AuthState
from app.core.settings import settings
from app.core import models

app = rxe.App(
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
    theme=rx.theme(appearance="dark"),
    stylesheets=["/colabe.css"],
)
app.add_page(index, route="/", on_load=AuthState.check_login)
app.add_page(health_check_page, route="/health", on_load=AuthState.check_login)
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(audit_log_page, route="/audits", on_load=AuthState.check_login)
app.add_page(security_page, route="/security", on_load=AuthState.check_login)
app.add_page(quality_page, route="/quality", on_load=AuthState.check_login)
app.add_page(policies_page, route="/policies", on_load=AuthState.check_login)
app.add_page(billing_page, route="/billing", on_load=AuthState.check_login)
app.add_page(api_docs_page, route="/api-docs", on_load=AuthState.check_login)
app.add_page(privacy_policy_page, route="/privacy")
app.add_page(terms_and_conditions_page, route="/terms")