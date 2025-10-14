import reflex as rx
import reflex_enterprise as rxe
from fastapi import FastAPI
from app.ui.pages.index import index
from app.ui.pages.dashboard import dashboard_page
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
from app.ui.pages.user_guide import user_guide_page
from app.ui.pages.faq import faq_page
from app.ui.pages.ai_help import ai_help_page
from app.ui.pages.kb import (
    kb_hub_page,
    kb_article_page,
    kb_search_page,
    kb_changelog_page,
)
from app.ui.states.auth_state import AuthState
from app.core.settings import settings
from app.core import models
from app.ui.states.api_center_state import ApiCenterState

api = FastAPI()


@api.get("/api/openapi.json")
async def openapi():
    return ApiCenterState.openapi_spec


@api.get("/api/asyncapi.json")
async def asyncapi():
    return ApiCenterState.asyncapi_spec


app = rxe.App(
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
        rx.el.script(
            src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX", async_=True
        ),
        rx.el.script("""
            window.dataLayer = window.dataLayer || [];
            function gtag(){dataLayer.push(arguments);}
            gtag('js', new Date());
            gtag('config', 'G-XXXXXXXXXX');
            """),
    ],
    theme=rx.theme(appearance="dark", accent_color="cyan"),
    stylesheets=["/colabe.css"],
    api_transformer=api,
)
app.add_page(index, route="/", on_load=AuthState.page_view)
app.add_page(
    dashboard_page, route="/app", on_load=[AuthState.check_login, AuthState.page_view]
)
app.add_page(health_check_page, route="/health", on_load=AuthState.check_login)
app.add_page(login_page, route="/login")
app.add_page(register_page, route="/register")
app.add_page(audit_log_page, route="/audits", on_load=AuthState.check_login)
app.add_page(security_page, route="/security", on_load=AuthState.check_login)
app.add_page(quality_page, route="/quality", on_load=AuthState.check_login)
app.add_page(policies_page, route="/policies", on_load=AuthState.check_login)
app.add_page(billing_page, route="/billing", on_load=AuthState.check_login)
app.add_page(api_docs_page, route="/api-docs", on_load=AuthState.check_login)
app.add_page(billing_page, route="/billing", on_load=AuthState.check_login)
app.add_page(api_docs_page, route="/api-docs", on_load=AuthState.check_login)
from app.ui.pages.api_center import (
    api_center_page,
    api_rest_page,
    api_webhooks_page,
    api_sdk_page,
    api_playground_page,
    api_changelog_page,
    api_keys_page,
)
from app.ui.pages.cookie_policy import cookie_policy_page
from app.ui.pages.privacy_center import privacy_center_page
from app.ui.states.api_center_state import ApiCenterState

app.add_page(api_center_page, route="/api-center", on_load=AuthState.check_login)
app.add_page(
    api_rest_page, route="/api-center/rest", on_load=ApiCenterState.on_load_spec
)
app.add_page(
    api_webhooks_page, route="/api-center/webhooks", on_load=AuthState.check_login
)
app.add_page(api_sdk_page, route="/api-center/sdk", on_load=AuthState.check_login)
app.add_page(
    api_playground_page, route="/api-center/playground", on_load=AuthState.check_login
)
app.add_page(
    api_changelog_page, route="/api-center/changelog", on_load=AuthState.check_login
)
app.add_page(
    api_keys_page, route="/api-center/keys", on_load=ApiCenterState.load_api_keys
)
app.add_page(security_page, route="/security")
app.add_page(privacy_policy_page, route="/legal/privacy")
app.add_page(terms_and_conditions_page, route="/legal/terms")
app.add_page(cookie_policy_page, route="/legal/cookies")
app.add_page(privacy_center_page, route="/privacy-center")
app.add_page(kb_hub_page, route="/kb", on_load=AuthState.check_login)
app.add_page(kb_article_page, route="/kb/guides/[slug]", on_load=AuthState.check_login)
app.add_page(kb_search_page, route="/kb/search", on_load=AuthState.check_login)
app.add_page(kb_changelog_page, route="/kb/changelog", on_load=AuthState.check_login)
app.add_page(faq_page, route="/kb/faq", on_load=AuthState.check_login)
app.add_page(user_guide_page, route="/guide", on_load=AuthState.check_login)
app.add_page(ai_help_page, route="/help", on_load=AuthState.check_login)