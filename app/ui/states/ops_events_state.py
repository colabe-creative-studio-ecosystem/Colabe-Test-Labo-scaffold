import reflex as rx
import sqlmodel
from app.ui.states.auth_state import AuthState
from app.core.models import EventOutbox, RoleEnum


class OpsEventsState(AuthState):
    outbox_events: list[EventOutbox] = []

    @rx.event
    def load_events(self):
        if not self.is_admin:
            return rx.redirect("/")
        with rx.session() as session:
            self.outbox_events = session.exec(
                sqlmodel.select(EventOutbox)
                .order_by(sqlmodel.desc(EventOutbox.created_at))
                .limit(100)
            ).all()

    @rx.event
    def retry_event(self, event_id: int):
        if not self.is_admin:
            return rx.toast("Permission denied.")
        with rx.session() as session:
            event = session.get(EventOutbox, event_id)
            if event:
                event.status = "pending"
                event.retry_count = 0
                session.add(event)
                session.commit()
        return OpsEventsState.load_events