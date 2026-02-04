# WhatsApp Webhook Connector - Production Safety Documentation

## Overview

The WhatsApp webhook connector provides a production-ready, durable integration for handling WhatsApp Business API webhook events with comprehensive safety features.

## Features

### 1. Idempotency
- **Purpose**: Prevents duplicate processing of webhook events
- **Implementation**: Tracks processed message IDs in the `webhookevent` table
- **Behavior**: Duplicate messages return status 200 with `{"status": "duplicate"}` without reprocessing

### 2. Dead-Letter Logging
- **Purpose**: Captures failed events for investigation and manual recovery
- **Implementation**: Stores failed events in the `deadletterevent` table with error details
- **Triggers**: Events that fail after exhausting all retry attempts

### 3. Retry Policy with Exponential Backoff
- **Maximum Retries**: 3 attempts
- **Backoff Strategy**: Exponential (1s, 2s, 4s)
- **Formula**: `backoff_time = INITIAL_BACKOFF * (2 ** retry_count)`
- **Behavior**: Retries are attempted automatically before logging to dead letter

### 4. Monitoring Counters
Tracks daily aggregated metrics in the `webhookmetrics` table:
- **inbound_events**: Total webhook events received
- **outbound_sends**: Total messages sent via WhatsApp API
- **failures**: Total processing failures
- **circuit_breaker_trips**: Times the circuit breaker prevented processing

### 5. Circuit Breaker Pattern
- **Threshold**: Opens after 5 consecutive failures
- **Timeout**: 60 seconds before attempting to close
- **Behavior**: Rejects incoming webhooks with 503 status when open
- **Reset**: Automatically resets on successful processing

## Database Schema

### WebhookEvent
```sql
CREATE TABLE webhookevent (
    id INTEGER PRIMARY KEY,
    message_id VARCHAR UNIQUE NOT NULL,  -- WhatsApp message ID
    event_type VARCHAR NOT NULL,         -- Type of webhook event
    source VARCHAR NOT NULL,             -- Always 'whatsapp'
    payload TEXT NOT NULL,               -- Full webhook payload
    processed_at DATETIME NOT NULL,      -- Processing timestamp
    retry_count INTEGER NOT NULL         -- Number of retries before success
);
CREATE INDEX ix_webhookevent_message_id ON webhookevent(message_id);
```

### DeadLetterEvent
```sql
CREATE TABLE deadletterevent (
    id INTEGER PRIMARY KEY,
    message_id VARCHAR NOT NULL,         -- WhatsApp message ID
    event_type VARCHAR NOT NULL,         -- Type of webhook event
    source VARCHAR NOT NULL,             -- Always 'whatsapp'
    payload TEXT NOT NULL,               -- Full webhook payload
    error_message TEXT NOT NULL,         -- Error details
    retry_count INTEGER NOT NULL,        -- Number of retries attempted
    failed_at DATETIME NOT NULL          -- Failure timestamp
);
CREATE INDEX ix_deadletterevent_message_id ON deadletterevent(message_id);
```

### WebhookMetrics
```sql
CREATE TABLE webhookmetrics (
    id INTEGER PRIMARY KEY,
    source VARCHAR NOT NULL,             -- Always 'whatsapp'
    date DATE NOT NULL,                  -- Metric date
    inbound_events INTEGER NOT NULL,     -- Count of received events
    outbound_sends INTEGER NOT NULL,     -- Count of sent messages
    failures INTEGER NOT NULL,           -- Count of failures
    circuit_breaker_trips INTEGER NOT NULL, -- Count of CB trips
    updated_at DATETIME NOT NULL         -- Last update timestamp
);
CREATE INDEX ix_webhookmetrics_source ON webhookmetrics(source);
CREATE INDEX ix_webhookmetrics_date ON webhookmetrics(date);
```

## API Endpoint

### POST /api/webhook/whatsapp
Handles incoming WhatsApp webhook events.

**Expected Payload Structure:**
```json
{
  "entry": [
    {
      "changes": [
        {
          "value": {
            "messages": [
              {
                "id": "wamid.xxxxxxxxxxxxx",
                "from": "1234567890",
                "timestamp": "1234567890",
                "type": "text",
                "text": {
                  "body": "Hello, World!"
                }
              }
            ]
          }
        }
      ]
    }
  ],
  "type": "message"
}
```

**Response Codes:**
- `200 OK`: Event processed successfully or identified as duplicate
- `400 Bad Request`: Invalid JSON or missing message ID
- `500 Internal Server Error`: Processing failed after all retries
- `503 Service Unavailable`: Circuit breaker is open

**Response Body Examples:**
```json
// Success
{"status": "success", "message_id": "wamid.xxxxx"}

// Duplicate
{"status": "duplicate", "message_id": "wamid.xxxxx"}

// Circuit breaker open
{"detail": "Service temporarily unavailable"}
```

## Configuration Constants

Located in `app/integrations/whatsapp_handler.py`:

```python
CIRCUIT_BREAKER_THRESHOLD = 5    # Failures before opening circuit
CIRCUIT_BREAKER_TIMEOUT = 60     # Seconds before trying to close
MAX_RETRIES = 3                  # Maximum retry attempts
INITIAL_BACKOFF = 1              # Initial backoff in seconds
```

## Usage Examples

### Processing Webhook Events
The handler automatically processes incoming webhooks. No manual intervention required for normal operation.

### Monitoring Metrics
Query daily metrics:
```python
from app.core.models import WebhookMetrics
from datetime import date

# Get today's metrics
metrics = session.exec(
    select(WebhookMetrics).where(
        WebhookMetrics.source == "whatsapp",
        WebhookMetrics.date == date.today()
    )
).first()

print(f"Inbound: {metrics.inbound_events}")
print(f"Outbound: {metrics.outbound_sends}")
print(f"Failures: {metrics.failures}")
print(f"CB Trips: {metrics.circuit_breaker_trips}")
```

### Investigating Failed Events
Query dead letter events:
```python
from app.core.models import DeadLetterEvent

# Get recent failed events
failed_events = session.exec(
    select(DeadLetterEvent)
    .where(DeadLetterEvent.source == "whatsapp")
    .order_by(DeadLetterEvent.failed_at.desc())
    .limit(10)
).all()

for event in failed_events:
    print(f"Message ID: {event.message_id}")
    print(f"Error: {event.error_message}")
    print(f"Retries: {event.retry_count}")
```

### Sending Outbound Messages
```python
from app.integrations.whatsapp_handler import send_whatsapp_message

success = await send_whatsapp_message(
    phone_number="+1234567890",
    message="Hello from Colabe!"
)
```

## Migration

Run the database migration to create required tables:

```bash
# Using Alembic
alembic upgrade head

# Or programmatically
from alembic.config import Config
from alembic import command

cfg = Config('alembic.ini')
command.upgrade(cfg, 'head')
```

## Testing

Comprehensive test suite in `tests/test_whatsapp_handler.py`:

```bash
# Run all WhatsApp handler tests
pytest tests/test_whatsapp_handler.py -v

# Run specific test class
pytest tests/test_whatsapp_handler.py::TestCircuitBreaker -v

# Run with coverage
pytest tests/test_whatsapp_handler.py --cov=app.integrations.whatsapp_handler
```

## Error Handling

### Automatic Retry Scenarios
The following errors trigger automatic retry:
- Database connection failures
- Temporary network issues
- Transient API errors
- Any exception during processing

### Dead Letter Scenarios
Events are logged to dead letter after:
- Exhausting all 3 retry attempts
- Cumulative processing failures

### Circuit Breaker Activation
Circuit opens when:
- 5 consecutive failures occur
- Closes automatically after 60 seconds
- Resets immediately on any successful processing

## Security Considerations

1. **Payload Validation**: Always validates JSON structure and required fields
2. **Message ID Verification**: Rejects webhooks without valid message IDs
3. **SQL Injection Protection**: Uses parameterized queries via SQLModel
4. **Rate Limiting**: Circuit breaker prevents resource exhaustion
5. **Error Exposure**: Error details logged server-side, not returned to client

## Performance Characteristics

- **Duplicate Check**: Single indexed database query (O(1))
- **Metric Updates**: Single row update or insert per webhook
- **Retry Delays**: Total max delay for 3 retries = 7 seconds (1+2+4)
- **Circuit Breaker**: In-memory state, zero database overhead

## Future Enhancements

Potential improvements for future iterations:
1. Webhook signature verification for authentication
2. Configurable retry policies per event type
3. Alerting integration (email, Slack) for circuit breaker trips
4. Real-time dashboard for monitoring metrics
5. Automatic dead letter replay mechanism
6. Message priority queue for high-priority events

## Troubleshooting

### Circuit Breaker Stuck Open
```python
# Manually reset circuit breaker
from app.integrations.whatsapp_handler import reset_circuit_breaker
reset_circuit_breaker()
```

### High Failure Rate
1. Check `deadletterevent` table for error patterns
2. Review application logs for exceptions
3. Verify WhatsApp API connectivity
4. Check database connection pool health

### Missing Metrics
Metrics are created on-demand. If no events processed on a given day, no row exists for that date.

## Support

For issues or questions:
1. Check application logs for detailed error messages
2. Query `deadletterevent` table for failed event details
3. Review `webhookmetrics` for traffic patterns
4. Consult WhatsApp Business API documentation for webhook format changes
