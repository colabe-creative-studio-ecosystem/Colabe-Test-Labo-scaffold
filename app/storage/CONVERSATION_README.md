# WhatsApp Conversation State Store

This module provides conversation state management for WhatsApp threads, including contact management, conversation tracking, and message history.

## Models

### Contact
Represents a WhatsApp contact.

**Fields:**
- `id`: Primary key
- `workspace_id`: Foreign key to Tenant (workspace)
- `phone_e164`: Phone number in E.164 format
- `display_name`: Optional display name
- `locale`: Optional locale (e.g., "en_US")
- `tags`: JSON string array of tags
- `created_at`: Timestamp

**Indexes:**
- `workspace_id` - for fast workspace lookups
- `phone_e164` - for fast phone lookups
- `(workspace_id, phone_e164)` - composite index for upsert operations

### Conversation
Represents a conversation thread with a contact.

**Fields:**
- `id`: Primary key
- `workspace_id`: Foreign key to Tenant
- `channel`: Channel type (default: "whatsapp")
- `contact_id`: Foreign key to Contact
- `status`: "open" or "closed"
- `last_message_at`: Timestamp of last message
- `last_intent`: Optional last detected intent
- `stage`: Optional conversation stage
- `assigned_agent_id`: Optional foreign key to User (agent)
- `awaiting_reply_key`: Optional key for expected reply type
- `created_at`: Timestamp

**Indexes:**
- `workspace_id` - for workspace queries
- `contact_id` - for contact queries
- `(workspace_id, status)` - for filtering active conversations
- `(contact_id, status)` - for finding active conversations per contact

### Message
Represents a single message in a conversation.

**Fields:**
- `id`: Primary key
- `conversation_id`: Foreign key to Conversation
- `direction`: "inbound" or "outbound"
- `content`: Message text content
- `message_metadata`: JSON string for WhatsApp-specific metadata
- `created_at`: Timestamp

**Indexes:**
- `conversation_id` - for message queries
- `created_at` - for time-based queries
- `(conversation_id, created_at)` - composite index for efficient history retrieval

## Services

### ConversationService

Static methods for managing conversations:

#### `upsert_contact(workspace_id, phone_e164, display_name=None, locale=None, tags=None)`
Creates or updates a contact by phone number.

**Parameters:**
- `workspace_id` (int): The workspace/tenant ID
- `phone_e164` (str): Phone number in E.164 format (e.g., "+14155552671")
- `display_name` (str, optional): Contact's display name
- `locale` (str, optional): Contact's locale (e.g., "en_US")
- `tags` (list, optional): List of tags

**Returns:** `Contact` object

#### `upsert_conversation(workspace_id, contact_id, channel="whatsapp", ...)`
Creates or updates a conversation for a contact.

**Parameters:**
- `workspace_id` (int): The workspace/tenant ID
- `contact_id` (int): Contact ID
- `channel` (str): Channel type (default: "whatsapp")
- `status` (ConversationStatusEnum): Conversation status (default: OPEN)
- `last_intent` (str, optional): Last detected intent
- `stage` (str, optional): Conversation stage
- `assigned_agent_id` (int, optional): Assigned agent user ID
- `awaiting_reply_key` (str, optional): Expected reply type

**Returns:** `Conversation` object

#### `add_message(conversation_id, direction, content, metadata=None)`
Adds a message to a conversation and updates last_message_at.

**Parameters:**
- `conversation_id` (int): Conversation ID
- `direction` (str): "inbound" or "outbound"
- `content` (str): Message text
- `metadata` (dict, optional): WhatsApp-specific metadata

**Returns:** `Message` object

#### `get_conversation_history(conversation_id, limit=100)`
Retrieves message history for a conversation.

**Parameters:**
- `conversation_id` (int): Conversation ID
- `limit` (int): Maximum number of messages (default: 100)

**Returns:** List of `Message` objects (newest first)

#### `close_conversation(conversation_id)`
Closes a conversation.

**Parameters:**
- `conversation_id` (int): Conversation ID

**Returns:** `Conversation` object

#### `get_active_conversations(workspace_id)`
Gets all active (open) conversations for a workspace.

**Parameters:**
- `workspace_id` (int): The workspace/tenant ID

**Returns:** List of `Conversation` objects (most recent first)

### MessagePipeline

#### `process_message_received(workspace_id, phone_e164, content, ...)`
Processes an incoming WhatsApp message through the full pipeline:
1. Upserts Contact by phone
2. Upserts Conversation
3. Attaches message to conversation history

**Parameters:**
- `workspace_id` (int): The workspace/tenant ID
- `phone_e164` (str): Phone number in E.164 format
- `content` (str): Message text
- `display_name` (str, optional): Contact display name
- `locale` (str, optional): Contact locale
- `tags` (list, optional): Contact tags
- `metadata` (dict, optional): WhatsApp-specific metadata

**Returns:** Dictionary with `contact_id`, `conversation_id`, and `message_id`

## Usage Example

```python
from app.storage import MessagePipeline, ConversationService

# Process incoming message
result = MessagePipeline.process_message_received(
    workspace_id=1,
    phone_e164="+14155552671",
    content="Hello, I need help",
    display_name="John Doe",
    locale="en_US",
    tags=["customer"],
    metadata={"whatsapp_message_id": "wamid.12345"}
)

print(f"Contact ID: {result['contact_id']}")
print(f"Conversation ID: {result['conversation_id']}")
print(f"Message ID: {result['message_id']}")

# Get conversation history
messages = ConversationService.get_conversation_history(
    conversation_id=result['conversation_id'],
    limit=10
)

# Get active conversations
active = ConversationService.get_active_conversations(workspace_id=1)

# Close conversation
ConversationService.close_conversation(conversation_id=result['conversation_id'])
```

## Database Migration

To create the tables in your database:

```bash
# Run the migration
alembic upgrade head
```

To rollback:

```bash
# Rollback one migration
alembic downgrade -1
```

## Performance Considerations

The implementation includes several performance optimizations:

1. **Composite Indexes**: Key combinations like `(workspace_id, phone_e164)` and `(conversation_id, created_at)` enable efficient queries
2. **Targeted Queries**: Uses `select().where()` with appropriate filters
3. **Limit on History**: Default limit of 100 messages for history queries
4. **Status Filtering**: Indexes on status fields for quick filtering of active conversations

## Design Decisions

1. **Tags as JSON String**: Stored as JSON string for simplicity and flexibility
2. **Message Metadata**: WhatsApp-specific data (message IDs, timestamps, etc.) stored as JSON
3. **Upsert Pattern**: Contacts and conversations are upserted to handle duplicate messages gracefully
4. **Open/Closed Status**: Simple two-state model for conversation lifecycle
5. **Workspace Isolation**: All queries are scoped by workspace_id for multi-tenancy
