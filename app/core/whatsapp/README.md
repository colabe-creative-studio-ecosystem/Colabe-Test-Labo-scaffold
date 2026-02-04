# WhatsApp Connector Abstraction Layer

This module provides a clean abstraction layer for WhatsApp messaging operations, enabling the engine to emit ActionPlans that can be executed by different connector implementations.

## Architecture

The system consists of three main components:

1. **Provider Interface** (`WhatsAppProvider`): Defines the contract for sending messages
2. **Webhook Verifier** (`WebhookVerifier`): Validates incoming webhook signatures
3. **Event Parser** (`WhatsAppEventParser`): Converts WhatsApp webhooks into engine events

## Implementations

### SimulationProvider

A provider that simulates WhatsApp operations without network calls. Perfect for:
- Development and testing
- Debugging message flows
- CI/CD environments

All operations are logged to trace for inspection.

### CloudProvider

A placeholder stub for WhatsApp Cloud API integration. This will be implemented in a future iteration with actual API calls to:
- WhatsApp Business Cloud API
- Authentication via access tokens
- Rate limiting and error handling

## Usage Examples

### Sending Messages with SimulationProvider

```python
from app.core.whatsapp import SimulationProvider, MessageButton, ListItem

# Initialize the provider
provider = SimulationProvider(trace_file="/tmp/whatsapp_trace.log")

# Send a simple text message
receipt = provider.send_text(
    to="+1234567890",
    text="Hello from the engine!",
    meta={"flow_id": "onboarding_001"}
)

print(f"Message sent: {receipt.message_id}")

# Send an interactive button message
buttons = [
    MessageButton(id="yes", title="Yes, continue"),
    MessageButton(id="no", title="No, thanks"),
]

receipt = provider.send_buttons(
    to="+1234567890",
    text="Would you like to continue?",
    buttons=buttons
)

# Send a list message
items = [
    ListItem(id="opt1", title="Option 1", description="First choice"),
    ListItem(id="opt2", title="Option 2", description="Second choice"),
    ListItem(id="opt3", title="Option 3", description="Third choice"),
]

receipt = provider.send_list(
    to="+1234567890",
    header="Select your preference:",
    items=items
)

# Send media
receipt = provider.send_media(
    to="+1234567890",
    media_url_or_id="https://example.com/image.jpg",
    caption="Check out this image!"
)

# Mark message as read
provider.mark_read("msg_123")
```

### Parsing Incoming Webhooks

```python
from app.core.whatsapp import SimulationEventParser, EventType

parser = SimulationEventParser()

# Parse an incoming webhook
webhook_payload = {
    "entry": [{
        "changes": [{
            "value": {
                "messages": [{
                    "id": "msg_123",
                    "from": "+1234567890",
                    "text": {"body": "Hello, bot!"},
                    "timestamp": "1234567890"
                }]
            }
        }]
    }]
}

events = parser.parse(webhook_payload)

for event in events:
    if event.event_type == EventType.MESSAGE_RECEIVED:
        print(f"Received message from {event.from_number}: {event.text}")
    elif event.event_type == EventType.BUTTON_CLICKED:
        print(f"Button clicked: {event.button_id}")
    elif event.event_type == EventType.LIST_SELECTED:
        print(f"List item selected: {event.list_item_id}")
```

### Verifying Webhooks

```python
from app.core.whatsapp import CloudWebhookVerifier

# Initialize with your app secret
verifier = CloudWebhookVerifier(app_secret="your_app_secret")

# Verify incoming webhook
signature = request.headers.get("X-Hub-Signature-256")
raw_body = request.body

if verifier.verify(signature, raw_body):
    # Webhook is authentic, process it
    events = parser.parse(webhook_json)
else:
    # Invalid signature, reject the webhook
    return {"error": "Invalid signature"}, 401
```

### Using CloudProvider (Future)

```python
from app.core.whatsapp import CloudProvider

# Initialize with credentials (stub implementation)
provider = CloudProvider(
    phone_number_id="your_phone_number_id",
    access_token="your_access_token",
    api_version="v18.0"
)

# Note: Actual API calls not yet implemented
# Returns stub receipt with error indicating not implemented
receipt = provider.send_text("+1234567890", "Hello!")
```

## Integration with Engine

The typical flow:

1. **Outbound**: Engine emits ActionPlan → Provider executes actions → Returns receipts
2. **Inbound**: Webhook arrives → Verifier checks signature → Parser converts to EngineEvents → Engine processes events

```python
# Outbound flow
def execute_action_plan(plan, provider):
    for action in plan.actions:
        if action.type == "send_text":
            receipt = provider.send_text(
                to=action.recipient,
                text=action.text,
                meta={"action_id": action.id}
            )
            # Store receipt for tracking
            store_receipt(action.id, receipt)

# Inbound flow (webhook endpoint)
async def handle_webhook(request):
    # Verify signature
    signature = request.headers.get("X-Hub-Signature-256")
    raw_body = await request.body()
    
    if not verifier.verify(signature, raw_body):
        return JSONResponse({"error": "Invalid signature"}, status_code=401)
    
    # Parse events
    webhook_data = await request.json()
    events = parser.parse(webhook_data)
    
    # Process each event with the engine
    for event in events:
        await engine.process_event(event)
    
    return JSONResponse({"status": "ok"})
```

## Testing

Run the test suite:

```bash
python3 -m pytest tests/test_whatsapp_provider.py -v
```

All tests should pass, covering:
- Message sending (text, buttons, lists, media)
- Webhook verification (HMAC SHA-256)
- Event parsing (messages, button clicks, list selections, statuses)
- Both simulation and cloud provider implementations

## File Structure

```
app/core/whatsapp/
├── __init__.py              # Public API exports
├── provider.py              # Base interfaces and data models
├── simulation_provider.py   # Simulation implementation (no network)
└── cloud_provider.py        # Cloud API stub (to be implemented)
```

## Future Enhancements

1. Complete CloudProvider implementation with actual WhatsApp Cloud API calls
2. Add retry logic and rate limiting
3. Support for additional message types (contacts, location, templates)
4. Message status tracking and delivery confirmations
5. Media upload/download functionality
6. Template message support for notifications
