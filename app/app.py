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
from app.ui.pages.public.home import home_page
from app.ui.pages.public.pricing import pricing_page
from app.ui.pages.public.features import features_page
from app.ui.pages.public.solutions import solutions_page
from app.ui.pages.public.compare import compare_page
from app.ui.pages.public.demos import demos_page
from app.ui.pages.public.customers import customers_page, customer_profile_page
from app.ui.pages.public.contact import contact_page
from app.ui.pages.public.partners import partners_page
from app.ui.pages.public.who_we_are import who_we_are_page
from app.ui.pages.public.adapters import adapters_page
from app.ui.pages.public.playbooks import playbooks_page
from app.ui.pages.public.integrations import integrations_page
from app.ui.pages.runners import runners_page
from app.ui.pages.public.sitemap import sitemap_index
from app.ui.states.auth_state import AuthState
from app.ui.states.seo_state import SeoState
from app.ui.states.marketing_state import MarketingState
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
app.add_page(index, route="/app", on_load=AuthState.check_login)
app.add_page(health_check_page, route="/app/health", on_load=AuthState.check_login)
app.add_page(audit_log_page, route="/app/audits", on_load=AuthState.check_login)
app.add_page(security_page, route="/app/security", on_load=AuthState.check_login)
app.add_page(quality_page, route="/app/quality", on_load=AuthState.check_login)
app.add_page(policies_page, route="/app/policies", on_load=AuthState.check_login)
app.add_page(billing_page, route="/app/billing", on_load=AuthState.check_login)
app.add_page(api_docs_page, route="/app/api-docs", on_load=AuthState.check_login)
app.add_page(gpt_hub_page, route="/app/gpt-hub", on_load=AuthState.check_login)
app.add_page(runners_page, route="/app/runners", on_load=AuthState.check_login)
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
public_routes = {
    "/": home_page,
    "/pricing": pricing_page,
    "/features": features_page,
    "/solutions/[solution]": solutions_page,
    "/compare/[tool]": compare_page,
    "/demos": demos_page,
    "/customers": customers_page,
    "/customers/[slug]": customer_profile_page,
    "/contact": contact_page,
    "/partners": partners_page,
    "/who-we-are": who_we_are_page,
    "/adapters/[adapter]": adapters_page,
    "/playbooks/[playbook]": playbooks_page,
    "/integrations/[integration]": integrations_page,
}
on_load_events = [SeoState.on_public_page_load, MarketingState.on_load]
for route, page_fn in public_routes.items():
    app.add_page(page_fn, route=route, on_load=on_load_events)
for lang in settings.PUBLIC_LOCALES.split(","):
    for route, page_fn in public_routes.items():
        if lang == settings.EDGE_REGION_DEFAULT and route == "/":
            continue
        prefixed_route = f"/{lang}{route}" if route != "/" else f"/{lang}"
        app.add_page(page_fn, route=prefixed_route, on_load=on_load_events)