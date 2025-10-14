import reflex as rx
from app.ui.states.auth_state import AuthState
from app.core.models import AuditLog, User
import sqlmodel
from datetime import datetime


class AuditState(AuthState):
    audit_logs: list[AuditLog] = []

    @rx.event
    def load_audit_logs(self):
        with rx.session() as session:
            if not self.user:
                return rx.redirect("/login")
            logs = session.exec(
                sqlmodel.select(AuditLog)
                .where(AuditLog.tenant_id == self.user.tenant_id)
                .options(sqlmodel.selectinload(AuditLog.user))
                .order_by(sqlmodel.desc(AuditLog.timestamp))
            ).all()
            self.audit_logs = logs


def audit_log_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Audit Trail",
                class_name="text-3xl font-bold text-text-primary title-gradient",
            ),
            rx.el.p(
                "A log of all significant actions within your tenant.",
                class_name="text-text-secondary mt-1",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Timestamp",
                                class_name="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "User",
                                class_name="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Action",
                                class_name="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Details",
                                class_name="px-6 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(AuditState.audit_logs, render_audit_row),
                        class_name="bg-bg-elevated divide-y divide-white/10",
                    ),
                    class_name="min-w-full divide-y divide-white/10",
                ),
                class_name="shadow overflow-hidden border-b border-white/10 sm:rounded-lg",
            ),
            class_name="mt-8",
        ),
        on_mount=AuditState.load_audit_logs,
        class_name="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 font-['Inter']",
    )


def render_audit_row(log: AuditLog) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            log.timestamp.to_string(),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-text-secondary",
        ),
        rx.el.td(
            rx.cond(log.user, log.user.username, "System"),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-text-primary",
        ),
        rx.el.td(
            rx.el.span(
                log.action,
                class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-accent-cyan/20 text-accent-cyan",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm",
        ),
        rx.el.td(
            log.details,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-text-secondary",
        ),
        class_name="border-b border-white/10",
    )