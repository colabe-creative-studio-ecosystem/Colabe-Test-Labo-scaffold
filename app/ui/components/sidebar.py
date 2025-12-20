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
                src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.user.username}",
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


def sidebar_link(text: str, href: str, icon: str, color: str) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, size=20, class_name=f"text-[{color}]"),
        rx.el.span(text, class_name=f"text-[{color}] font-medium"),
        href=href,
        class_name=f"flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 hover:bg-[{color}]/10 hover:shadow-[0_0_15px_-5px_{color}] opacity-80 hover:opacity-100",
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
            sidebar_link("Dashboard", "/", "layout-dashboard", "#00E5FF"),
            sidebar_link("Projects", "/projects", "folder-kanban", "#FF3CF7"),
            sidebar_link("Adapters", "/adapters", "puzzle", "#FFE600"),
            sidebar_link("Test Plans", "/test-plans", "file-check", "#D8B76E"),
            sidebar_link("Live Runs", "/runs", "circle-play", "#00D68F"),
            sidebar_link("Diffs", "/diffs", "git-compare", "#FFB020"),
            sidebar_link("Coverage", "/quality", "pie-chart", "#00E5FF"),
            sidebar_link("Security", "/security", "shield", "#FF3B3B"),
            sidebar_link("Accessibility", "/accessibility", "accessibility", "#FF3CF7"),
            sidebar_link("Performance", "/performance", "gauge", "#FFE600"),
            sidebar_link("Policies", "/policies", "gavel", "#D8B76E"),
            sidebar_link("Audit Log", "/audits", "scroll-text", "#00E5FF"),
            sidebar_link("Billing & Wallet", "/billing", "wallet", "#00D68F"),
            sidebar_link("API & Webhooks", "/api-docs", "code", "#FF3CF7"),
            sidebar_link("System Health", "/health", "heart-pulse", "#00D68F"),
            sidebar_link("Settings", "/settings", "settings", "#E8F0FF"),
            class_name="flex-grow p-4 space-y-2",
        ),
        class_name=sidebar_style,
    )