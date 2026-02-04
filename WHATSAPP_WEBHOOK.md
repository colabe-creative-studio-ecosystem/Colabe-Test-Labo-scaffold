# WhatsApp Webhook Integration

This document describes the WhatsApp webhook endpoint implementation.

## Overview

The WhatsApp webhook endpoint (`POST /api/whatsapp/webhook`) provides a secure way to receive WhatsApp events in your application.

## Features

- **Signature Verification**: All incoming webhooks are verified using HMAC-SHA256 signatures
- **Event Parsing**: Webhook payloads are parsed into structured `EngineEvent` objects
- **PII Redaction**: Personal information is redacted from stored event logs
- **Event Queue**: Events are enqueued for asynchronous processing
- **Tenant Mapping**: Events are linked to tenants via phone number ID mapping

## Configuration

Set the following environment variable:

```bash
WHATSAPP_WEBHOOK_SECRET=your_webhook_secret_here
```

## API Endpoint

### POST /api/whatsapp/webhook

Receives WhatsApp webhook events.

**Headers:**
- `x-hub-signature-256`: HMAC-SHA256 signature of the request body
- `Content-Type`: application/json

**Request Body:**
Standard WhatsApp webhook payload format (see WhatsApp Business API documentation)

**Response:**
- `200 OK`: Webhook processed successfully
- `400 Bad Request`: Missing signature, invalid JSON, or invalid payload
- `401 Unauthorized`: Invalid signature
- `500 Internal Server Error`: Server error or webhook not configured

**Example Success Response:**
```json
{
  "status": "success"
}
```

## Database Models

### WhatsAppPhoneMapping

Maps WhatsApp phone number IDs to tenant IDs:

- `phone_number_id` (unique, indexed): WhatsApp phone number ID
- `tenant_id`: Associated tenant ID
- `created_at`: Timestamp

### EventLog

Stores minimal event information with PII redacted:

- `tenant_id`: Associated tenant ID (nullable)
- `event_type`: Type of event (e.g., "message", "status")
- `event_source`: Always "whatsapp" for WhatsApp events
- `payload`: Minimal JSON payload with PII redacted
- `processed`: Boolean flag indicating if event was processed
- `created_at`: Timestamp

## Event Processing

Events are processed as follows:

1. **Signature Verification**: Request signature is verified before processing
2. **Parsing**: Webhook payload is parsed into `EngineEvent` objects
3. **Tenant Lookup**: Phone number ID is mapped to tenant ID
4. **Logging**: Minimal event data is stored in `EventLog` with PII redacted
5. **Queuing**: Events are enqueued in an in-process queue for processing

## Security Features

### Signature Verification

The `WebhookVerifier` class uses HMAC-SHA256 to verify webhook authenticity:

```python
from app.integrations.webhook_verifier import WebhookVerifier

verifier = WebhookVerifier(secret)
is_valid = verifier.verify_signature(payload_bytes, signature)
```

### PII Redaction

The parser automatically redacts:
- Phone numbers (replaced with `[REDACTED_PHONE]`)
- Long message text (truncated to 100 characters)
- Full message content (not stored in EventLog)

## Event Types

The parser supports the following WhatsApp event types:

### Message Events
- Text messages
- Image messages
- Document messages
- Other media types

### Status Events
- Message delivery status
- Read receipts
- Sent confirmations

## Usage Example

### Setting up a Phone Number Mapping

```python
from app.core.models import WhatsAppPhoneMapping
import reflex as rx

with rx.session() as db:
    mapping = WhatsAppPhoneMapping(
        phone_number_id="123456789",
        tenant_id=1
    )
    db.add(mapping)
    db.commit()
```

### Processing Queued Events

```python
from app.integrations.whatsapp_webhook_handler import (
    dequeue_event,
    get_queue_size
)

# Check queue size
size = get_queue_size()

# Process events
while size > 0:
    event = dequeue_event()
    # Process event...
    size = get_queue_size()
```

## Testing

Unit tests are provided for:

- **WebhookVerifier**: Signature verification logic
- **WhatsAppEventParser**: Webhook parsing and PII redaction

Run tests with:

```bash
python -m pytest tests/ -v
```

## Migration

A database migration is included to create the new tables:

```bash
python -m app.scripts.run_migration
```

Or manually with alembic:

```bash
alembic upgrade head
```

## Error Handling

The webhook handler includes comprehensive error handling:

- Invalid signatures are rejected with 401
- Malformed JSON returns 400
- Missing configuration returns 500
- Parsing errors are logged and return 400
- Database errors are caught and return 500

All errors are logged for debugging purposes.
