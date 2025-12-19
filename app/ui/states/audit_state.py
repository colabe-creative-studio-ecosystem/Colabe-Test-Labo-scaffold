import reflex as rx
import sqlmodel
from sqlalchemy.orm import selectinload
from app.ui.states.auth_state import AuthState
from app.core.models import AuditLog


class AuditUserDisplay(rx.Base):
    username: str


class AuditLogDisplay(rx.Base):
    timestamp: str
    user: AuditUserDisplay | None = None
    action: str
    details: str | None = None


class AuditState(rx.State):
    audit_logs: list[AuditLogDisplay] = []

    @rx.event
    async def load_audit_logs(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return rx.redirect("/login")
        with rx.session() as session:
            logs = session.exec(
                sqlmodel.select(AuditLog)
                .where(AuditLog.tenant_id == auth_state.user.tenant_id)
                .options(selectinload(AuditLog.user))
                .order_by(sqlmodel.desc(AuditLog.timestamp))
            ).all()
            self.audit_logs = [
                AuditLogDisplay(
                    timestamp=log.timestamp.isoformat(),
                    user=AuditUserDisplay(username=log.user.username)
                    if log.user
                    else None,
                    action=log.action,
                    details=log.details,
                )
                for log in logs
            ]