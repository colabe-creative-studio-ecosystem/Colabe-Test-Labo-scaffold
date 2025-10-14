import reflex as rx
from app.ui.states.auth_state import AuthState
from app.ui.states.billing_state import BillingState
from app.ui.styles import (
    card_style,
    sidebar_style,
    sidebar_button_style,
    page_style,
    header_style,
    page_content_style,
)


def wallet_badge() -> rx.Component:
    return rx.el.div(
        rx.icon("gem", size=16),
        rx.text(BillingState.wallet_balance, class_name="font-semibold"),
        rx.text("coins", class_name="text-sm text-text-secondary"),
        class_name="flex items-center space-x-2 p-2 rounded-lg bg-bg-elevated border border-accent-gold/20",
    )


def tenant_switcher() -> rx.Component:
    return rx.radix.dropdown_menu.root(
        rx.radix.dropdown_menu.trigger(
            rx.el.button(
                rx.icon("building", class_name="hidden md:block"),
                rx.text(
                    AuthState.current_tenant.name,
                    class_name="hidden md:block text-text-primary",
                ),
                rx.icon("chevrons-up-down", size=16, class_name="hidden md:block"),
                class_name="flex items-center space-x-2 p-2 rounded-lg hover:bg-bg-elevated",
            )
        ),
        rx.radix.dropdown_menu.content(
            rx.foreach(
                AuthState.memberships,
                lambda m: rx.radix.dropdown_menu.item(
                    m.tenant.name, on_click=lambda: AuthState.switch_tenant(m.tenant_id)
                ),
            )
        ),
    )


def user_dropdown() -> rx.Component:
    return rx.el.div(
        wallet_badge(),
        tenant_switcher(),
        rx.radix.dropdown_menu.root(
            rx.radix.dropdown_menu.trigger(
                rx.el.button(
                    rx.image(
                        src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.user.username}",
                        class_name="h-8 w-8 rounded-full",
                    ),
                    rx.el.span(
                        AuthState.user.username,
                        class_name="hidden md:block text-text-primary",
                    ),
                    rx.icon("chevron-down", size=16, class_name="hidden md:block"),
                    class_name="flex items-center space-x-2 p-2 rounded-lg hover:bg-bg-elevated",
                )
            ),
            rx.radix.dropdown_menu.content(
                rx.radix.dropdown_menu.item(
                    "Profile", on_click=rx.redirect("/profile")
                ),
                rx.radix.dropdown_menu.separator(),
                rx.radix.dropdown_menu.item(
                    "Logout", on_click=AuthState.logout, color="red"
                ),
            ),
        ),
        class_name="flex items-center space-x-4",
    )


def sidebar_link(text: str, href: str, icon: str) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, size=20),
        rx.text(text),
        href=href,
        class_name=sidebar_button_style,
    )


def sidebar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.a(
                rx.icon("flask-conical", size=32, class_name="text-accent-cyan"),
                rx.text(
                    "Colabe Test Labo", class_name="text-xl font-bold text-text-primary"
                ),
                href="/",
                class_name="flex items-center space-x-2",
            ),
            class_name="p-4 border-b border-white/10",
        ),
        rx.el.div(
            sidebar_link("Dashboard", "/", "layout-dashboard"),
            sidebar_link("Projects", "/projects", "folder-kanban"),
            sidebar_link("Quality", "/quality", "pie-chart"),
            sidebar_link("Security", "/security", "shield"),
            sidebar_link("Policies", "/policies", "gavel"),
            sidebar_link("Members", "/members", "users"),
            sidebar_link("Audit Log", "/audits", "scroll-text"),
            sidebar_link("Billing", "/billing", "wallet"),
            sidebar_link("API", "/api-docs", "code"),
            class_name="flex-grow p-4 space-y-2",
        ),
        rx.el.div(
            sidebar_link("System Health", "/health", "heart-pulse"),
            rx.cond(
                AuthState.is_admin,
                rx.el.div(
                    sidebar_link("Admin Tenants", "/admin/tenants", "shield-half"),
                    sidebar_link("Ops Dashboard", "/ops/dashboard", "server"),
                    sidebar_link("Ops Events", "/ops/events", "webhook"),
                ),
            ),
            class_name="p-4 space-y-2 border-t border-white/10",
        ),
        class_name=sidebar_style,
    )


def main_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Dashboard",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    f"Welcome back, {AuthState.user.username}!",
                    class_name="text-text-secondary",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Colabe Test Labo",
                    class_name="text-5xl font-bold tracking-tighter text-text-primary title-gradient",
                ),
                rx.el.p(
                    "The environment is ready. Start building your test automation platform.",
                    class_name="mt-4 text-lg text-text-secondary max-w-2xl text-center",
                ),
                rx.el.p(
                    f"Current Role: {AuthState.current_role.to_string()}",
                    class_name="mt-4 text-md text-accent-cyan bg-accent-cyan/10 px-3 py-1 rounded-full",
                ),
                class_name="flex flex-col items-center justify-center text-center p-16",
                **card_style("cyan"),
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )


def index() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(sidebar(), main_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-text-primary"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=[AuthState.check_login, BillingState.load_wallet],
    )