from starlette.requests import Request
from starlette.responses import JSONResponse
import reflex as rx
from app.integrations.webhook_verifier import WebhookVerifier
from app.integrations.whatsapp_event_parser import WhatsAppEventParser, EngineEvent
from app.core.models import EventLog, WhatsAppPhoneMapping
from app.core.settings import settings
import sqlmodel
import logging
import json
from queue import Queue
from typing import List

logger = logging.getLogger(__name__)

# In-process queue for event processing
event_processing_queue: Queue[EngineEvent] = Queue()


async def whatsapp_webhook(request: Request):
    """
    Handle incoming WhatsApp webhook requests.
    
    This endpoint:
    1. Reads the raw body (before JSON parsing)
    2. Verifies the webhook signature
    3. Parses the webhook into EngineEvents
    4. Enqueues events for processing
    5. Stores EventLog entries with minimal payload
    """
    # Check for webhook secret
    if not settings.WHATSAPP_WEBHOOK_SECRET:
        logger.error("WHATSAPP_WEBHOOK_SECRET is not configured")
        return JSONResponse(
            {"detail": "Webhook not configured"},
            status_code=500
        )
    
    # Get signature from header
    signature = request.headers.get("x-hub-signature-256")
    if not signature:
        logger.warning("Missing x-hub-signature-256 header")
        return JSONResponse(
            {"detail": "Missing signature"},
            status_code=400
        )
    
    # Read raw body for signature verification
    try:
        raw_body = await request.body()
    except Exception as e:
        logger.exception(f"Error reading request body: {e}")
        return JSONResponse(
            {"detail": "Invalid request body"},
            status_code=400
        )
    
    # Verify signature
    verifier = WebhookVerifier(settings.WHATSAPP_WEBHOOK_SECRET)
    if not verifier.verify_signature(raw_body, signature):
        logger.warning("Invalid webhook signature")
        return JSONResponse(
            {"detail": "Invalid signature"},
            status_code=401
        )
    
    # Parse JSON payload
    try:
        payload = json.loads(raw_body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.exception(f"Error parsing JSON payload: {e}")
        return JSONResponse(
            {"detail": "Invalid JSON payload"},
            status_code=400
        )
    
    # Parse webhook into EngineEvents
    try:
        events = WhatsAppEventParser.parse_webhook(payload)
    except ValueError as e:
        logger.exception(f"Error parsing webhook: {e}")
        return JSONResponse(
            {"detail": f"Invalid webhook format: {str(e)}"},
            status_code=400
        )
    except Exception as e:
        logger.exception(f"Unexpected error parsing webhook: {e}")
        return JSONResponse(
            {"detail": "Internal server error"},
            status_code=500
        )
    
    # Process each event
    try:
        await process_events(events, payload)
    except Exception as e:
        logger.exception(f"Error processing events: {e}")
        return JSONResponse(
            {"detail": "Error processing webhook"},
            status_code=500
        )
    
    return JSONResponse({"status": "success"})


async def process_events(events: List[EngineEvent], raw_payload: dict):
    """
    Process parsed events.
    
    1. Look up tenant_id from phone_number_id
    2. Store EventLog with minimal, redacted payload
    3. Enqueue events for processing
    """
    with rx.session() as db_session:
        for event in events:
            # Look up tenant from phone number mapping
            phone_mapping = db_session.exec(
                sqlmodel.select(WhatsAppPhoneMapping).where(
                    WhatsAppPhoneMapping.phone_number_id == event.phone_number_id
                )
            ).first()
            
            tenant_id = phone_mapping.tenant_id if phone_mapping else None
            
            if not tenant_id:
                logger.warning(
                    f"No tenant mapping found for phone_number_id: {event.phone_number_id}"
                )
            
            # Create minimal EventLog entry (redact PII)
            minimal_payload = {
                'event_type': event.event_type,
                'phone_number_id': event.phone_number_id,
                'message_type': event.message_type,
                'timestamp': event.timestamp,
                # Don't store full text or phone numbers in logs
                'has_text': event.text_body is not None,
                'metadata': {
                    'display_phone_number': event.metadata.get('display_phone_number')
                }
            }
            
            event_log = EventLog(
                tenant_id=tenant_id,
                event_type=event.event_type,
                event_source='whatsapp',
                payload=json.dumps(minimal_payload),
                processed=False
            )
            db_session.add(event_log)
            
            # Enqueue for processing
            event_processing_queue.put(event)
            logger.info(
                f"Enqueued event: {event.event_type} for phone_number_id: {event.phone_number_id}"
            )
        
        db_session.commit()


def get_queue_size() -> int:
    """Get the current size of the event processing queue."""
    return event_processing_queue.qsize()


def dequeue_event() -> EngineEvent:
    """Dequeue an event from the processing queue."""
    return event_processing_queue.get()
