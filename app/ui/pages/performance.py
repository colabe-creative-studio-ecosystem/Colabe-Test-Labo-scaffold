import reflex as rx
from app.ui.components.footer import footer
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.states.auth_state import AuthState
from app.ui.styles import page_style, page_content_style, header_style


def performance_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    rx.el.main(
                        rx.el.header(
                            rx.el.div(
                                rx.el.h1(
                                    "Performance",
                                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                                ),
                                rx.el.p(
                                    "Performance metrics and analysis.",
                                    class_name="text-[#A9B3C1]",
                                ),
                            ),
                            user_dropdown(),
                            class_name=header_style,
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Performance page content coming soon...",
                                class_name="text-[#A9B3C1]",
                            ),
                            class_name="p-8",
                        ),
                        class_name=page_content_style,
                    ),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )