"""State management for outbound messaging monitoring."""
import reflex as rx
import sqlmodel
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from app.ui.states.auth_state import AuthState
from app.core.models import (
    OutboundMessage,
    CircuitBreakerState,
    ConversationRateLimit,
    ContactCooldown,
    WorkspaceQuietHours,
)


class OutboundMessageDisplay(rx.Base):
    """Display model for outbound messages."""
    id: int
    recipient_email: str
    message_type: str
    status: str
    failure_reason: str | None = None
    sent_at: str | None = None
    created_at: str
    conversation_id: str | None = None


class CircuitBreakerDisplay(rx.Base):
    """Display model for circuit breaker status."""
    state: str
    failure_count: int
    last_failure_at: str | None = None
    circuit_opened_at: str | None = None


class QuietHoursDisplay(rx.Base):
    """Display model for quiet hours configuration."""
    enabled: bool
    start_hour: int
    end_hour: int
    timezone: str


class OutboundMessagingState(rx.State):
    """State for outbound messaging monitoring dashboard."""
    
    # Recent messages
    recent_messages: list[OutboundMessageDisplay] = []
    
    # Circuit breaker status
    circuit_breaker: CircuitBreakerDisplay | None = None
    
    # Quiet hours configuration
    quiet_hours: QuietHoursDisplay | None = None
    
    # Statistics
    total_sent_today: int = 0
    total_failed_today: int = 0
    total_blocked_today: int = 0
    
    # Filters
    show_status_filter: str = "all"  # all, sent, failed, blocked, pending
    
    # UI state
    loading: bool = False
    error_message: str = ""
    success_message: str = ""
    
    # Quiet hours form
    quiet_hours_enabled: bool = True
    quiet_hours_start: int = 22
    quiet_hours_end: int = 8
    quiet_hours_timezone: str = "UTC"
    
    @rx.event
    async def load_dashboard(self):
        """Load all dashboard data."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return rx.redirect("/login")
        
        self.loading = True
        tenant_id = auth_state.user.tenant_id
        
        with rx.session() as session:
            # Load recent messages
            query = sqlmodel.select(OutboundMessage).where(
                OutboundMessage.tenant_id == tenant_id
            )
            
            if self.show_status_filter != "all":
                query = query.where(OutboundMessage.status == self.show_status_filter)
            
            messages = session.exec(
                query.order_by(sqlmodel.desc(OutboundMessage.created_at)).limit(50)
            ).all()
            
            self.recent_messages = [
                OutboundMessageDisplay(
                    id=msg.id,
                    recipient_email=msg.recipient_email,
                    message_type=msg.message_type,
                    status=msg.status,
                    failure_reason=msg.failure_reason,
                    sent_at=msg.sent_at.isoformat() if msg.sent_at else None,
                    created_at=msg.created_at.isoformat(),
                    conversation_id=msg.conversation_id,
                )
                for msg in messages
            ]
            
            # Load circuit breaker status
            circuit = session.exec(
                sqlmodel.select(CircuitBreakerState).where(
                    CircuitBreakerState.tenant_id == tenant_id
                )
            ).first()
            
            if circuit:
                self.circuit_breaker = CircuitBreakerDisplay(
                    state=circuit.state,
                    failure_count=circuit.failure_count,
                    last_failure_at=circuit.last_failure_at.isoformat()
                    if circuit.last_failure_at
                    else None,
                    circuit_opened_at=circuit.circuit_opened_at.isoformat()
                    if circuit.circuit_opened_at
                    else None,
                )
            else:
                self.circuit_breaker = CircuitBreakerDisplay(
                    state="closed",
                    failure_count=0,
                    last_failure_at=None,
                    circuit_opened_at=None,
                )
            
            # Load quiet hours
            quiet_hours = session.exec(
                sqlmodel.select(WorkspaceQuietHours).where(
                    WorkspaceQuietHours.tenant_id == tenant_id
                )
            ).first()
            
            if quiet_hours:
                self.quiet_hours = QuietHoursDisplay(
                    enabled=quiet_hours.enabled,
                    start_hour=quiet_hours.start_hour,
                    end_hour=quiet_hours.end_hour,
                    timezone=quiet_hours.timezone,
                )
                self.quiet_hours_enabled = quiet_hours.enabled
                self.quiet_hours_start = quiet_hours.start_hour
                self.quiet_hours_end = quiet_hours.end_hour
                self.quiet_hours_timezone = quiet_hours.timezone
            else:
                self.quiet_hours = QuietHoursDisplay(
                    enabled=True,
                    start_hour=22,
                    end_hour=8,
                    timezone="UTC",
                )
            
            # Calculate statistics for today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            self.total_sent_today = session.exec(
                sqlmodel.select(sqlmodel.func.count(OutboundMessage.id)).where(
                    OutboundMessage.tenant_id == tenant_id,
                    OutboundMessage.status == "sent",
                    OutboundMessage.created_at >= today_start,
                )
            ).one()
            
            self.total_failed_today = session.exec(
                sqlmodel.select(sqlmodel.func.count(OutboundMessage.id)).where(
                    OutboundMessage.tenant_id == tenant_id,
                    OutboundMessage.status == "failed",
                    OutboundMessage.created_at >= today_start,
                )
            ).one()
            
            self.total_blocked_today = session.exec(
                sqlmodel.select(sqlmodel.func.count(OutboundMessage.id)).where(
                    OutboundMessage.tenant_id == tenant_id,
                    OutboundMessage.status == "blocked",
                    OutboundMessage.created_at >= today_start,
                )
            ).one()
        
        self.loading = False
    
    @rx.event
    async def update_quiet_hours(self):
        """Update quiet hours configuration."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return rx.redirect("/login")
        
        tenant_id = auth_state.user.tenant_id
        
        with rx.session() as session:
            quiet_hours = session.exec(
                sqlmodel.select(WorkspaceQuietHours).where(
                    WorkspaceQuietHours.tenant_id == tenant_id
                )
            ).first()
            
            if quiet_hours:
                quiet_hours.enabled = self.quiet_hours_enabled
                quiet_hours.start_hour = self.quiet_hours_start
                quiet_hours.end_hour = self.quiet_hours_end
                quiet_hours.timezone = self.quiet_hours_timezone
            else:
                quiet_hours = WorkspaceQuietHours(
                    tenant_id=tenant_id,
                    enabled=self.quiet_hours_enabled,
                    start_hour=self.quiet_hours_start,
                    end_hour=self.quiet_hours_end,
                    timezone=self.quiet_hours_timezone,
                )
                session.add(quiet_hours)
            
            session.commit()
            self.success_message = "Quiet hours updated successfully"
            
        # Reload dashboard
        await self.load_dashboard()
    
    @rx.event
    async def reset_circuit_breaker(self):
        """Manually reset the circuit breaker (admin action)."""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return rx.redirect("/login")
        
        tenant_id = auth_state.user.tenant_id
        
        with rx.session() as session:
            circuit = session.exec(
                sqlmodel.select(CircuitBreakerState).where(
                    CircuitBreakerState.tenant_id == tenant_id
                )
            ).first()
            
            if circuit:
                circuit.state = "closed"
                circuit.failure_count = 0
                circuit.circuit_opened_at = None
                circuit.last_failure_at = None
                circuit.window_start = datetime.now()
                session.commit()
                self.success_message = "Circuit breaker reset successfully"
            else:
                self.error_message = "No circuit breaker found"
        
        # Reload dashboard
        await self.load_dashboard()
    
    @rx.event
    async def change_status_filter(self, status: str):
        """Change the status filter for messages."""
        self.show_status_filter = status
        await self.load_dashboard()
