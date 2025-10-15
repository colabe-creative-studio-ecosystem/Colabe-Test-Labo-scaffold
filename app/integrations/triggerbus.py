import logging
import json
import hashlib
import hmac
import time
from app.core.settings import settings

logger = logging.getLogger(__name__)


def publish(topic: str, payload: dict):
    """
    Simulates publishing an event to the TriggerBus.
    In a real system, this would send a message to a broker like Kafka or RabbitMQ.
    """
    event_id = f"evt_{int(time.time())}_{hashlib.sha1(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:8]}"
    event = {"event_id": event_id, "topic": topic, "payload": payload}
    signature = sign_payload(json.dumps(event, sort_keys=True).encode())
    logger.info(
        f"TRIGGERBUS PUBLISH -> Topic: {topic}, EventID: {event_id}, Signature: {signature}"
    )
    return (event, signature)


def sign_payload(payload: bytes) -> str:
    """Signs a payload using HMAC-SHA256."""
    secret = settings.SUPPORT_WEBHOOK_SIGNING_SECRET.encode()
    return hmac.new(secret, payload, hashlib.sha256).hexdigest()


def verify_signature(payload: bytes, signature: str) -> bool:
    """Verifies a payload signature."""
    expected_signature = sign_payload(payload)
    return hmac.compare_digest(expected_signature, signature)


def handle_incoming_event(event: dict):
    """
    Simulates a subscriber handling an incoming event from the bus.
    This would be part of a worker process listening to a queue.
    """
    topic = event.get("topic")
    payload = event.get("payload")
    logger.info(f"TRIGGERBUS SUBSCRIBE -> Handling topic: {topic}")
    if topic in [
        "ops.synthetics.failed",
        "ops.error_budget.burn_fast",
        "payments.error",
        "events.consumer.lag.high",
        "status.incident.updated",
    ]:
        logger.info(f"-> Triggering auto-ticket creation for topic: {topic}")
    else:
        logger.warning(f"-> No handler registered for topic: {topic}")