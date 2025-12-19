import reflex as rx
from app.ui.components.footer import footer
from app.ui.components.sidebar import sidebar
from app.ui.states.auth_state import AuthState
from app.ui.states.audit_state import AuditState, AuditLogDisplay
from app.ui.styles import page_style, page_content_style, header_style


def audit_log_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    rx.el.main(
                        rx.el.header(
                            rx.el.div(
                                rx.el.h1(
                                    "Audit Trail",
                                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                                ),
                                rx.el.p(
                                    "A log of all significant actions within your tenant.",
                                    class_name="text-[#A9B3C1]",
                                ),
                            ),
                            class_name=header_style,
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.table(
                                    rx.el.thead(
                                        rx.el.tr(
                                            rx.el.th(
                                                "Timestamp",
                                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                                            ),
                                            rx.el.th(
                                                "User",
                                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                                            ),
                                            rx.el.th(
                                                "Action",
                                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                                            ),
                                            rx.el.th(
                                                "Details",
                                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                                            ),
                                        )
                                    ),
                                    rx.el.tbody(
                                        rx.foreach(
                                            AuditState.audit_logs, render_audit_row
                                        ),
                                        class_name="divide-y divide-white/10",
                                    ),
                                    class_name="min-w-full divide-y divide-white/10",
                                ),
                                class_name="overflow-hidden rounded-xl border border-white/10 bg-[#0E1520]",
                            ),
                            class_name="p-8 flex-1",
                        ),
                        class_name=page_content_style,
                    ),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=AuditState.load_audit_logs,
    )


def render_audit_row(log: AuditLogDisplay) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            log.timestamp,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]",
        ),
        rx.el.td(
            rx.cond(log.user, log.user.username, "System"),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]",
        ),
        rx.el.td(
            rx.el.span(
                log.action,
                class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#00E5FF]/20 text-[#00E5FF]",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm",
        ),
        rx.el.td(
            log.details, class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]"
        ),
    )