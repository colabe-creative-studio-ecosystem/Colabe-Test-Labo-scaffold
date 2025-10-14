import reflex as rx
from app.ui.states.api_center_state import ApiCenterState
from app.ui.states.auth_state import AuthState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def api_center_layout(title: str, subtitle: str, *children) -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.main(
                    rx.el.header(
                        rx.el.div(
                            rx.el.h1(
                                title,
                                class_name="text-2xl font-bold text-text-primary title-gradient",
                            ),
                            rx.el.p(subtitle, class_name="text-text-secondary"),
                        ),
                        class_name=header_style,
                    ),
                    api_center_tabs(),
                    rx.el.div(*children, class_name="p-8"),
                    class_name=page_content_style,
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def api_center_tabs() -> rx.Component:
    tabs = {
        "Overview": "/api-center",
        "REST API": "/api-center/rest",
        "API Keys": "/api-center/keys",
        "Webhooks": "/api-center/webhooks",
        "SDKs": "/api-center/sdk",
        "Playground": "/api-center/playground",
        "Changelog": "/api-center/changelog",
    }

    def tab_button(text: str, href: str):
        return rx.el.a(
            text,
            href=href,
            class_name=rx.cond(
                ApiCenterState.router.page.path == href,
                "px-4 py-2 font-semibold text-accent-cyan border-b-2 border-accent-cyan",
                "px-4 py-2 font-medium text-text-secondary hover:text-text-primary",
            ),
        )

    return rx.el.div(
        rx.foreach(list(tabs.items()), lambda item: tab_button(item[0], item[1])),
        class_name="flex border-b border-white/10 px-4",
    )


def api_center_page() -> rx.Component:
    return api_center_layout(
        "API Center",
        "Integrate, automate, and build on top of Colabe Test Labo.",
        rx.el.div(
            rx.el.a(
                rx.icon("binary", class_name="text-accent-cyan", size=24),
                rx.el.h3("REST API", class_name="font-semibold mt-2"),
                rx.el.p(
                    "Explore our OpenAPI spec.",
                    class_name="text-sm text-text-secondary",
                ),
                href="/api-center/rest",
                **card_style("cyan"),
            ),
            rx.el.a(
                rx.icon("key-round", class_name="text-accent-gold", size=24),
                rx.el.h3("API Keys", class_name="font-semibold mt-2"),
                rx.el.p(
                    "Manage your personal access tokens.",
                    class_name="text-sm text-text-secondary",
                ),
                href="/api-center/keys",
                **card_style("gold"),
            ),
            rx.el.a(
                rx.icon("webhook", class_name="text-accent-magenta", size=24),
                rx.el.h3("Webhooks", class_name="font-semibold mt-2"),
                rx.el.p(
                    "Subscribe to real-time events.",
                    class_name="text-sm text-text-secondary",
                ),
                href="/api-center/webhooks",
                **card_style("magenta"),
            ),
            rx.el.a(
                rx.icon("package", class_name="text-accent-yellow", size=24),
                rx.el.h3("SDKs", class_name="font-semibold mt-2"),
                rx.el.p(
                    "Typed clients for Python & TS.",
                    class_name="text-sm text-text-secondary",
                ),
                href="/api-center/sdk",
                **card_style("yellow"),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
        ),
    )


def api_rest_page() -> rx.Component:
    return api_center_layout(
        "REST API",
        "Explore endpoints, schemas, and responses.",
        rx.el.button(
            rx.icon("download", class_name="mr-2", size=16),
            "Download openapi.json",
            on_click=rx.download(url="/api/openapi.json", filename="openapi.json"),
            class_name="mb-6 inline-flex items-center px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
        ),
        rx.el.div(id="swagger-ui", class_name="w-full"),
        rx.el.script(src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"),
        rx.el.script(
            src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js"
        ),
        rx.el.link(
            rel="stylesheet", href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"
        ),
        rx.el.script("""
            window.onload = function() {
              window.ui = SwaggerUIBundle({
                url: "/api/openapi.json",
                dom_id: '#swagger-ui',
                deepLinking: true,
                presets: [
                  SwaggerUIBundle.presets.apis,
                  SwaggerUIStandalonePreset
                ],
                plugins: [
                  SwaggerUIBundle.plugins.DownloadUrl
                ],
                layout: "StandaloneLayout"
              });
            };
        """),
    )


def api_keys_page() -> rx.Component:
    return api_center_layout(
        "API Keys",
        "Manage Personal Access Tokens (PATs) for your account.",
        rx.cond(
            ApiCenterState.newly_created_key,
            rx.el.div(
                rx.el.h3(
                    "New Key Generated", class_name="font-semibold text-accent-yellow"
                ),
                rx.el.p(
                    "This is the only time you will see this key. Store it securely.",
                    class_name="text-sm",
                ),
                rx.el.code(
                    ApiCenterState.newly_created_key,
                    class_name="block p-3 bg-bg-base rounded-lg mt-2",
                ),
                rx.el.button(
                    "Acknowledge",
                    on_click=ApiCenterState.clear_new_key,
                    class_name="mt-4 px-4 py-2 bg-accent-yellow text-bg-base rounded-lg",
                ),
                class_name="p-4 mb-6 border border-accent-yellow/30 bg-accent-yellow/10 rounded-lg",
            ),
        ),
        rx.el.form(
            rx.el.h3("Create New API Key", class_name="text-lg font-bold mb-4"),
            rx.el.div(
                rx.el.label("Key Name", class_name="font-medium"),
                rx.el.input(
                    name="name",
                    placeholder="e.g., 'CI Server Key'",
                    class_name="w-full mt-1 bg-bg-base border border-white/20 rounded-lg p-2",
                ),
                class_name="mb-4",
            ),
            rx.el.div(
                rx.el.label("Scopes", class_name="font-medium"),
                rx.el.div(
                    rx.foreach(
                        ApiCenterState.available_scopes,
                        lambda scope: rx.el.label(
                            rx.el.input(
                                type="checkbox",
                                name="scopes",
                                class_name="mr-2",
                                default_value=scope,
                                key=scope,
                            ),
                            scope,
                            class_name="flex items-center",
                        ),
                    ),
                    class_name="grid grid-cols-2 md:grid-cols-4 gap-2 mt-2",
                ),
            ),
            rx.el.button(
                "Create Key",
                type="submit",
                class_name="mt-6 px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
            ),
            on_submit=ApiCenterState.create_api_key,
            reset_on_submit=True,
            **card_style("cyan"),
        ),
        rx.el.div(
            rx.el.h3("Existing Keys", class_name="text-lg font-bold mt-8 mb-4"),
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Name"),
                        rx.el.th("Prefix"),
                        rx.el.th("Scopes"),
                        rx.el.th("Last Used"),
                        rx.el.th("Created"),
                        rx.el.th(""),
                    )
                ),
                rx.el.tbody(rx.foreach(ApiCenterState.api_keys, render_api_key_row)),
                class_name="w-full text-left",
            ),
            class_name="mt-8",
        ),
    )


def render_api_key_row(key: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(key["name"]),
        rx.el.td(rx.el.code(key["prefix"])),
        rx.el.td(key["scopes"]),
        rx.el.td(key["last_used_at"]),
        rx.el.td(key["created_at"]),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", size=16),
                on_click=lambda: ApiCenterState.revoke_api_key(key["id"]),
                class_name="p-2 text-danger hover:bg-danger/20 rounded-full",
            )
        ),
        class_name="border-b border-white/10 hover:bg-white/5",
    )


def api_webhooks_page() -> rx.Component:
    return api_center_layout(
        "Webhooks",
        "Get real-time event notifications via HTTP callbacks.",
        rx.el.p("Webhooks documentation coming soon."),
    )


def api_sdk_page() -> rx.Component:
    return api_center_layout(
        "SDKs",
        "Interact with the Colabe API using our typed SDKs.",
        rx.el.p("SDK documentation coming soon."),
    )


def api_playground_page() -> rx.Component:
    return api_center_layout(
        "Playground",
        "Experiment with the API in a secure, sandboxed environment.",
        rx.el.p("API Playground coming soon."),
    )


def api_changelog_page() -> rx.Component:
    return api_center_layout(
        "Changelog",
        "Stay up-to-date with the latest changes to our API.",
        rx.el.p("API Changelog coming soon."),
    )