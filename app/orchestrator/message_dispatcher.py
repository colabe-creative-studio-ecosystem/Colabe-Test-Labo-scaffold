"""
Message Dispatcher Service with Outbound Sending Guardrails.

This service enforces:
- Per-conversation send limits (e.g., max 4 messages / 60 seconds)
- Quiet hours per workspace
- Cooldown per contact
- Circuit breaker: if >N failures in 10 minutes, disable live sending and alert admin
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlmodel import Session, select
import pytz

from app.core.models import (
    OutboundMessage,
    ConversationRateLimit,
    ContactCooldown,
    WorkspaceQuietHours,
    CircuitBreakerState,
    Tenant,
    User,
    AuditLog,
)

logger = logging.getLogger(__name__)


class GuardrailViolation(Exception):
    """Raised when a guardrail check fails."""
    def __init__(self, reason: str, suggested_fix: str):
        self.reason = reason
        self.suggested_fix = suggested_fix
        super().__init__(reason)


class MessageDispatcherConfig:
    """Configuration for the message dispatcher."""
    # Rate limiting
    MAX_MESSAGES_PER_CONVERSATION_WINDOW = 4
    CONVERSATION_WINDOW_SECONDS = 60
    
    # Contact cooldown
    DEFAULT_CONTACT_COOLDOWN_SECONDS = 300  # 5 minutes
    
    # Circuit breaker
    CIRCUIT_BREAKER_FAILURE_THRESHOLD = 10
    CIRCUIT_BREAKER_WINDOW_MINUTES = 10
    CIRCUIT_BREAKER_RECOVERY_SECONDS = 300  # 5 minutes before trying half_open
    
    # Admin notification cooldown (don't spam admins)
    ADMIN_NOTIFICATION_COOLDOWN_MINUTES = 60


class MessageDispatcher:
    """Dispatcher service that enforces outbound sending guardrails."""
    
    def __init__(self, db_session: Session, config: Optional[MessageDispatcherConfig] = None):
        self.db = db_session
        self.config = config or MessageDispatcherConfig()
    
    def can_send_message(
        self,
        tenant_id: int,
        recipient_email: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if a message can be sent based on all guardrails.
        
        Returns:
            Tuple[can_send, reason, suggested_fix]
        """
        try:
            # Check circuit breaker first (most critical)
            self._check_circuit_breaker(tenant_id)
            
            # Check quiet hours
            self._check_quiet_hours(tenant_id)
            
            # Check conversation rate limit
            if conversation_id:
                self._check_conversation_rate_limit(tenant_id, conversation_id)
            
            # Check contact cooldown
            self._check_contact_cooldown(tenant_id, recipient_email)
            
            return True, None, None
            
        except GuardrailViolation as e:
            logger.warning(
                f"Guardrail violation for tenant {tenant_id}: {e.reason}. "
                f"Suggested fix: {e.suggested_fix}"
            )
            return False, e.reason, e.suggested_fix
    
    def _check_circuit_breaker(self, tenant_id: int):
        """Check if circuit breaker is open for this tenant."""
        circuit_state = self.db.exec(
            select(CircuitBreakerState).where(
                CircuitBreakerState.tenant_id == tenant_id
            )
        ).first()
        
        if not circuit_state:
            # Initialize circuit breaker for tenant
            circuit_state = CircuitBreakerState(
                tenant_id=tenant_id,
                state="closed",
                failure_count=0,
                window_start=datetime.now(),
            )
            self.db.add(circuit_state)
            self.db.commit()
            return
        
        # Check if circuit is open
        if circuit_state.state == "open":
            # Check if enough time has passed to try half_open
            if circuit_state.circuit_opened_at:
                recovery_time = circuit_state.circuit_opened_at + timedelta(
                    seconds=self.config.CIRCUIT_BREAKER_RECOVERY_SECONDS
                )
                if datetime.now() >= recovery_time:
                    # Try half_open state
                    circuit_state.state = "half_open"
                    self.db.commit()
                    logger.info(f"Circuit breaker for tenant {tenant_id} moved to half_open state")
                else:
                    raise GuardrailViolation(
                        reason=f"Circuit breaker is OPEN due to excessive failures. "
                               f"Live sending disabled until {recovery_time.isoformat()}.",
                        suggested_fix="Check system logs for recurring errors. "
                                    "Verify email service configuration. "
                                    "Contact system administrator if issue persists."
                    )
    
    def _check_quiet_hours(self, tenant_id: int):
        """Check if current time is within quiet hours for the workspace."""
        quiet_hours = self.db.exec(
            select(WorkspaceQuietHours).where(
                WorkspaceQuietHours.tenant_id == tenant_id
            )
        ).first()
        
        if not quiet_hours or not quiet_hours.enabled:
            return
        
        # Get current time in workspace timezone
        tz = pytz.timezone(quiet_hours.timezone)
        now = datetime.now(tz)
        current_hour = now.hour
        
        # Check if current hour is in quiet period
        if quiet_hours.start_hour > quiet_hours.end_hour:
            # Quiet hours span midnight (e.g., 22:00 - 08:00)
            is_quiet = current_hour >= quiet_hours.start_hour or current_hour < quiet_hours.end_hour
        else:
            # Normal case (e.g., 01:00 - 06:00)
            is_quiet = quiet_hours.start_hour <= current_hour < quiet_hours.end_hour
        
        if is_quiet:
            raise GuardrailViolation(
                reason=f"Workspace quiet hours are active ({quiet_hours.start_hour}:00 - "
                       f"{quiet_hours.end_hour}:00 {quiet_hours.timezone}). "
                       f"Outbound messages are blocked.",
                suggested_fix="Wait until quiet hours end or adjust workspace quiet hours settings. "
                            "Consider queuing messages for delivery after quiet hours."
            )
    
    def _check_conversation_rate_limit(self, tenant_id: int, conversation_id: str):
        """Check if conversation rate limit has been exceeded."""
        rate_limit = self.db.exec(
            select(ConversationRateLimit).where(
                ConversationRateLimit.conversation_id == conversation_id,
                ConversationRateLimit.tenant_id == tenant_id
            )
        ).first()
        
        now = datetime.now()
        window_duration = timedelta(seconds=self.config.CONVERSATION_WINDOW_SECONDS)
        
        if not rate_limit:
            # Create new rate limit tracking
            rate_limit = ConversationRateLimit(
                conversation_id=conversation_id,
                tenant_id=tenant_id,
                message_count=0,
                window_start=now
            )
            self.db.add(rate_limit)
            self.db.commit()
        
        # Check if we need to reset the window
        if now >= rate_limit.window_start + window_duration:
            rate_limit.message_count = 0
            rate_limit.window_start = now
            self.db.commit()
        
        # Check if limit exceeded
        if rate_limit.message_count >= self.config.MAX_MESSAGES_PER_CONVERSATION_WINDOW:
            window_reset_time = rate_limit.window_start + window_duration
            seconds_until_reset = int((window_reset_time - now).total_seconds())
            
            raise GuardrailViolation(
                reason=f"Conversation rate limit exceeded: {rate_limit.message_count} messages "
                       f"sent in the last {self.config.CONVERSATION_WINDOW_SECONDS} seconds. "
                       f"Limit is {self.config.MAX_MESSAGES_PER_CONVERSATION_WINDOW} messages "
                       f"per {self.config.CONVERSATION_WINDOW_SECONDS} seconds.",
                suggested_fix=f"Wait {seconds_until_reset} seconds before sending more messages. "
                            f"Consider consolidating messages or increasing the rate limit."
            )
    
    def _check_contact_cooldown(self, tenant_id: int, recipient_email: str):
        """Check if contact is in cooldown period."""
        cooldown = self.db.exec(
            select(ContactCooldown).where(
                ContactCooldown.contact_email == recipient_email,
                ContactCooldown.tenant_id == tenant_id
            )
        ).first()
        
        if not cooldown:
            return  # No cooldown exists yet
        
        now = datetime.now()
        if now < cooldown.cooldown_until:
            seconds_remaining = int((cooldown.cooldown_until - now).total_seconds())
            
            raise GuardrailViolation(
                reason=f"Contact {recipient_email} is in cooldown period until "
                       f"{cooldown.cooldown_until.isoformat()}.",
                suggested_fix=f"Wait {seconds_remaining} seconds before contacting this recipient again. "
                            f"This prevents message fatigue and spam complaints."
            )
    
    def record_message_attempt(
        self,
        tenant_id: int,
        recipient_email: str,
        message_type: str,
        conversation_id: Optional[str] = None,
        user_id: Optional[int] = None,
        status: str = "pending",
    ) -> OutboundMessage:
        """Record an outbound message attempt."""
        message = OutboundMessage(
            tenant_id=tenant_id,
            user_id=user_id,
            conversation_id=conversation_id,
            recipient_email=recipient_email,
            message_type=message_type,
            status=status,
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        
        # Update rate limit counter if conversation_id provided
        if conversation_id and status != "blocked":
            self._increment_conversation_counter(tenant_id, conversation_id)
        
        # Update contact cooldown
        if status == "sent":
            self._update_contact_cooldown(tenant_id, recipient_email)
        
        return message
    
    def record_message_success(self, message_id: int):
        """Mark a message as successfully sent."""
        message = self.db.get(OutboundMessage, message_id)
        if message:
            message.status = "sent"
            message.sent_at = datetime.now()
            self.db.commit()
            
            # Update contact cooldown
            self._update_contact_cooldown(message.tenant_id, message.recipient_email)
            
            # Reset circuit breaker failure count on success
            self._record_circuit_breaker_success(message.tenant_id)
    
    def record_message_failure(self, message_id: int, failure_reason: str):
        """Mark a message as failed and update circuit breaker."""
        message = self.db.get(OutboundMessage, message_id)
        if message:
            message.status = "failed"
            message.failure_reason = failure_reason
            self.db.commit()
            
            # Update circuit breaker
            self._record_circuit_breaker_failure(message.tenant_id, failure_reason)
    
    def _increment_conversation_counter(self, tenant_id: int, conversation_id: str):
        """Increment the message counter for a conversation."""
        rate_limit = self.db.exec(
            select(ConversationRateLimit).where(
                ConversationRateLimit.conversation_id == conversation_id,
                ConversationRateLimit.tenant_id == tenant_id
            )
        ).first()
        
        if rate_limit:
            rate_limit.message_count += 1
            self.db.commit()
    
    def _update_contact_cooldown(self, tenant_id: int, recipient_email: str):
        """Update or create cooldown for a contact."""
        cooldown = self.db.exec(
            select(ContactCooldown).where(
                ContactCooldown.contact_email == recipient_email,
                ContactCooldown.tenant_id == tenant_id
            )
        ).first()
        
        now = datetime.now()
        cooldown_until = now + timedelta(seconds=self.config.DEFAULT_CONTACT_COOLDOWN_SECONDS)
        
        if cooldown:
            cooldown.last_message_sent_at = now
            cooldown.cooldown_until = cooldown_until
        else:
            cooldown = ContactCooldown(
                contact_email=recipient_email,
                tenant_id=tenant_id,
                last_message_sent_at=now,
                cooldown_until=cooldown_until
            )
            self.db.add(cooldown)
        
        self.db.commit()
    
    def _record_circuit_breaker_success(self, tenant_id: int):
        """Record a successful message send, potentially closing the circuit."""
        circuit_state = self.db.exec(
            select(CircuitBreakerState).where(
                CircuitBreakerState.tenant_id == tenant_id
            )
        ).first()
        
        if not circuit_state:
            return
        
        if circuit_state.state == "half_open":
            # Success in half_open state means we can close the circuit
            circuit_state.state = "closed"
            circuit_state.failure_count = 0
            circuit_state.window_start = datetime.now()
            circuit_state.circuit_opened_at = None
            self.db.commit()
            logger.info(f"Circuit breaker for tenant {tenant_id} closed after successful send")
    
    def _record_circuit_breaker_failure(self, tenant_id: int, failure_reason: str):
        """Record a failed message send and potentially open the circuit."""
        circuit_state = self.db.exec(
            select(CircuitBreakerState).where(
                CircuitBreakerState.tenant_id == tenant_id
            )
        ).first()
        
        if not circuit_state:
            circuit_state = CircuitBreakerState(
                tenant_id=tenant_id,
                state="closed",
                failure_count=0,
                window_start=datetime.now(),
            )
            self.db.add(circuit_state)
            self.db.commit()
            self.db.refresh(circuit_state)
        
        now = datetime.now()
        window_duration = timedelta(minutes=self.config.CIRCUIT_BREAKER_WINDOW_MINUTES)
        
        # Check if we need to reset the window
        if now >= circuit_state.window_start + window_duration:
            circuit_state.failure_count = 0
            circuit_state.window_start = now
        
        # Increment failure count
        circuit_state.failure_count += 1
        circuit_state.last_failure_at = now
        
        # Check if we should open the circuit
        if circuit_state.failure_count >= self.config.CIRCUIT_BREAKER_FAILURE_THRESHOLD:
            if circuit_state.state != "open":
                circuit_state.state = "open"
                circuit_state.circuit_opened_at = now
                
                # Notify admin (with cooldown to avoid spam)
                self._notify_admin_circuit_breaker_opened(tenant_id, circuit_state)
                
                logger.error(
                    f"Circuit breaker OPENED for tenant {tenant_id} after "
                    f"{circuit_state.failure_count} failures in "
                    f"{self.config.CIRCUIT_BREAKER_WINDOW_MINUTES} minutes"
                )
        
        self.db.commit()
    
    def _notify_admin_circuit_breaker_opened(
        self, tenant_id: int, circuit_state: CircuitBreakerState
    ):
        """Notify admin that circuit breaker has opened."""
        now = datetime.now()
        
        # Check if we've recently notified (cooldown)
        if circuit_state.admin_notified_at:
            cooldown_duration = timedelta(
                minutes=self.config.ADMIN_NOTIFICATION_COOLDOWN_MINUTES
            )
            if now < circuit_state.admin_notified_at + cooldown_duration:
                return  # Don't spam admin
        
        # Log the alert
        audit_log = AuditLog(
            tenant_id=tenant_id,
            action="CIRCUIT_BREAKER_OPENED",
            details=(
                f"Circuit breaker opened due to {circuit_state.failure_count} failures "
                f"in {self.config.CIRCUIT_BREAKER_WINDOW_MINUTES} minutes. "
                f"Live sending is disabled. Review system logs and email service configuration."
            )
        )
        self.db.add(audit_log)
        
        circuit_state.admin_notified_at = now
        self.db.commit()
        
        logger.critical(
            f"ADMIN ALERT: Circuit breaker opened for tenant {tenant_id}. "
            f"Outbound sending disabled."
        )
