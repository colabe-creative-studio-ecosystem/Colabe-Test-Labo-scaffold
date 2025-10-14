import reflex as rx
import sqlmodel
import csv
import io
from app.ui.states.auth_state import AuthState
from app.core.models import AuditEvent, User


class AuditState(AuthState):
    audit_logs: list[AuditEvent] = []
    filter_actor: str = ""
    filter_action: str = ""
    filter_date: str = ""

    @rx.event
    def load_audit_logs(self):
        if not self.is_logged_in or not self.current_tenant:
            return rx.redirect("/login")
        with rx.session() as session:
            query = (
                sqlmodel.select(AuditEvent)
                .where(AuditEvent.tenant_id == self.current_tenant.id)
                .options(sqlmodel.selectinload(AuditEvent.actor))
                .order_by(sqlmodel.desc(AuditEvent.timestamp))
            )
            self.audit_logs = session.exec(query).all()

    @rx.var
    def filtered_logs(self) -> list[AuditEvent]:
        logs = self.audit_logs
        if self.filter_actor:
            logs = [
                log
                for log in logs
                if log.actor and self.filter_actor.lower() in log.actor.username.lower()
            ]
        if self.filter_action:
            logs = [
                log for log in logs if self.filter_action.lower() in log.action.lower()
            ]
        if self.filter_date:
            logs = [
                log
                for log in logs
                if log.timestamp.strftime("%Y-%m-%d") == self.filter_date
            ]
        return logs

    @rx.event
    def export_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "timestamp",
                "actor_username",
                "action",
                "resource_crn",
                "ip_address",
                "before_json",
                "after_json",
            ]
        )
        for log in self.filtered_logs:
            writer.writerow(
                [
                    log.timestamp.isoformat(),
                    log.actor.username if log.actor else "System",
                    log.action,
                    log.resource_crn,
                    log.ip_address,
                    log.before_json,
                    log.after_json,
                ]
            )
        csv_data = output.getvalue()
        return rx.download(data=csv_data.encode("utf-8"), filename="audit_log.csv")