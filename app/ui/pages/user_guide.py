import reflex as rx
from app.ui.states.auth_state import AuthState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style


def user_guide_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "User Guide",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Learn how to use Colabe Test Labo.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(rx.el.p("User guide content coming soon."), class_name="p-8"),
        class_name=page_content_style,
    )


def user_guide_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(sidebar(), user_guide_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=AuthState.check_login,
    )