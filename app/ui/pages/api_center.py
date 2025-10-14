import reflex as rx
from app.ui.states.api_center_state import ApiCenterState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.core.models import ApiKey


def api_center_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ApiCenterState.is_logged_in,
            rx.el.div(sidebar(), api_center_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def api_center_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "API Center",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Integrate, automate, and extend Colabe Test Labo.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            tabs(),
            rx.match(
                ApiCenterState.active_tab,
                ("rest", rest_api_tab()),
                ("webhooks", webhooks_tab()),
                ("sdks", sdks_tab()),
                ("keys", api_keys_tab()),
                ("playground", playground_tab()),
                ("changelog", changelog_tab()),
            ),
            class_name="p-8 space-y-8",
        ),
        class_name=page_content_style,
    )


def tabs() -> rx.Component:
    return rx.el.div(
        tab_button("REST API", "rest", "server"),
        tab_button("Webhooks", "webhooks", "webhook"),
        tab_button("SDKs", "sdks", "binary"),
        tab_button("API Keys", "keys", "key-round"),
        tab_button("Playground", "playground", "terminal"),
        tab_button("Changelog", "changelog", "history"),
        class_name="flex space-x-1 border-b border-white/10",
    )


def tab_button(text: str, tab_name: str, icon: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, size=16),
        text,
        on_click=ApiCenterState.set_active_tab(tab_name),
        class_name=rx.cond(
            ApiCenterState.active_tab == tab_name,
            "border-accent-cyan text-accent-cyan",
            "border-transparent text-text-secondary hover:text-text-primary",
        )
        + " flex items-center gap-2 px-4 py-3 border-b-2 text-sm font-medium transition-colors",
    )


def rest_api_tab() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "OpenAPI 3.0 Specification",
            class_name="text-xl font-semibold text-text-primary",
        ),
        rx.el.p(
            "Our entire API is documented below. You can also ",
            rx.el.a(
                "download the OpenAPI JSON file",
                on_click=rx.download(
                    data=ApiCenterState.openapi_json_str, filename="openapi.json"
                ),
                class_name="text-accent-cyan hover:underline",
            ),
            " to generate clients.",
            class_name="text-text-secondary mt-1",
        ),
        rx.el.pre(
            rx.el.code(ApiCenterState.openapi_json_str, class_name="language-json"),
            class_name="mt-4 p-4 rounded-lg bg-bg-base border border-white/10 max-h-[60vh] overflow-auto text-sm",
        ),
    )


def webhooks_tab() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Webhooks", class_name="text-xl font-semibold text-text-primary"),
        rx.el.p(
            "Receive real-time notifications for events in your tenant.",
            class_name="text-text-secondary mt-1",
        ),
        rx.el.h3(
            "Available Events",
            class_name="text-lg font-semibold text-text-primary mt-6 mb-2",
        ),
        rx.el.ul(
            rx.foreach(
                ApiCenterState.webhook_events,
                lambda event: rx.el.li(
                    rx.el.code(event, class_name="bg-bg-base p-1 rounded")
                ),
            ),
            class_name="list-disc list-inside text-text-secondary space-y-1",
        ),
        rx.el.h3(
            "Signature Verification",
            class_name="text-lg font-semibold text-text-primary mt-6 mb-2",
        ),
        rx.el.p(
            "Verify webhook signatures to ensure they originated from Colabe. We use an HMAC-SHA256 signature computed over the raw request body and timestamp, included in the ",
            rx.el.code("X-Colabe-Signature", class_name="bg-bg-base p-1 rounded"),
            " and ",
            rx.el.code("X-Colabe-Timestamp", class_name="bg-bg-base p-1 rounded"),
            " headers.",
            class_name="text-text-secondary",
        ),
        rx.el.h4(
            "Python Example", class_name="text-md font-semibold text-text-primary mt-4"
        ),
        rx.el.pre(
            rx.el.code(ApiCenterState.webhook_py_example, class_name="language-python"),
            class_name="mt-2 p-4 rounded-lg bg-bg-base border border-white/10 text-sm",
        ),
        rx.el.h4(
            "TypeScript Example",
            class_name="text-md font-semibold text-text-primary mt-4",
        ),
        rx.el.pre(
            rx.el.code(
                ApiCenterState.webhook_ts_example, class_name="language-typescript"
            ),
            class_name="mt-2 p-4 rounded-lg bg-bg-base border border-white/10 text-sm",
        ),
        class_name="space-y-4",
    )


def sdks_tab() -> rx.Component:
    return rx.el.div(
        rx.el.h2("SDKs", class_name="text-xl font-semibold text-text-primary"),
        rx.el.p(
            "Install our typed SDKs to interact with the Colabe API idiomatically.",
            class_name="text-text-secondary mt-1",
        ),
        rx.el.h3("Python", class_name="text-lg font-semibold text-text-primary mt-6"),
        rx.el.pre(
            rx.el.code("pip install colabe_testlabo", class_name="language-bash"),
            class_name="mt-2 p-4 rounded-lg bg-bg-base border border-white/10 text-sm",
        ),
        rx.el.pre(
            rx.el.code(ApiCenterState.sdk_py_example, class_name="language-python"),
            class_name="mt-2 p-4 rounded-lg bg-bg-base border border-white/10 text-sm",
        ),
        rx.el.h3(
            "TypeScript", class_name="text-lg font-semibold text-text-primary mt-6"
        ),
        rx.el.pre(
            rx.el.code("npm install @colabe/testlabo", class_name="language-bash"),
            class_name="mt-2 p-4 rounded-lg bg-bg-base border border-white/10 text-sm",
        ),
        rx.el.pre(
            rx.el.code(ApiCenterState.sdk_ts_example, class_name="language-typescript"),
            class_name="mt-2 p-4 rounded-lg bg-bg-base border border-white/10 text-sm",
        ),
        class_name="space-y-4",
    )


def api_keys_tab() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Personal Access Tokens (API Keys)",
            class_name="text-xl font-semibold text-text-primary",
        ),
        rx.el.p(
            "Generate API keys to authenticate requests from your scripts and applications.",
            class_name="text-text-secondary mt-1",
        ),
        rx.el.div(
            rx.el.h3(
                "Generate New Key",
                class_name="text-lg font-semibold text-text-primary mb-4",
            ),
            rx.el.form(
                rx.el.input(
                    name="name",
                    placeholder="Key Name (e.g., 'CI-CD Key')",
                    class_name="w-full p-2 rounded-lg bg-bg-base border border-white/10",
                ),
                rx.el.input(
                    name="scopes",
                    placeholder="Scopes (e.g., 'runs.read,runs.write')",
                    class_name="w-full p-2 rounded-lg bg-bg-base border border-white/10",
                ),
                rx.el.button("Generate Key", type="submit"),
                on_submit=ApiCenterState.create_api_key,
                class_name="space-y-4",
            ),
            rx.cond(
                ApiCenterState.new_api_key,
                rx.el.div(
                    rx.el.p(
                        "New key generated. Copy it now, you won't see it again:",
                        class_name="text-warning font-semibold",
                    ),
                    rx.el.code(
                        ApiCenterState.new_api_key,
                        class_name="mt-2 p-2 block bg-bg-base text-accent-cyan rounded",
                    ),
                    class_name="mt-4 p-4 border border-warning/50 rounded-lg bg-warning/10",
                ),
            ),
            class_name="mt-6",
        ),
        rx.el.div(
            rx.el.h3(
                "Your Keys", class_name="text-lg font-semibold text-text-primary mb-4"
            ),
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Name"),
                        rx.el.th("Prefix"),
                        rx.el.th("Scopes"),
                        rx.el.th("Created"),
                        rx.el.th("Actions"),
                        class_name="text-left text-sm text-text-secondary",
                    )
                ),
                rx.el.tbody(rx.foreach(ApiCenterState.api_keys, render_api_key_row)),
                class_name="w-full",
            ),
            class_name="mt-6",
        ),
        class_name="space-y-4",
    )


def render_api_key_row(key: ApiKey) -> rx.Component:
    return rx.el.tr(
        rx.el.td(key.name),
        rx.el.td(rx.el.code(key.key_prefix, class_name="bg-bg-base p-1 rounded")),
        rx.el.td(key.scopes),
        rx.el.td(key.created_at.to_string()),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", size=16),
                on_click=lambda: ApiCenterState.revoke_api_key(key.id),
                class_name="text-danger hover:opacity-80",
                variant="ghost",
            )
        ),
        class_name="text-sm border-b border-white/10",
    )


def playground_tab() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Playground", class_name="text-xl font-semibold text-text-primary"),
        rx.el.p(
            "Secure, tenant-scoped API playground. (Coming Soon)",
            class_name="text-text-secondary mt-1",
        ),
        **card_style("magenta"),
    )


def changelog_tab() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Changelog", class_name="text-xl font-semibold text-text-primary"),
        rx.el.p(
            "Versioned API changes will be displayed here. (Coming Soon)",
            class_name="text-text-secondary mt-1",
        ),
        **card_style("gold"),
    )