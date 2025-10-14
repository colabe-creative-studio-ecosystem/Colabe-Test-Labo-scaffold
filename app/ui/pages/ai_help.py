import reflex as rx
from app.ui.pages.index import sidebar
from app.ui.states.auth_state import AuthState
from app.ui.styles import page_style, page_content_style, header_style, card_style


def ai_help_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(sidebar(), ai_help_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def ai_help_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "AI Support Copilot",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Your intelligent assistant for navigating Colabe Test Labo.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("bot", size=48, class_name="text-accent-cyan"),
                    rx.el.h2(
                        "Coming Soon",
                        class_name="text-3xl font-bold text-text-primary mt-4",
                    ),
                    rx.el.p(
                        "We are working on an interactive AI assistant that will provide context-aware help, guided tours, and quick answers to your questions.",
                        class_name="text-text-secondary mt-2 max-w-xl text-center",
                    ),
                ),
                class_name="flex flex-col items-center justify-center text-center p-16",
                **card_style("cyan"),
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )