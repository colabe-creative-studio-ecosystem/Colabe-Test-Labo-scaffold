import reflex as rx
from typing import TypedDict
from app.ui.states.auth_state import AuthState


class EcosystemNode(TypedDict):
    id: str
    name: str
    description: str
    cta_link: str
    cta_text: str
    icon: str
    color: str


class WhoWeAreState(AuthState):
    is_modal_open: bool = False
    modal_content: EcosystemNode = {
        "id": "",
        "name": "",
        "description": "",
        "cta_link": "",
        "cta_text": "",
        "icon": "",
        "color": "gray",
    }
    ecosystem_nodes: list[EcosystemNode] = [
        {
            "id": "triggerbus",
            "name": "TriggerBus",
            "description": "The event-driven backbone of Colabe, enabling services to communicate asynchronously with guaranteed delivery and replayability.",
            "cta_link": "/ops/events",
            "cta_text": "View Event Stream",
            "icon": "webhook",
            "color": "cyan",
        },
        {
            "id": "api-center",
            "name": "API Center",
            "description": "Your hub for managing API keys, webhooks, and accessing SDKs to integrate Test Labo into your workflows programmatically.",
            "cta_link": "/api-docs",
            "cta_text": "Explore APIs",
            "icon": "code",
            "color": "magenta",
        },
        {
            "id": "gpt-hub",
            "name": "GPT Hub",
            "description": "Leverages large language models to provide intelligent autofixes, test summaries, and insights from your run data.",
            "cta_link": "/security",
            "cta_text": "See Autofix in Action",
            "icon": "brain-circuit",
            "color": "gold",
        },
        {
            "id": "payments",
            "name": "Payments",
            "description": "A secure, unified system for managing subscriptions, wallet balances, and viewing invoices across all Colabe services.",
            "cta_link": "/billing",
            "cta_text": "Manage Billing",
            "icon": "wallet",
            "color": "success",
        },
        {
            "id": "domains",
            "name": "Domains",
            "description": "Centralized management for all your domains, with automated DNS configuration for services like Test Labo.",
            "cta_link": "#",
            "cta_text": "Coming Soon",
            "icon": "globe",
            "color": "blue",
        },
        {
            "id": "seo-boosters",
            "name": "SEO Boosters",
            "description": "Analyzes performance and accessibility reports from Test Labo to provide actionable recommendations for improving your site's SEO.",
            "cta_link": "/quality",
            "cta_text": "View Quality Reports",
            "icon": "trending-up",
            "color": "warning",
        },
    ]

    @rx.event
    def open_modal(self, node: EcosystemNode):
        self.modal_content = node
        self.is_modal_open = True

    @rx.event
    def close_modal(self):
        self.is_modal_open = False