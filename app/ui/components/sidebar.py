import reflex as rx
from app.ui.states.auth_state import AuthState
from app.ui.states.billing_state import BillingState
from app.ui.styles import sidebar_style, sidebar_button_style


def wallet_badge() -> rx.Component:
    return rx.el.div(
        rx.icon("gem", size=16),
        rx.el.span(BillingState.wallet_balance, class_name="font-semibold"),
        rx.el.span("coins", class_name="text-sm text-[#A9B3C1]"),
        class_name="flex items-center space-x-2 p-2 rounded-lg bg-[#0E1520] border border-[#D8B76E]/20",
    )


def user_dropdown() -> rx.Component:
    return rx.el.div(
        wallet_badge(),
        rx.el.button(
            rx.el.img(
                src="https://api.dicebear.com/9.x/initials/svg?seed="
                + AuthState.user.username,
                class_name="h-8 w-8 rounded-full",
                alt="User Avatar",
            ),
            rx.el.span(
                AuthState.user.username, class_name="hidden md:block text-[#E8F0FF]"
            ),
            rx.icon("chevron-down", size=16, class_name="hidden md:block"),
            class_name="flex items-center space-x-2 p-2 rounded-lg hover:bg-[#0E1520]",
        ),
        rx.el.button(
            "Logout",
            on_click=AuthState.logout,
            class_name="ml-4 px-4 py-2 text-sm font-medium text-[#E8F0FF] bg-[#FF3B3B]/80 rounded-lg hover:bg-[#FF3B3B]",
        ),
        class_name="flex items-center space-x-4",
    )


def sidebar_link(text: str, href: str, icon: str) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, size=20),
        rx.el.span(text),
        href=href,
        class_name=sidebar_button_style,
    )


def sidebar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.a(
                rx.icon("flask-conical", size=32, class_name="text-[#00E5FF]"),
                rx.el.span(
                    "Colabe Test Labo", class_name="text-xl font-bold text-[#E8F0FF]"
                ),
                href="/",
                class_name="flex items-center space-x-2",
            ),
            class_name="p-4 border-b border-white/10",
        ),
        rx.el.div(
            sidebar_link("Dashboard", "/", "layout-dashboard"),
            sidebar_link("Projects", "/projects", "folder-kanban"),
            sidebar_link("Test Plans", "/test-plans", "file-check"),
            sidebar_link("Live Runs", "/runs", "circle-play"),
            sidebar_link("Diffs", "/diffs", "git-compare"),
            sidebar_link("Coverage", "/quality", "pie-chart"),
            sidebar_link("Security", "/security", "shield"),
            sidebar_link("Accessibility", "/accessibility", "accessibility"),
            sidebar_link("Performance", "/performance", "gauge"),
            sidebar_link("Policies", "/policies", "gavel"),
            sidebar_link("Audit Log", "/audits", "scroll-text"),
            sidebar_link("Billing & Wallet", "/billing", "wallet"),
            sidebar_link("API & Webhooks", "/api-docs", "code"),
            sidebar_link("System Health", "/health", "heart-pulse"),
            sidebar_link("Settings", "/settings", "settings"),
            class_name="flex-grow p-4 space-y-2",
        ),
        class_name=sidebar_style,
    )