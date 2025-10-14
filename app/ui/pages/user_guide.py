import reflex as rx
from app.ui.states.kb_state import KBState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style


def render_guide_section(section: dict) -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            section["title"],
            class_name="text-2xl font-semibold text-text-primary mt-8 mb-4 border-b border-white/10 pb-2",
        ),
        rx.el.p(section["content"], class_name="text-text-secondary"),
        rx.foreach(section["subsections"], render_guide_subsection),
    )


def render_guide_subsection(section: dict) -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            section["title"],
            class_name="text-xl font-semibold text-text-primary mt-6 mb-3",
        ),
        rx.el.p(section["content"], class_name="text-text-secondary"),
        class_name="ml-4 pl-4 border-l border-white/10",
    )


def user_guide_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            KBState.is_logged_in,
            rx.el.div(sidebar(), user_guide_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def user_guide_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "User Guide",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "A comprehensive guide to getting started with Colabe Test Labo.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.foreach(KBState.user_guide_content, render_guide_section),
            class_name="p-8 max-w-4xl mx-auto",
        ),
        class_name=f"{page_content_style} overflow-y-auto",
    )