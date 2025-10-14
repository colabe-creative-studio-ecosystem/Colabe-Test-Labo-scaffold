import reflex as rx
from app.ui.states.seo_state import SeoState


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
            rx.el.header(
                rx.el.nav(
                    rx.el.a("Colabe", href="/", class_name="text-xl font-bold"),
                    rx.el.div(
                        rx.foreach(
                            SeoState.public_nav_links,
                            lambda link: rx.el.a(
                                link["text"],
                                href=link["href"],
                                class_name="text-gray-600 hover:text-gray-900",
                            ),
                        ),
                        class_name="flex items-center space-x-8",
                    ),
                    class_name="container mx-auto flex justify-between items-center p-4",
                ),
                class_name="bg-white border-b border-gray-200",
            ),
            rx.el.main(main_content, class_name="flex-grow"),
            rx.el.footer(
                rx.el.div(
                    rx.el.p("© 2024 Colabe. All rights reserved."),
                    rx.el.div(),
                    class_name="container mx-auto p-4 text-center text-gray-500",
                ),
                class_name="bg-gray-100",
            ),
            class_name="flex flex-col min-h-screen font-['Inter']",
        ),
    )