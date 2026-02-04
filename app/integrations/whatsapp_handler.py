"""WhatsApp webhook handler with production safety features"""
from starlette.requests import Request
from starlette.responses import JSONResponse
import reflex as rx
from app.core.models import WebhookEvent, DeadLetterEvent, WebhookMetrics
import sqlmodel
import logging
import json
import asyncio
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)

# Circuit breaker configuration
CIRCUIT_BREAKER_THRESHOLD = 5  # Number of failures before opening circuit
CIRCUIT_BREAKER_TIMEOUT = 60  # Seconds before trying to close circuit
MAX_RETRIES = 3
INITIAL_BACKOFF = 1  # seconds

# Circuit breaker state
circuit_breaker_state = {
    "is_open": False,
    "failure_count": 0,
    "last_failure_time": None
}


async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp webhook events with production safety features:
    - Idempotency: ignore duplicate message IDs
    - Retry policy with exponential backoff (max 3 retries)
    - Dead-letter logging for failed events
    - Monitoring counters
    """
    try:
        # Parse webhook payload
        payload = await request.body()
        payload_str = payload.decode('utf-8')
        
        try:
            event_data = json.loads(payload_str)
        except json.JSONDecodeError:
            logger.error("Invalid JSON payload")
            return JSONResponse({"detail": "Invalid JSON"}, status_code=400)
        
        # Extract message ID for idempotency
        message_id = extract_message_id(event_data)
        if not message_id:
            logger.error("Missing message ID in webhook payload")
            return JSONResponse({"detail": "Missing message ID"}, status_code=400)
        
        # Check circuit breaker
        if is_circuit_breaker_open():
            logger.warning(f"Circuit breaker is open, rejecting message {message_id}")
            await increment_metric("circuit_breaker_trips")
            return JSONResponse(
                {"detail": "Service temporarily unavailable"}, 
                status_code=503
            )
        
        # Increment inbound events counter
        await increment_metric("inbound_events")
        
        # Check for duplicate (idempotency)
        if await is_duplicate_event(message_id):
            logger.info(f"Duplicate message ID detected: {message_id}, ignoring")
            return JSONResponse({"status": "duplicate", "message_id": message_id})
        
        # Process the webhook event
        event_type = event_data.get("type", "message")
        success = await process_webhook_event(
            message_id=message_id,
            event_type=event_type,
            payload=payload_str,
            retry_count=0
        )
        
        if success:
            return JSONResponse({"status": "success", "message_id": message_id})
        else:
            # Will be handled by dead-letter logging in process_webhook_event
            return JSONResponse(
                {"detail": "Processing failed"},
                status_code=500
            )
            
    except Exception as e:
        logger.exception(f"Unexpected error in webhook handler: {e}")
        await increment_metric("failures")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


def extract_message_id(event_data: dict) -> Optional[str]:
    """Extract message ID from WhatsApp webhook payload"""
    # WhatsApp webhook structure: entry[0].changes[0].value.messages[0].id
    try:
        entry = event_data.get("entry", [])
        if entry and len(entry) > 0:
            changes = entry[0].get("changes", [])
            if changes and len(changes) > 0:
                value = changes[0].get("value", {})
                messages = value.get("messages", [])
                if messages and len(messages) > 0:
                    return messages[0].get("id")
        # Fallback: check if there's a direct id field
        return event_data.get("id")
    except Exception as e:
        logger.error(f"Error extracting message ID: {e}")
        return None


async def is_duplicate_event(message_id: str) -> bool:
    """Check if event has already been processed (idempotency)"""
    with rx.session() as db_session:
        existing = db_session.exec(
            sqlmodel.select(WebhookEvent).where(
                WebhookEvent.message_id == message_id
            )
        ).first()
        return existing is not None


async def process_webhook_event(
    message_id: str,
    event_type: str,
    payload: str,
    retry_count: int
) -> bool:
    """
    Process webhook event with retry logic and exponential backoff
    """
    try:
        # Simulate processing logic - replace with actual WhatsApp handling
        payload_data = json.loads(payload)
        logger.info(f"Processing WhatsApp event {message_id} of type {event_type}")
        
        # TODO: Add actual WhatsApp message processing logic here
        # For example: extract message content, sender, recipient, etc.
        # and route to appropriate handler
        
        # If processing succeeds, record the event
        await record_processed_event(message_id, event_type, payload, retry_count)
        
        # Reset circuit breaker on success
        reset_circuit_breaker()
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing event {message_id}: {e}")
        
        # Increment failure count
        await increment_metric("failures")
        increment_circuit_breaker_failure()
        
        # Retry with exponential backoff
        if retry_count < MAX_RETRIES:
            backoff_time = INITIAL_BACKOFF * (2 ** retry_count)
            logger.info(
                f"Retrying event {message_id} in {backoff_time}s "
                f"(attempt {retry_count + 1}/{MAX_RETRIES})"
            )
            await asyncio.sleep(backoff_time)
            return await process_webhook_event(
                message_id, event_type, payload, retry_count + 1
            )
        else:
            # Max retries reached, log to dead letter
            logger.error(
                f"Max retries reached for event {message_id}, "
                f"logging to dead letter"
            )
            await log_to_dead_letter(
                message_id, event_type, payload, str(e), retry_count
            )
            return False


async def record_processed_event(
    message_id: str,
    event_type: str,
    payload: str,
    retry_count: int
):
    """Record successfully processed event for idempotency tracking"""
    with rx.session() as db_session:
        webhook_event = WebhookEvent(
            message_id=message_id,
            event_type=event_type,
            source="whatsapp",
            payload=payload,
            retry_count=retry_count
        )
        db_session.add(webhook_event)
        db_session.commit()


async def log_to_dead_letter(
    message_id: str,
    event_type: str,
    payload: str,
    error_message: str,
    retry_count: int
):
    """Log failed events to dead letter queue for investigation"""
    with rx.session() as db_session:
        dead_letter = DeadLetterEvent(
            message_id=message_id,
            event_type=event_type,
            source="whatsapp",
            payload=payload,
            error_message=error_message,
            retry_count=retry_count
        )
        db_session.add(dead_letter)
        db_session.commit()
        logger.info(f"Event {message_id} logged to dead letter queue")


async def increment_metric(metric_name: str):
    """Increment monitoring counter"""
    with rx.session() as db_session:
        today = date.today()
        metric = db_session.exec(
            sqlmodel.select(WebhookMetrics).where(
                WebhookMetrics.source == "whatsapp",
                WebhookMetrics.date == today
            )
        ).first()
        
        if not metric:
            metric = WebhookMetrics(source="whatsapp", date=today)
            db_session.add(metric)
        
        # Increment the appropriate counter
        if metric_name == "inbound_events":
            metric.inbound_events += 1
        elif metric_name == "outbound_sends":
            metric.outbound_sends += 1
        elif metric_name == "failures":
            metric.failures += 1
        elif metric_name == "circuit_breaker_trips":
            metric.circuit_breaker_trips += 1
        
        metric.updated_at = datetime.now()
        db_session.add(metric)
        db_session.commit()


def is_circuit_breaker_open() -> bool:
    """Check if circuit breaker is open"""
    if not circuit_breaker_state["is_open"]:
        return False
    
    # Check if timeout has elapsed
    if circuit_breaker_state["last_failure_time"]:
        elapsed = (datetime.now() - circuit_breaker_state["last_failure_time"]).seconds
        if elapsed >= CIRCUIT_BREAKER_TIMEOUT:
            # Try to close circuit
            logger.info("Circuit breaker timeout elapsed, attempting to close")
            circuit_breaker_state["is_open"] = False
            circuit_breaker_state["failure_count"] = 0
            return False
    
    return True


def increment_circuit_breaker_failure():
    """Increment failure count and open circuit if threshold reached"""
    circuit_breaker_state["failure_count"] += 1
    circuit_breaker_state["last_failure_time"] = datetime.now()
    
    if circuit_breaker_state["failure_count"] >= CIRCUIT_BREAKER_THRESHOLD:
        circuit_breaker_state["is_open"] = True
        logger.warning(
            f"Circuit breaker opened after {CIRCUIT_BREAKER_THRESHOLD} failures"
        )


def reset_circuit_breaker():
    """Reset circuit breaker on successful processing"""
    if circuit_breaker_state["failure_count"] > 0:
        logger.info("Resetting circuit breaker after successful processing")
    circuit_breaker_state["failure_count"] = 0
    circuit_breaker_state["is_open"] = False
    circuit_breaker_state["last_failure_time"] = None


async def send_whatsapp_message(phone_number: str, message: str) -> bool:
    """
    Send outbound WhatsApp message
    Returns True if successful, False otherwise
    """
    try:
        # TODO: Implement actual WhatsApp Business API call
        # For now, this is a placeholder
        logger.info(f"Sending WhatsApp message to {phone_number}: {message}")
        
        # Increment outbound counter
        await increment_metric("outbound_sends")
        
        return True
    except Exception as e:
        logger.error(f"Failed to send WhatsApp message: {e}")
        await increment_metric("failures")
        return False
