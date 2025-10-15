import reflex as rx
from app.ui.states.seo_state import SeoState
from app.ui.states.marketing_state import MarketingState
from app.core.settings import settings


def public_header() -> rx.Component:
    return rx.el.header(
        rx.el.nav(
            rx.el.a(
                rx.icon("flask-conical", size=32, class_name="text-accent-cyan"),
                "Colabe",
                href=MarketingState.home_link,
                class_name="flex items-center gap-2 text-xl font-bold text-gray-900",
            ),
            rx.el.div(
                rx.foreach(
                    MarketingState.header_links,
                    lambda link: rx.el.a(
                        link["text"],
                        href=link["href"],
                        class_name="text-gray-600 hover:text-gray-900 font-medium",
                    ),
                ),
                class_name="hidden md:flex items-center space-x-8",
            ),
            rx.el.div(
                rx.el.a(
                    "Log in",
                    href="/login",
                    class_name="text-gray-600 hover:text-gray-900 font-medium",
                ),
                rx.el.a(
                    "Start for Free",
                    href="/register",
                    class_name="px-4 py-2 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600",
                ),
                class_name="flex items-center space-x-4",
            ),
            class_name="container mx-auto flex justify-between items-center p-4",
        ),
        class_name="bg-white border-b border-gray-200 sticky top-0 z-50",
    )


def public_footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.p("© 2024 Colabe. All rights reserved."),
            rx.el.div(
                rx.el.a(
                    "Privacy Policy",
                    href="/legal/privacy",
                    class_name="hover:underline",
                ),
                rx.el.a(
                    "Terms of Service",
                    href="/legal/terms",
                    class_name="hover:underline",
                ),
                rx.el.select(
                    [
                        rx.el.option(lang.upper(), value=lang)
                        for lang in settings.PUBLIC_LOCALES.split(",")
                    ],
                    value=MarketingState.current_lang,
                    on_change=MarketingState.set_language,
                ),
                class_name="flex items-center gap-4 text-sm text-gray-500",
            ),
            class_name="container mx-auto p-8 flex justify-between items-center",
        ),
        class_name="bg-gray-100",
    )


def public_page_layout(main_content: rx.Component) -> rx.Component:
    return rx.fragment(
        rx.el.title(SeoState.meta_title),
        rx.el.meta(name="description", content=SeoState.meta_description),
        rx.el.link(rel="canonical", href=SeoState.canonical_url),
        rx.foreach(
            SeoState.hreflang_links,
            lambda link: rx.el.link(
                rel=link["rel"], href=link["href"], hreflang=link["hreflang"]
            ),
        ),
        rx.el.meta(property="og:title", content=SeoState.og_title),
        rx.el.meta(property="og:description", content=SeoState.og_description),
        rx.el.meta(property="og:image", content=SeoState.og_image),
        rx.el.meta(property="og:url", content=SeoState.canonical_url),
        rx.el.meta(name="twitter:card", content="summary_large_image"),
        rx.el.div(
            public_header(),
            rx.el.main(main_content, class_name="flex-grow bg-white"),
            public_footer(),
            class_name="flex flex-col min-h-screen font-['Inter']",
        ),
    )