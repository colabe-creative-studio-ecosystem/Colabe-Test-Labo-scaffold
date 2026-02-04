# WhatsApp Event Parser

This implementation provides a robust WhatsApp webhook event parser that converts inbound messages into EngineEvent format for processing.

## Features

### Supported Message Types

- ✅ **Text Messages** - Plain text messages with body content
- ✅ **Button Replies** - Interactive button click responses
- ✅ **List Replies** - Interactive list selection responses
- ✅ **Media Messages** - Image, video, audio, document, sticker, voice (stores reference only)
- ✅ **Delivery/Read Receipts** - Optional status updates (delivered, read)

### Unsupported Message Types

- ❌ **Location** - Gracefully rejected
- ❌ **Contacts** - Gracefully rejected
- ❌ **Unknown types** - Gracefully rejected with logging

## Architecture

### Files Created/Modified

1. **`app/integrations/whatsapp_parser.py`** (NEW)
   - Core parsing logic with exhaustive validation
   - Signature validation for webhook security
   - Custom exception types for error handling

2. **`app/integrations/webhook_handler.py`** (MODIFIED)
   - Added `whatsapp_webhook()` async function
   - Handles GET (verification) and POST (events) requests
   - Validates signatures, parses events, stores in database

3. **`app/core/models.py`** (MODIFIED)
   - Added `EngineEvent` SQLModel table
   - Added `InteractiveData` SQLModel for button/list data

4. **`app/app.py`** (MODIFIED)
   - Added WhatsApp webhook route: `/api/webhook/whatsapp`
   - Supports both GET (verification) and POST (events)

5. **`alembic/versions/a1b2c3d4e5f6_add_engineevent_model.py`** (NEW)
   - Database migration for EngineEvent table

6. **`tests/test_whatsapp_parser.py`** (NEW)
   - Comprehensive test suite with 13 test cases
   - All tests passing ✅

## EngineEvent Structure

```python
{
    "type": "message_received",           # Event type
    "workspace_id": str,                   # Phone number ID
    "conversation_id": str,                # Conversation identifier
    "contact_id": str,                     # Sender's WhatsApp ID
    "message_id": str,                     # Unique message ID
    "text": Optional[str],                 # Message text or media reference
    "interactive_type": Optional[str],     # "button" or "list" (if interactive)
    "interactive_id": Optional[str],       # Button/list item ID
    "interactive_title": Optional[str],    # Button/list item title
    "timestamp": datetime                  # Message timestamp
}
```

## Usage

### Webhook Endpoint

**URL:** `/api/webhook/whatsapp`

**Methods:**
- `GET` - For WhatsApp webhook verification during setup
- `POST` - For receiving inbound message events

### Environment Variables

```bash
WHATSAPP_VERIFY_TOKEN=your_verification_token  # Required for webhook verification
WHATSAPP_APP_SECRET=your_app_secret           # Optional, for signature validation
```

### Webhook Verification (GET)

WhatsApp sends a GET request during webhook setup:

```
GET /api/webhook/whatsapp?hub.mode=subscribe&hub.verify_token=TOKEN&hub.challenge=CHALLENGE
```

Response: Returns the challenge value if verification token matches.

### Event Processing (POST)

WhatsApp sends POST requests with event payloads:

```json
{
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "123456",
      "changes": [
        {
          "value": {
            "metadata": {
              "phone_number_id": "workspace123"
            },
            "messages": [
              {
                "from": "contact123",
                "id": "message123",
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
  ]
}
```

## Error Handling

### Exception Types

1. **`InvalidMessageFormatError`**
   - Raised when webhook payload structure is invalid
   - Returns 400 Bad Request

2. **`UnsupportedMessageTypeError`**
   - Raised when message type is not supported (location, contacts, etc.)
   - Returns 200 OK (acknowledges but doesn't process)

3. **`WhatsAppParserError`**
   - Base exception for all parsing errors
   - Returns 400 Bad Request

### Validation Checks

- ✅ Payload structure validation
- ✅ Required field validation
- ✅ Type checking for all fields
- ✅ Timestamp format validation
- ✅ Signature validation (when secret is configured)
- ✅ Graceful handling of unsupported types

## Testing

### Run Tests

```bash
pytest tests/test_whatsapp_parser.py -v
```

### Test Coverage

- Text message parsing
- Button reply parsing
- List reply parsing
- Image message with caption
- Video message without caption
- Delivery receipt parsing
- Unsupported message type rejection
- Invalid payload structure handling
- Missing required field handling
- Empty message array handling
- Valid signature validation
- Invalid signature rejection
- Wrong signature format handling

**Result:** 13/13 tests passing ✅

### Manual Validation

```bash
PYTHONPATH=. python tests/manual_validation.py
```

This demonstrates parsing of all supported message types with example payloads.

## Security

### Signature Validation

The parser supports WhatsApp's signature validation using HMAC-SHA256:

```python
from app.integrations.whatsapp_parser import validate_webhook_signature

is_valid = validate_webhook_signature(
    payload=request_body,
    signature=request.headers.get("x-hub-signature-256"),
    secret=os.environ.get("WHATSAPP_APP_SECRET")
)
```

### Best Practices

1. **Always configure WHATSAPP_APP_SECRET** in production
2. **Use HTTPS** for webhook endpoint
3. **Rotate verification token** periodically
4. **Monitor failed signature validations** for security alerts
5. **Rate limit webhook endpoint** to prevent abuse

## Database Schema

### EngineEvent Table

```sql
CREATE TABLE engineevent (
    id INTEGER PRIMARY KEY,
    type VARCHAR NOT NULL,
    workspace_id VARCHAR NOT NULL,
    conversation_id VARCHAR NOT NULL,
    contact_id VARCHAR NOT NULL,
    message_id VARCHAR NOT NULL,
    text VARCHAR,
    interactive_type VARCHAR,
    interactive_id VARCHAR,
    interactive_title VARCHAR,
    timestamp DATETIME NOT NULL,
    created_at DATETIME NOT NULL
);
```

## Media Handling

Media messages (image, video, audio, document, sticker, voice) are stored as references only:

- **Format:** `[TYPE:media_id] optional_caption`
- **Example:** `[IMAGE:img_abc123] Product photo`

To download media:
1. Extract media ID from the text field
2. Use WhatsApp API to download media by ID
3. Store media separately (S3, local storage, etc.)

## Future Enhancements

Potential improvements:

- [ ] Add conversation context tracking
- [ ] Implement media download/storage
- [ ] Add support for location messages
- [ ] Add support for contact messages
- [ ] Implement message templates
- [ ] Add webhook retry logic
- [ ] Add event queuing for async processing
- [ ] Add metrics and monitoring
- [ ] Add rate limiting
- [ ] Add webhook payload logging

## License

Part of the Colabe Test Labo Scaffold project.
