import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.api_docs_state import ApiDocsState
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def api_docs_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    api_docs_content(),
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


def api_docs_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "API & Webhooks",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Integrate with Colabe Test Labo using our OpenAPI specification.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "OpenAPI 3.0 Specification",
                    class_name="text-xl font-semibold text-[#E8F0FF]",
                ),
                rx.el.p(
                    "Download our OpenAPI JSON file to generate clients, or explore the API endpoints below.",
                    class_name="text-[#A9B3C1] mt-1",
                ),
                rx.el.button(
                    rx.icon("download", size=16, class_name="mr-2"),
                    "Download openapi.json",
                    on_click=rx.download(
                        data=ApiDocsState.openapi_json_str, filename="openapi.json"
                    ),
                    class_name="mt-4 inline-flex items-center px-4 py-2 bg-[#00E5FF] text-[#0A0F14] font-semibold rounded-lg hover:opacity-90",
                ),
                **card_style("cyan"),
            ),
            rx.el.div(
                rx.el.h2("API Keys", class_name="text-xl font-semibold text-[#E8F0FF]"),
                rx.el.p(
                    "API keys are scoped per-project. Manage your keys in your project settings. Authenticate by providing the key in the ",
                    rx.el.code("X-API-Key", class_name="bg-[#0A0F14] p-1 rounded"),
                    " header.",
                    class_name="text-[#A9B3C1] mt-1",
                ),
                **card_style("gold"),
            ),
            rx.el.div(
                rx.el.h2("Webhooks", class_name="text-xl font-semibold text-[#E8F0FF]"),
                rx.el.p(
                    "Configure webhooks to receive real-time updates on run events and PR statuses. See the 'webhooks' section in the OpenAPI spec for payload details.",
                    class_name="text-[#A9B3C1] mt-1",
                ),
                **card_style("magenta"),
            ),
            class_name="grid grid-cols-1 md:grid-cols-1 gap-6 p-8",
        ),
        class_name=page_content_style,
    )