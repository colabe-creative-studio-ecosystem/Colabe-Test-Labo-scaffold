import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.auth_state import AuthState
from app.ui.states.billing_state import BillingState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import card_style, page_style, header_style, page_content_style


def main_content() -> rx.Component:
    style = card_style("cyan")
    style["class_name"] = (
        style["class_name"]
        + " flex flex-col items-center justify-center text-center p-16"
    )
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Dashboard",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Welcome back, " + AuthState.user.username + "!",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Colabe Test Labo",
                    class_name="text-5xl font-bold tracking-tighter text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "The environment is ready. Start building your test automation platform.",
                    class_name="mt-4 text-lg text-[#A9B3C1] max-w-2xl text-center",
                ),
                rx.el.p(
                    "You are logged in with role: " + AuthState.current_user_role,
                    class_name="mt-4 text-md text-[#00E5FF] bg-[#00E5FF]/10 px-3 py-1 rounded-full",
                ),
                **style,
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )


def index() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    main_content(), footer(), class_name="flex-1 flex flex-col min-w-0"
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=BillingState.load_wallet,
    )