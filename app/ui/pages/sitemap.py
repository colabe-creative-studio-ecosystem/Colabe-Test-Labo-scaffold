import reflex as rx
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def sitemap_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.header(
                rx.el.div(
                    rx.el.h1(
                        "Sitemap",
                        class_name="text-2xl font-bold text-text-primary title-gradient",
                    ),
                    rx.el.p(
                        "An overview of all pages in the application.",
                        class_name="text-text-secondary",
                    ),
                ),
                class_name=header_style,
            ),
            rx.el.div(
                sitemap_category(
                    "Core Application",
                    [
                        ("/", "Dashboard"),
                        ("/projects", "Projects"),
                        ("/test-plans", "Test Plans"),
                        ("/runs", "Live Runs"),
                        ("/quality", "Quality & Coverage"),
                        ("/security", "Security"),
                        ("/policies", "Policies"),
                    ],
                ),
                sitemap_category(
                    "Account & Billing",
                    [
                        ("/billing", "Billing & Wallet"),
                        ("/audits", "Audit Log"),
                        ("/settings", "Settings"),
                    ],
                ),
                sitemap_category(
                    "Operations & Info",
                    [
                        ("/api-docs", "API & Webhooks"),
                        ("/ops/events", "Operational Events"),
                        ("/health", "System Health"),
                        ("/who-we-are", "Who We Are"),
                    ],
                ),
                sitemap_category(
                    "Static & Legal",
                    [
                        ("/sitemap.xml", "XML Sitemap"),
                        ("/robots.txt", "Robots.txt"),
                        ("/privacy", "Privacy Policy (soon)"),
                        ("/terms", "Terms & Conditions (soon)"),
                    ],
                ),
                class_name="p-8 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
            ),
            class_name=page_content_style,
        ),
        class_name=page_style,
    )


def sitemap_category(title: str, links: list[tuple[str, str]]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-semibold text-text-primary mb-3"),
        rx.el.div(
            rx.foreach(links, lambda link: sitemap_link(link[0], link[1])),
            class_name="space-y-2",
        ),
        **card_style("cyan"),
        class_name="p-4",
    )


def sitemap_link(href: str, text: str) -> rx.Component:
    return rx.el.a(
        rx.icon("link-2", class_name="mr-2 text-text-secondary"),
        text,
        href=href,
        class_name="flex items-center text-text-secondary hover:text-accent-cyan",
        target=rx.cond(href.contains("."), "_blank", "_self"),
    )