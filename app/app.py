import reflex as rx
import reflex_enterprise as rxe
from fastapi import FastAPI
from app.ui.pages.index import index
from app.ui.pages.health import health_check_page
from app.ui.pages.auth import login_page, register_page
from app.ui.pages.audit import audit_log_page
from app.ui.pages.security import security_page
from app.ui.pages.quality import quality_page
from app.ui.pages.policies import policies_page
from app.ui.pages.billing import billing_page
from app.ui.pages.api_docs import api_docs_page
from app.ui.pages.gpt_hub import gpt_hub_page
from app.ui.pages.public.who_we_are import who_we_are_page
from app.ui.pages.public.adapters import adapters_page
from app.ui.pages.public.playbooks import playbooks_page
from app.ui.pages.public.integrations import integrations_page
from app.ui.pages.runners import runners_page
from app.ui.pages.public.sitemap import sitemap_index
from app.ui.states.auth_state import AuthState
from app.ui.states.seo_state import SeoState
from app.core.settings import settings
from app.core import models

api = FastAPI()
api.add_api_route("/sitemap.xml", sitemap_index)
app = rxe.App(
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.link(rel="preconnect", href=settings.PUBLIC_BASE_URL),
        rx.el.link(rel="dns-prefetch", href=settings.PUBLIC_BASE_URL),
    ],
    theme=rx.theme(appearance="dark"),
    stylesheets=["/colabe.css"],
    api_transformer=api,
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
app.add_page(gpt_hub_page, route="/gpt-hub", on_load=AuthState.check_login)
app.add_page(runners_page, route="/runners", on_load=AuthState.check_login)
public_routes = {
    "/who-we-are": who_we_are_page,
    "/adapters/[adapter]": adapters_page,
    "/playbooks/[playbook]": playbooks_page,
    "/integrations/[integration]": integrations_page,
}
for lang in settings.PUBLIC_LOCALES.split(","):
    for route, page_fn in public_routes.items():
        app.add_page(
            page_fn, route=f"/{lang}{route}", on_load=SeoState.on_public_page_load
        )