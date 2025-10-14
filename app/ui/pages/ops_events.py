import reflex as rx
from app.ui.states.ops_events_state import OpsEventsState
from app.core.models import EventOutbox
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style


def ops_events_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        ops_events_content(),
        class_name=page_style,
        on_mount=OpsEventsState.load_events,
    )


def ops_events_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.h1(
                "Operational Events", class_name="text-2xl font-bold title-gradient"
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.cond(
                OpsEventsState.is_admin,
                rx.el.div(
                    rx.el.button(
                        "Refresh",
                        on_click=OpsEventsState.load_events,
                        class_name="px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90 mb-4",
                    ),
                    rx.el.h3("Outbox Events", class_name="text-lg font-semibold mb-2"),
                    rx.el.div(
                        rx.el.table(
                            rx.el.thead(
                                rx.el.tr(
                                    rx.el.th("Created At", class_name="p-3 text-left"),
                                    rx.el.th("Event ID", class_name="p-3 text-left"),
                                    rx.el.th("Topic", class_name="p-3 text-left"),
                                    rx.el.th("Status", class_name="p-3 text-left"),
                                    rx.el.th("Retries", class_name="p-3 text-left"),
                                    rx.el.th("Actions", class_name="p-3 text-left"),
                                )
                            ),
                            rx.el.tbody(
                                rx.foreach(
                                    OpsEventsState.outbox_events, render_event_row
                                )
                            ),
                        ),
                        class_name="overflow-x-auto rounded-lg border border-white/10",
                    ),
                ),
                rx.el.div(
                    "Access Denied. Admin or Owner role required.",
                    class_name="p-8 text-danger",
                ),
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
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
        class_name="border-t border-white/10 hover:bg-bg-elevated",
    )