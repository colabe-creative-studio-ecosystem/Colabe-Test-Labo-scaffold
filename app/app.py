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
from app.ui.pages.ops_events import ops_events_page
from app.ui.pages.admin_tenants import admin_tenants_page
from app.ui.states.auth_state import AuthState
from app.core.settings import settings
from app.core import models
from app.ui.pages.who_we_are import who_we_are_page
from app.ui.pages.embeds import embed_page
from app.ui.pages.sitemap import sitemap_page
from app.ui.pages.ops_dashboard import ops_dashboard_page
from app.ui.pages.profile import profile_page
from app.ui.pages.members import members_page

csp = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' https://api.dicebear.com data:; connect-src 'self' wss://*.colabe.app"
app = rxe.App(
    head_components=[
        rx.el.meta(char_set="UTF-8"),
        rx.el.meta(name="viewport", content="width=device-width, initial-scale=1.0"),
        rx.el.meta(http_equiv="X-UA-Compatible", content="ie=edge"),
        rx.el.meta(http_equiv="Content-Security-Policy", content=csp),
        rx.el.meta(name="Referrer-Policy", content="strict-origin-when-cross-origin"),
        rx.el.meta(name="X-Content-Type-Options", content="nosniff"),
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
app.add_page(ops_events_page, route="/ops/events", on_load=AuthState.check_login)
app.add_page(who_we_are_page, route="/who-we-are", on_load=AuthState.check_login)
app.add_page(sitemap_page, route="/sitemap", on_load=AuthState.check_login)
app.add_page(embed_page, route="/embed/[widget_type]")
app.add_page(admin_tenants_page, route="/admin/tenants", on_load=AuthState.check_login)
app.add_page(ops_dashboard_page, route="/ops/dashboard", on_load=AuthState.check_login)
app.add_page(profile_page, route="/profile", on_load=AuthState.check_login)
app.add_page(members_page, route="/members", on_load=AuthState.check_login)