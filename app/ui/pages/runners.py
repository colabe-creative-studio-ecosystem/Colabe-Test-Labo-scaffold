import reflex as rx
from app.ui.states.runner_state import RunnerState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style
from app.core.models import RunnerPool, Runner
from typing import Any


def runners_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            RunnerState.is_logged_in,
            rx.el.div(sidebar(), runners_page_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=RunnerState.load_runner_data,
    )


def runners_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Runners & Pools",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Manage your private runners and device cloud integrations.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Runner Pools",
                        class_name="text-xl font-semibold text-text-primary mb-4",
                    ),
                    rx.el.div(
                        rx.foreach(RunnerState.runner_pools, pool_list_item),
                        class_name="space-y-2",
                    ),
                    class_name="w-1/3 pr-4 border-r border-white/10",
                ),
                rx.el.div(
                    rx.cond(
                        RunnerState.selected_pool,
                        pool_details_view(),
                        rx.el.div(
                            rx.icon(
                                "arrow-left", class_name="mr-2 text-text-secondary"
                            ),
                            rx.el.p(
                                "Select a pool to see details",
                                class_name="text-text-secondary",
                            ),
                            class_name="flex items-center justify-center h-full",
                        ),
                    ),
                    class_name="w-2/3 pl-4",
                ),
                class_name="flex p-8",
            )
        ),
        class_name=page_content_style,
    )


def pool_list_item(pool: RunnerPool) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.el.div(
                rx.el.p(pool.name, class_name="font-semibold"),
                rx.el.p(
                    f"{pool.region} • {pool.pool_type}",
                    class_name="text-sm text-text-secondary capitalize",
                ),
                class_name="flex-grow text-left",
            ),
            rx.el.div(
                rx.el.p(f"{pool.runners.length()}/{pool.max_runners}"),
                rx.icon("server", size=16),
                class_name="flex items-center gap-2 text-sm",
            ),
        ),
        on_click=lambda: RunnerState.select_pool(pool.id),
        class_name=rx.cond(
            RunnerState.selected_pool_id == pool.id,
            "w-full flex items-center justify-between p-3 rounded-lg bg-accent-cyan/20 border border-accent-cyan text-text-primary",
            "w-full flex items-center justify-between p-3 rounded-lg bg-bg-elevated hover:bg-white/10 border border-transparent",
        ),
    )


def pool_details_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.button(
                "Runners",
                on_click=RunnerState.set_active_tab("runners"),
                class_name=rx.cond(
                    RunnerState.active_tab == "runners",
                    "px-4 py-2 font-semibold text-accent-cyan border-b-2 border-accent-cyan",
                    "px-4 py-2 font-semibold text-text-secondary",
                ),
            ),
            rx.el.button(
                "Install",
                on_click=RunnerState.set_active_tab("install"),
                class_name=rx.cond(
                    RunnerState.active_tab == "install",
                    "px-4 py-2 font-semibold text-accent-cyan border-b-2 border-accent-cyan",
                    "px-4 py-2 font-semibold text-text-secondary",
                ),
            ),
            class_name="flex border-b border-white/10",
        ),
        rx.el.div(
            rx.match(
                RunnerState.active_tab,
                ("runners", runners_tab()),
                ("install", install_tab()),
                rx.el.div(),
            ),
            class_name="p-4",
        ),
    )


def runners_tab() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Hostname"),
                        rx.el.th("OS / Arch"),
                        rx.el.th("IP Address"),
                        rx.el.th("Agent Version"),
                        rx.el.th("Status"),
                        rx.el.th("Last Heartbeat"),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(RunnerState.runners_in_selected_pool, render_runner_row)
                ),
                class_name="min-w-full divide-y divide-gray-700",
            ),
            class_name="mt-4 overflow-x-auto rounded-lg border border-white/10",
        )
    )


def install_tab() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Runner Enrollment", class_name="text-lg font-semibold text-text-primary"
        ),
        rx.el.p(
            "Use the token below to enroll new runners into this pool. This token is valid for 1 hour.",
            class_name="text-sm text-text-secondary mt-1",
        ),
        rx.el.div(
            rx.el.input(
                is_read_only=True,
                class_name="bg-bg-base text-text-primary p-2 rounded-l-md w-full font-mono",
                default_value=RunnerState.enrollment_token,
                key=RunnerState.enrollment_token,
            ),
            rx.el.button(
                rx.icon("copy", size=16),
                on_click=rx.set_clipboard(RunnerState.enrollment_token),
                class_name="p-3 bg-white/20 hover:bg-white/30 rounded-r-md",
            ),
            class_name="flex mt-4",
        ),
        rx.el.button(
            "Generate New Token",
            on_click=RunnerState.generate_enrollment_token,
            class_name="mt-2 px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
        ),
        class_name="space-y-6",
    )


def render_runner_row(runner: Runner) -> rx.Component:
    return rx.el.tr(
        rx.el.td(runner.hostname),
        rx.el.td(f"{runner.os} / {runner.arch}"),
        rx.el.td(runner.ip_address),
        rx.el.td(runner.agent_version),
        rx.el.td(
            rx.el.div(
                rx.el.div(
                    class_name=rx.cond(
                        runner.status == "online",
                        "h-2 w-2 rounded-full bg-green-500",
                        "h-2 w-2 rounded-full bg-red-500",
                    )
                ),
                rx.el.span(runner.status),
                class_name="flex items-center gap-2 capitalize",
            )
        ),
        rx.el.td(runner.last_heartbeat.to_string()),
        class_name="text-sm",
    )