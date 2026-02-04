"""
Service layer for sending outbound messages with guardrail enforcement.

This module provides a high-level interface for sending messages
while enforcing all guardrails and handling task queue integration.
"""
import logging
from typing import Optional
from sqlmodel import Session
from app.orchestrator.message_dispatcher import (
    MessageDispatcher,
    MessageDispatcherConfig,
    GuardrailViolation,
)
from app.orchestrator.tasks import enqueue_outbound_message
from app.core.models import AuditLog

logger = logging.getLogger(__name__)


class OutboundMessagingService:
    """High-level service for sending outbound messages."""
    
    def __init__(self, db_session: Session, config: Optional[MessageDispatcherConfig] = None):
        self.db = db_session
        self.dispatcher = MessageDispatcher(db_session, config)
    
    def send_message(
        self,
        tenant_id: int,
        recipient_email: str,
        message_content: str,
        message_type: str = "notification",
        conversation_id: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        """
        Send an outbound message with guardrail enforcement.
        
        Args:
            tenant_id: ID of the tenant sending the message
            recipient_email: Email address of the recipient
            message_content: Content of the message to send
            message_type: Type of message (notification, alert, report, etc.)
            conversation_id: Optional conversation ID for rate limiting
            user_id: Optional user ID who initiated the send
        
        Returns:
            Dictionary with status and details:
            {
                "success": bool,
                "message_id": int or None,
                "job_id": str or None,
                "blocked_reason": str or None,
                "suggested_fix": str or None
            }
        """
        # Check all guardrails
        can_send, reason, suggested_fix = self.dispatcher.can_send_message(
            tenant_id=tenant_id,
            recipient_email=recipient_email,
            conversation_id=conversation_id,
            user_id=user_id,
        )
        
        if not can_send:
            # Log the blocked attempt
            logger.warning(
                f"Message blocked for tenant {tenant_id} to {recipient_email}. "
                f"Reason: {reason}. Fix: {suggested_fix}"
            )
            
            # Record blocked message
            message = self.dispatcher.record_message_attempt(
                tenant_id=tenant_id,
                recipient_email=recipient_email,
                message_type=message_type,
                conversation_id=conversation_id,
                user_id=user_id,
                status="blocked",
            )
            message.failure_reason = reason
            self.db.commit()
            
            # Log to audit trail
            audit_log = AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action="MESSAGE_BLOCKED",
                details=f"Message to {recipient_email} blocked: {reason}",
            )
            self.db.add(audit_log)
            self.db.commit()
            
            return {
                "success": False,
                "message_id": message.id,
                "job_id": None,
                "blocked_reason": reason,
                "suggested_fix": suggested_fix,
            }
        
        # Guardrails passed - record and enqueue message
        message = self.dispatcher.record_message_attempt(
            tenant_id=tenant_id,
            recipient_email=recipient_email,
            message_type=message_type,
            conversation_id=conversation_id,
            user_id=user_id,
            status="pending",
        )
        
        # Enqueue message for async sending
        job_id = enqueue_outbound_message(
            message_id=message.id,
            recipient_email=recipient_email,
            message_content=message_content,
            message_type=message_type,
        )
        
        if not job_id:
            # Failed to enqueue - mark as failed
            message.status = "failed"
            message.failure_reason = "Failed to enqueue message to task queue"
            self.db.commit()
            
            logger.error(f"Failed to enqueue message {message.id}")
            
            return {
                "success": False,
                "message_id": message.id,
                "job_id": None,
                "blocked_reason": "Task queue unavailable",
                "suggested_fix": "Check Redis connection and task queue configuration",
            }
        
        # Log to audit trail
        audit_log = AuditLog(
            tenant_id=tenant_id,
            user_id=user_id,
            action="MESSAGE_ENQUEUED",
            details=f"Message to {recipient_email} enqueued for sending (job: {job_id})",
        )
        self.db.add(audit_log)
        self.db.commit()
        
        logger.info(
            f"Message {message.id} enqueued for tenant {tenant_id} "
            f"to {recipient_email} (job: {job_id})"
        )
        
        return {
            "success": True,
            "message_id": message.id,
            "job_id": job_id,
            "blocked_reason": None,
            "suggested_fix": None,
        }
    
    def get_circuit_breaker_status(self, tenant_id: int) -> dict:
        """
        Get the circuit breaker status for a tenant.
        
        Returns:
            Dictionary with circuit breaker state and metrics
        """
        from sqlmodel import select
        from app.core.models import CircuitBreakerState
        
        circuit = self.db.exec(
            select(CircuitBreakerState).where(CircuitBreakerState.tenant_id == tenant_id)
        ).first()
        
        if not circuit:
            return {
                "state": "closed",
                "failure_count": 0,
                "sending_enabled": True,
            }
        
        return {
            "state": circuit.state,
            "failure_count": circuit.failure_count,
            "sending_enabled": circuit.state != "open",
            "last_failure_at": circuit.last_failure_at.isoformat()
            if circuit.last_failure_at
            else None,
            "circuit_opened_at": circuit.circuit_opened_at.isoformat()
            if circuit.circuit_opened_at
            else None,
        }
