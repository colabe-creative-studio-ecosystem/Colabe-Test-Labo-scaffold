import reflex as rx
from app.ui.states.audit_state import AuditState
from app.core.models import AuditEvent
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style


def audit_log_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        audit_content(),
        class_name=page_style,
        on_mount=AuditState.load_audit_logs,
    )


def audit_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.h1("Audit Trail", class_name="text-2xl font-bold title-gradient"),
            rx.el.p(
                "A log of all significant actions within your tenant.",
                class_name="text-text-secondary",
            ),
            class_name=header_style,
        ),
        rx.el.div(audit_filters(), audit_table(), class_name="p-8 space-y-6"),
        class_name=page_content_style,
    )


def audit_filters() -> rx.Component:
    return rx.el.div(
        rx.el.input(
            placeholder="Filter by actor...",
            on_change=AuditState.set_filter_actor,
            class_name="p-2 rounded-lg bg-bg-base border border-white/20",
        ),
        rx.el.input(
            placeholder="Filter by action...",
            on_change=AuditState.set_filter_action,
            class_name="p-2 rounded-lg bg-bg-base border border-white/20",
        ),
        rx.el.input(
            type="date",
            on_change=AuditState.set_filter_date,
            class_name="p-2 rounded-lg bg-bg-base border border-white/20",
        ),
        rx.el.button(
            "Export CSV",
            on_click=AuditState.export_csv,
            class_name="px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
        ),
        class_name="grid grid-cols-1 md:grid-cols-4 gap-4 items-center",
    )


def audit_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Timestamp", class_name="p-3 text-left"),
                    rx.el.th("Actor", class_name="p-3 text-left"),
                    rx.el.th("Action", class_name="p-3 text-left"),
                    rx.el.th("Resource CRN", class_name="p-3 text-left"),
                    rx.el.th("IP Address", class_name="p-3 text-left"),
                )
            ),
            rx.el.tbody(rx.foreach(AuditState.filtered_logs, render_audit_row)),
        ),
        class_name="overflow-x-auto rounded-lg border border-white/10",
    )


def render_audit_row(event: AuditEvent) -> rx.Component:
    return rx.el.tr(
        rx.el.td(event.timestamp.to_string(), class_name="p-3 text-sm"),
        rx.el.td(
            rx.cond(event.actor, event.actor.username, "System"),
            class_name="p-3 text-sm",
        ),
        rx.el.td(
            rx.el.span(
                event.action,
                class_name="px-2 py-1 text-xs font-semibold rounded-full bg-accent-cyan/20 text-accent-cyan",
            ),
            class_name="p-3",
        ),
        rx.el.td(event.resource_crn, class_name="p-3 text-sm font-mono"),
        rx.el.td(event.ip_address, class_name="p-3 text-sm font-mono"),
        class_name="border-t border-white/10 hover:bg-bg-elevated",
    )