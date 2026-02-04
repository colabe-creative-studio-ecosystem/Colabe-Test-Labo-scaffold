# Inbound Processor Pipeline

## Overview

The Inbound Processor Pipeline is a robust system for processing webhook events and executing automations. It follows a clean architecture with retry logic, error handling, and comprehensive audit trails.

## Architecture

```
Webhook Event → Normalize → Load Automations → Execute → Dispatch → Audit
```

### Flow Details

1. **Webhook Event Reception** (`/api/webhook/inbound`)
   - Receives POST requests with event data
   - Validates JSON payload
   - Routes to inbound processor

2. **Event Normalization**
   - Standardizes event format
   - Validates required fields
   - Extracts workspace and conversation context

3. **Context Resolution**
   - Validates workspace exists
   - Creates or updates conversation records
   - Loads workspace settings

4. **Automation Loading**
   - Queries automations with `status=live`
   - Filters by trigger type (TRIGGER_MESSAGE, etc.)
   - Returns matched automations

5. **Execution Engine**
   - Determines execution mode (simulate/live)
   - Executes flow steps
   - Captures execution trace
   - Emits actions

6. **Action Dispatcher**
   - Processes emitted actions
   - Handles different action types
   - Respects simulation mode

7. **Trace & Audit**
   - Writes ExecutionRun records
   - Logs notable actions (handoff, payment_link, etc.)
   - Creates AuditLog entries

## Models

### WorkspaceSettings
Configures execution behavior per workspace:
- `execution_mode`: "auto", "simulate", or "live"
- `environment`: "staging" or "production"
- Default behavior: simulate in staging, live in production

### Conversation
Tracks conversation context:
- `external_id`: External conversation identifier
- `channel`: Communication channel (slack, email, etc.)
- `status`: active, closed, archived

### Automation
Defines automation flows:
- `status`: draft, live, paused, archived
- `trigger_type`: TRIGGER_MESSAGE, TRIGGER_WEBHOOK, etc.
- `flow_definition`: JSON with flow steps and actions

### ExecutionRun
Traces automation execution:
- `status`: pending, running, completed, failed, retrying
- `mode`: simulate or live
- `execution_trace`: JSON with step-by-step execution log
- `actions_dispatched`: JSON with dispatched actions
- `retry_count`: Number of retry attempts

## Usage

### Webhook Endpoint

**POST** `/api/webhook/inbound`

**Request Body:**
```json
{
  "type": "message.received",
  "workspace_id": "123",
  "conversation_id": "conv_456",
  "channel": "slack",
  "payload": {
    "text": "Hello",
    "user": "user_789"
  }
}
```

**Success Response (200):**
```json
{
  "status": "success",
  "result": {
    "status": "completed",
    "workspace_id": 123,
    "conversation_id": 456,
    "results": [
      {
        "automation_id": 1,
        "execution_run_id": 789,
        "status": "success"
      }
    ]
  }
}
```

**Error Response (400 - Permanent Error):**
```json
{
  "status": "error",
  "error": "Missing workspace_id or tenant_id",
  "retryable": false
}
```

**Error Response (503 - Transient Error):**
```json
{
  "status": "error",
  "error": "Database connection failed",
  "retryable": true
}
```

### Programmatic Usage

```python
from app.server.inbound_processor import process_inbound_event

# Process an event
result = await process_inbound_event({
    "type": "message.received",
    "workspace_id": "123",
    "conversation_id": "conv_456",
    "channel": "slack",
    "payload": {"text": "Hello"}
})
```

## Error Handling

### Error Types

1. **PermanentError**
   - Invalid data format
   - Missing required fields
   - Workspace not found
   - No retry

2. **TransientError**
   - Database connection issues
   - Timeout errors
   - Network failures
   - Triggers retry with exponential backoff

### Retry Logic

- **Max Retries:** 3 (configurable)
- **Base Delay:** 2 seconds (configurable)
- **Backoff:** Exponential (2^attempt * base_delay)
- **Example delays:** 2s, 4s, 8s

```python
# Customize retry behavior
processor = InboundProcessor(max_retries=5, retry_delay_base=1.0)
```

## Execution Modes

### Auto Mode (Default)
- In **staging** environment: simulate
- In **production** environment: live

### Simulate Mode
- Logs all actions without executing
- Safe for testing and validation
- Creates execution traces

### Live Mode
- Executes actions for real
- Dispatches to external services
- Production behavior

## Action Types

### Notable Actions (Audited)
- `handoff`: Transfer to human agent
- `payment_link`: Send payment link
- `notification`: Send important notification
- `escalation`: Escalate issue

### Standard Actions
- `send_message`: Send message
- `update_status`: Update status
- `tag_conversation`: Add tags
- Custom action types

## Database Schema

The inbound processor uses the following tables:

- `workspacesettings`: Workspace execution configuration
- `conversation`: Conversation context tracking
- `automation`: Automation flow definitions
- `executionrun`: Execution trace records
- `auditlog`: Audit trail for notable actions

## Testing

Run the verification script:
```bash
python verify_inbound_processor.py
```

Run unit tests (requires full environment):
```bash
pytest tests/test_inbound_processor.py -v
```

## Configuration

Set environment variables in `.env`:

```env
DATABASE_URL=postgresql://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
```

## Monitoring

### Logs
All operations are logged with appropriate levels:
- `INFO`: Normal operations
- `WARNING`: Transient errors, retries
- `ERROR`: Permanent errors
- `EXCEPTION`: Unexpected errors with stack traces

### Metrics
Track these metrics for monitoring:
- Event processing rate
- Automation execution count
- Error rate (transient vs permanent)
- Retry count
- Average execution time

## Example Automation Flow

```json
{
  "steps": [
    {
      "name": "greet_user",
      "type": "action",
      "action": {
        "type": "send_message",
        "data": {
          "text": "Hello! How can I help?"
        }
      }
    },
    {
      "name": "check_intent",
      "type": "condition",
      "action": {
        "type": "analyze_intent"
      }
    },
    {
      "name": "handoff_if_needed",
      "type": "action",
      "action": {
        "type": "handoff",
        "data": {
          "agent": "support",
          "reason": "complex_query"
        }
      }
    }
  ]
}
```

## Security Considerations

1. **Webhook Authentication**: Add signature verification (similar to Stripe webhooks)
2. **Rate Limiting**: Implement rate limits on webhook endpoint
3. **Input Validation**: All inputs are validated and sanitized
4. **Audit Trail**: All actions are logged for compliance
5. **Error Masking**: Sensitive errors are not exposed to clients

## Future Enhancements

- [ ] Webhook signature verification
- [ ] Rate limiting and throttling
- [ ] Dead letter queue for failed events
- [ ] Webhook delivery status tracking
- [ ] Advanced retry strategies (circuit breaker)
- [ ] Metrics and observability integration
- [ ] Multi-step flow orchestration
- [ ] Conditional branching in flows
- [ ] External service integrations (Slack, Teams, etc.)

## Support

For issues or questions, contact the development team or file an issue in the repository.
