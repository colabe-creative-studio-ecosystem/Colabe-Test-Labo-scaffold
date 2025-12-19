import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style
from app.ui.states.health_state import HealthState


def health_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "System Health",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p("Status of system components.", class_name="text-[#A9B3C1]"),
            ),
            user_dropdown(),
            class_name="flex items-center justify-between p-4 border-b border-white/10",
        ),
        rx.el.div(
            rx.el.button(
                "Refresh",
                on_click=HealthState.check_health,
                class_name="mb-6 px-4 py-2 bg-[#00E5FF] text-[#0A0F14] font-semibold rounded-lg hover:opacity-90",
            ),
            rx.el.div(
                status_card("Overall Status", HealthState.health_status),
                status_card("Database", HealthState.db_status),
                status_card("Redis Cache", HealthState.redis_status),
                status_card("Background Worker", HealthState.worker_status),
                class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6",
            ),
            class_name="p-8",
        ),
        class_name="flex-1 flex flex-col",
    )


def health_check_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    health_page_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def status_card(title: str, status: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-medium text-[#E8F0FF]"),
        rx.el.div(
            rx.el.div(
                class_name=rx.cond(
                    status.contains("OK"),
                    "h-3 w-3 rounded-full bg-green-500",
                    rx.cond(
                        status.contains("Error") | status.contains("Failed"),
                        "h-3 w-3 rounded-full bg-red-500",
                        "h-3 w-3 rounded-full bg-yellow-500",
                    ),
                )
            ),
            rx.el.p(
                status,
                class_name=rx.cond(
                    status.contains("OK"),
                    "text-green-600 font-semibold",
                    rx.cond(
                        status.contains("Error") | status.contains("Failed"),
                        "text-red-600 font-semibold",
                        "text-yellow-600 font-semibold",
                    ),
                ),
            ),
            class_name="mt-2 flex items-center space-x-2",
        ),
        class_name="bg-[#0E1520] p-6 rounded-xl border border-white/10 shadow-sm",
    )