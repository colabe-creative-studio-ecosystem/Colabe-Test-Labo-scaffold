import reflex as rx
import sqlmodel
from typing import Optional, TypedDict
from app.ui.states.auth_state import AuthState
from app.core.models import (
    Ticket,
    TicketMessage,
    Runbook,
    SLAPolicy,
    TicketStatus,
    TicketSeverity,
    TicketPriority,
    TicketChannel,
    TicketAuthorType,
)
from datetime import datetime
from app.integrations import triggerbus


class SupportState(AuthState):
    tickets: list[Ticket] = []
    runbooks: list[Runbook] = []
    sla_policies: list[SLAPolicy] = []
    selected_ticket: Optional[Ticket] = None
    new_ticket_subject: str = ""
    new_ticket_body: str = ""
    new_ticket_severity: str = TicketSeverity.SEV4.value
    active_tab: str = "tickets"

    @rx.event
    def on_support_page_load(self):
        if not self.is_logged_in:
            return rx.redirect("/login")
        self._log_audit("support.hub.view")
        triggerbus.handle_incoming_event(
            {
                "topic": "ops.synthetics.failed",
                "payload": {
                    "check_name": "Public API Health",
                    "region": "us-east-1",
                    "error": "503 Service Unavailable",
                },
            }
        )
        yield SupportState.load_tickets
        yield SupportState.load_runbooks
        yield SupportState.load_sla_policies

    @rx.event
    def on_ticket_detail_load(self):
        ticket_id = self.router.page.params.get("ticket_id")
        if ticket_id:
            self.load_ticket_details(int(ticket_id))

    @rx.event
    def load_tickets(self):
        with rx.session() as session:
            if not self.user:
                return
            self.tickets = session.exec(
                sqlmodel.select(Ticket)
                .where(Ticket.tenant_id == self.user.tenant_id)
                .order_by(sqlmodel.desc(Ticket.opened_at))
            ).all()

    @rx.event
    def load_runbooks(self):
        with rx.session() as session:
            self.runbooks = session.exec(sqlmodel.select(Runbook)).all()

    @rx.event
    def load_sla_policies(self):
        with rx.session() as session:
            self.sla_policies = session.exec(sqlmodel.select(SLAPolicy)).all()

    @rx.event
    def load_ticket_details(self, ticket_id: int):
        with rx.session() as session:
            if not self.user:
                return
            ticket = session.exec(
                sqlmodel.select(Ticket)
                .where(Ticket.id == ticket_id, Ticket.tenant_id == self.user.tenant_id)
                .options(sqlmodel.selectinload(Ticket.messages))
            ).first()
            if ticket:
                self.selected_ticket = ticket
                self._log_audit(
                    "support.ticket.view", details=f"ticket_id: {ticket_id}"
                )

    @rx.event
    def create_ticket(self, form_data: dict):
        subject = form_data.get("subject")
        body = form_data.get("body")
        severity = form_data.get("severity", TicketSeverity.SEV4.value)
        if not self.user or not subject or (not body):
            return rx.toast("Subject and description are required.", duration=3000)
        with rx.session() as session:
            new_ticket = Ticket(
                tenant_id=self.user.tenant_id,
                subject=subject,
                channel=TicketChannel.WEB,
                priority=TicketPriority.NORMAL,
                severity=TicketSeverity(severity),
                status=TicketStatus.NEW,
                language=self.current_lang,
            )
            session.add(new_ticket)
            session.commit()
            session.refresh(new_ticket)
            initial_message = TicketMessage(
                ticket_id=new_ticket.id,
                author_type=TicketAuthorType.USER,
                author_id=self.user.id,
                body_markdown=body,
            )
            session.add(initial_message)
            session.commit()
            ticket_data = {
                "id": new_ticket.id,
                "subject": new_ticket.subject,
                "status": new_ticket.status.value,
                "severity": new_ticket.severity.value,
                "channel": new_ticket.channel.value,
                "tenant_id": new_ticket.tenant_id,
            }
            triggerbus.publish("support.ticket.created", ticket_data)
            self._log_audit(
                "support.ticket.created", details=f"ticket_id: {new_ticket.id}"
            )
        self.set_active_tab("tickets")
        self.load_tickets()
        return rx.toast("Ticket created successfully!", duration=3000)

    @rx.event
    def create_auto_ticket(
        self,
        subject: str,
        body: str,
        severity: TicketSeverity,
        related_crns: list[str] | None = None,
    ):
        if not self.user:
            return
        with rx.session() as session:
            auto_ticket = Ticket(
                tenant_id=self.user.tenant_id,
                subject=subject,
                channel=TicketChannel.AUTOTICKET,
                priority=TicketPriority.HIGH,
                severity=severity,
                status=TicketStatus.NEW,
                language="en",
                related_crns=related_crns or [],
            )
            session.add(auto_ticket)
            session.commit()
            session.refresh(auto_ticket)
            message = TicketMessage(
                ticket_id=auto_ticket.id,
                author_type=TicketAuthorType.SYSTEM,
                body_markdown=body,
            )
            session.add(message)
            session.commit()
            ticket_data = {
                "id": auto_ticket.id,
                "subject": auto_ticket.subject,
                "status": auto_ticket.status.value,
                "severity": auto_ticket.severity.value,
                "channel": auto_ticket.channel.value,
                "tenant_id": auto_ticket.tenant_id,
            }
            triggerbus.publish("support.auto_ticket.opened", ticket_data)
            self._log_audit(
                "support.auto_ticket.opened", details=f"ticket_id: {auto_ticket.id}"
            )
            self.load_tickets()

    @rx.event
    def update_ticket_status(self, ticket_id: int, new_status_str: str):
        with rx.session() as session:
            ticket = session.get(Ticket, ticket_id)
            if not ticket or ticket.tenant_id != self.user.tenant_id:
                return rx.toast("Ticket not found or permission denied.", duration=3000)
            new_status = TicketStatus(new_status_str)
            ticket.status = new_status
            if new_status == TicketStatus.RESOLVED:
                ticket.resolved_at = datetime.utcnow()
            elif new_status == TicketStatus.CLOSED:
                if not ticket.resolved_at:
                    ticket.resolved_at = datetime.utcnow()
            session.add(ticket)
            session.commit()
            session.refresh(ticket)
            self.selected_ticket = ticket
            self.load_tickets()
            ticket_data = {"id": ticket.id, "status": ticket.status.value}
            triggerbus.publish("support.ticket.updated", ticket_data)
            if new_status == TicketStatus.RESOLVED:
                triggerbus.publish("support.ticket.resolved", ticket_data)
            elif new_status == TicketStatus.CLOSED:
                triggerbus.publish("support.ticket.closed", ticket_data)
            self._log_audit(
                "support.ticket.status.changed",
                details=f"ticket_id: {ticket.id}, new_status: {new_status.value}",
            )
        return rx.toast(f"Ticket status updated to {new_status_str}.", duration=3000)

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab

    @rx.var
    def severities(self) -> list[str]:
        return [s.value for s in TicketSeverity]