import reflex as rx
from app.ui.states.runner_state import RunnerState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style
from app.core.models import RunnerPool, Runner


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
                rx.el.h2(
                    "Runner Pools", class_name="text-xl font-semibold text-text-primary"
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Name"),
                                rx.el.th("Region"),
                                rx.el.th("Type"),
                                rx.el.th("Capacity"),
                                rx.el.th("Status"),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(RunnerState.runner_pools, render_pool_row)
                        ),
                        class_name="min-w-full divide-y divide-gray-700",
                    ),
                    class_name="mt-4 overflow-x-auto rounded-lg border border-white/10",
                ),
                class_name="bg-bg-elevated p-6 rounded-xl border border-white/20",
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )


def render_pool_row(pool: RunnerPool) -> rx.Component:
    return rx.el.tr(
        rx.el.td(pool.name),
        rx.el.td(pool.region),
        rx.el.td(
            rx.el.span(
                pool.pool_type,
                class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-cyan-900 text-cyan-300",
            )
        ),
        rx.el.td(f"{pool.runners.length()}/{pool.max_runners}"),
        rx.el.td(
            rx.el.div(
                rx.el.div(class_name="h-2 w-2 rounded-full bg-green-500"),
                rx.el.span("Healthy"),
                class_name="flex items-center gap-2",
            )
        ),
        class_name="text-sm",
    )