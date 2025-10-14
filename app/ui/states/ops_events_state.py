import reflex as rx
import sqlmodel
from app.ui.states.auth_state import AuthState
from app.core.models import EventOutbox, RoleEnum


class OpsEventsState(AuthState):
    outbox_events: list[EventOutbox] = []
    is_admin_or_owner: bool = False

    @rx.event
    def load_events(self):
        if not self.is_logged_in or not self.user:
            return rx.redirect("/login")
        with rx.session() as session:
            role = session.exec(
                sqlmodel.select(RoleEnum)
                .join(UserRole)
                .where(UserRole.user_id == self.user.id)
            ).first()
            if role not in [RoleEnum.ADMIN, RoleEnum.OWNER]:
                self.is_admin_or_owner = False
                return rx.redirect("/")
            self.is_admin_or_owner = True
            self.outbox_events = session.exec(
                sqlmodel.select(EventOutbox)
                .order_by(sqlmodel.desc(EventOutbox.created_at))
                .limit(100)
            ).all()

    @rx.event
    def retry_event(self, event_id: int):
        with rx.session() as session:
            event = session.get(EventOutbox, event_id)
            if event:
                event.status = "pending"
                event.retry_count = 0
                session.add(event)
                session.commit()
        return OpsEventsState.load_events