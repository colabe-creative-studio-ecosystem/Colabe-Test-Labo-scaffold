import reflex as rx
from app.ui.states.ops_events_state import OpsEventsState
from app.core.models import EventOutbox
from app.ui.pages.index import sidebar


def ops_events_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            OpsEventsState.is_logged_in,
            rx.el.div(sidebar(), ops_events_content(), class_name="flex min-h-screen"),
            rx.el.p("Unauthorized"),
        ),
        on_mount=OpsEventsState.load_events,
        class_name="colabe-bg text-text-primary",
    )


def ops_events_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.h1(
                "Operational Events",
                class_name="text-2xl font-bold text-text-primary title-gradient",
            ),
            class_name="p-4 border-b border-white/10",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    "Refresh",
                    on_click=OpsEventsState.load_events,
                    class_name="px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
                ),
                class_name="flex items-center space-x-4 mb-4",
            ),
            rx.el.div(
                rx.el.h3("Outbox Events", class_name="text-lg font-semibold mb-2"),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th("Created At"),
                                rx.el.th("Event ID"),
                                rx.el.th("Topic"),
                                rx.el.th("Status"),
                                rx.el.th("Retries"),
                                rx.el.th("Actions"),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(OpsEventsState.outbox_events, render_event_row)
                        ),
                        class_name="min-w-full divide-y divide-gray-700",
                    ),
                    class_name="overflow-x-auto rounded-lg border border-white/10",
                ),
                class_name="p-4 bg-bg-elevated rounded-lg",
            ),
            class_name="p-8",
        ),
        class_name="flex-1",
    )


def render_event_row(event: EventOutbox) -> rx.Component:
    return rx.el.tr(
        rx.el.td(event.created_at.to_string(), class_name="p-3 text-sm"),
        rx.el.td(event.event_id, class_name="p-3 text-sm font-mono"),
        rx.el.td(event.topic, class_name="p-3 text-sm"),
        rx.el.td(
            rx.el.span(
                event.status,
                class_name=rx.cond(
                    event.status == "sent",
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-success/20 text-success",
                    rx.cond(
                        event.status == "failed",
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-danger/20 text-danger",
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-warning/20 text-warning",
                    ),
                ),
            ),
            class_name="p-3 text-sm",
        ),
        rx.el.td(event.retry_count.to_string(), class_name="p-3 text-sm"),
        rx.el.td(
            rx.el.button(
                "Retry",
                on_click=lambda: OpsEventsState.retry_event(event.id),
                size="1",
                class_name="px-2 py-1 text-xs font-medium text-bg-base bg-accent-cyan rounded-md hover:opacity-90",
            ),
            class_name="p-3 text-sm",
        ),
    )