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


def user_dropdown() -> rx.Component:
    return rx.el.div(
        wallet_badge(),
        rx.el.button(
            rx.image(
                src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.user.username}",
                class_name="h-8 w-8 rounded-full",
            ),
            rx.el.span(
                AuthState.user.username, class_name="hidden md:block text-text-primary"
            ),
            rx.icon("chevron-down", size=16, class_name="hidden md:block"),
            class_name="flex items-center space-x-2 p-2 rounded-lg hover:bg-bg-elevated transition-colors duration-200",
        ),
        rx.el.button(
            "Logout",
            on_click=AuthState.logout,
            class_name="ml-4 px-4 py-2 text-sm font-medium text-text-primary bg-danger/80 rounded-lg hover:bg-danger transition-colors duration-200",
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
            sidebar_link("Dashboard", "/app", "layout-dashboard"),
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
            rx.el.div(class_name="flex-grow"),
            sidebar_link("User Guide", "/guide", "book-open"),
            sidebar_link("FAQ", "/faq", "circle-plus"),
            sidebar_link("AI Help", "/help", "sparkles"),
            class_name="flex-grow p-4 space-y-2 flex flex-col",
        ),
        class_name=sidebar_style,
    )


def landing_header() -> rx.Component:
    return rx.el.header(
        rx.el.div(
            rx.el.a(
                rx.icon("flask-conical", size=32, class_name="text-accent-cyan"),
                rx.el.h1("Colabe Test Labo", class_name="text-xl font-bold"),
                href="/",
                class_name="flex items-center space-x-2 text-text-primary",
            ),
            rx.el.nav(
                rx.el.a("Docs", href="/guide", class_name="hover:text-accent-cyan"),
                rx.el.a(
                    "API Center", href="/api-docs", class_name="hover:text-accent-cyan"
                ),
                rx.el.a("Contact", href="#", class_name="hover:text-accent-cyan"),
                class_name="hidden md:flex items-center space-x-6 text-sm font-medium",
            ),
            rx.cond(
                AuthState.is_logged_in,
                rx.el.a(
                    "Go to App",
                    href="/app",
                    class_name="px-4 py-2 bg-accent-cyan text-bg-base rounded-lg font-semibold hover:opacity-90 transition-opacity",
                ),
                rx.el.a(
                    "Get Started",
                    href="/login",
                    on_click=lambda: AuthState.cta_clicked("login_landing_header"),
                    class_name="px-4 py-2 bg-accent-cyan text-bg-base rounded-lg font-semibold hover:opacity-90 transition-opacity",
                ),
            ),
            class_name="container mx-auto flex items-center justify-between p-4",
        ),
        class_name="sticky top-0 z-50 bg-bg-base/80 backdrop-blur-md border-b border-white/10",
    )


def hero_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h1(
                "AI Test Labo for Every Stack.",
                class_name="text-5xl md:text-7xl font-bold tracking-tighter title-gradient",
            ),
            rx.el.p(
                "Find bugs, enforce budgets, and ship autofix PRs—fully Colabe-integrated.",
                class_name="mt-4 text-lg md:text-xl text-text-secondary max-w-2xl text-center",
            ),
            rx.el.div(
                rx.el.a(
                    "Get Started (SSO)",
                    href="/login",
                    on_click=lambda: AuthState.cta_clicked("get_started_hero"),
                    class_name="px-6 py-3 bg-accent-cyan text-bg-base rounded-lg font-semibold hover:opacity-90 transition-opacity",
                ),
                rx.el.a(
                    "Run Demo Sweep",
                    href="#",
                    on_click=lambda: AuthState.cta_clicked("demo_sweep_hero"),
                    class_name="px-6 py-3 bg-bg-elevated border border-white/20 text-text-primary rounded-lg font-semibold hover:bg-white/5 transition-colors",
                ),
                class_name="mt-8 flex flex-col sm:flex-row items-center space-y-4 sm:space-y-0 sm:space-x-4",
            ),
            class_name="relative z-10 flex flex-col items-center justify-center text-center p-8",
        ),
        class_name="relative min-h-[60vh] flex items-center justify-center overflow-hidden",
    )


def trust_badges() -> rx.Component:
    badges = [
        "github",
        "gitlab",
        "git-branch-plus",
        "play",
        "lightbulb",
        "smartphone",
        "shield-check",
        "package",
        "bug",
    ]
    return rx.el.div(
        rx.el.p(
            "Trusted by teams, compatible with your stack",
            class_name="text-sm text-text-secondary mb-6",
        ),
        rx.el.div(
            rx.foreach(
                badges,
                lambda icon: rx.icon(
                    icon,
                    size=32,
                    class_name="text-text-secondary hover:text-text-primary transition-colors",
                ),
            ),
            class_name="flex flex-wrap justify-center items-center gap-8",
        ),
        class_name="py-16 text-center",
    )


def value_prop_card(
    icon: str, title: str, description: str, accent: str
) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, size=24, class_name=f"text-accent-{accent}"),
        rx.el.h3(title, class_name="text-xl font-semibold mt-4 text-text-primary"),
        rx.el.p(description, class_name="mt-2 text-text-secondary"),
        class_name="flex flex-col p-6",
        **card_style(accent),
    )


def value_props_section() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            value_prop_card(
                "git-pull-request-arrow",
                "Autofix PRs",
                "Minimal diffs with policy gates.",
                "cyan",
            ),
            value_prop_card(
                "blinds", "Cross-Stack Adapters", "Web, Mobile, and Backend.", "magenta"
            ),
            value_prop_card(
                "combine",
                "Budgets that Enforce",
                "Perf, A11y, Security, & Coverage.",
                "yellow",
            ),
            value_prop_card(
                "wallet",
                "Coins + Subscriptions",
                "Integrated with Colabe Payments.",
                "gold",
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8",
        ),
        class_name="container mx-auto px-4 py-16",
    )


def footer() -> rx.Component:
    links = {
        "Company": [
            ("Who We Are", "#"),
            ("Privacy", "/privacy"),
            ("T&C", "/terms"),
            ("Contact", "#"),
        ],
        "Resources": [
            ("API Center", "/api-docs"),
            ("Status", "/health"),
            ("Security", "/security"),
            ("Compliance", "#"),
        ],
    }
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.a(
                    rx.icon("flask-conical", size=32, class_name="text-accent-cyan"),
                    rx.el.p("Colabe Test Labo", class_name="font-bold"),
                    href="/",
                    class_name="flex items-center space-x-2 text-text-primary",
                ),
                rx.el.p(
                    "© 2024 Colabe. All rights reserved.",
                    class_name="text-sm text-text-secondary mt-4",
                ),
                class_name="max-w-xs",
            ),
            rx.el.div(
                rx.foreach(
                    list(links.items()),
                    lambda item: rx.el.div(
                        rx.el.h4(
                            item[0], class_name="font-semibold text-text-primary mb-4"
                        ),
                        rx.el.ul(
                            rx.foreach(
                                item[1],
                                lambda link: rx.el.li(
                                    rx.el.a(
                                        link[0],
                                        href=link[1],
                                        class_name="hover:text-accent-cyan transition-colors",
                                    )
                                ),
                            ),
                            class_name="space-y-2",
                        ),
                        class_name="text-text-secondary text-sm",
                    ),
                ),
                class_name="grid grid-cols-2 gap-8",
            ),
            class_name="container mx-auto grid grid-cols-1 md:grid-cols-3 gap-12 p-8",
        ),
        class_name="bg-bg-elevated border-t border-white/10 mt-24",
    )


def landing_page() -> rx.Component:
    return rx.el.div(
        landing_header(),
        rx.el.main(hero_section(), trust_badges(), value_props_section()),
        footer(),
        class_name="colabe-bg min-h-screen text-text-primary font-['Inter']",
    )


def index() -> rx.Component:
    return rx.el.div(landing_page(), on_mount=AuthState.check_login_for_redirect)