# Agent Console - WhatsApp Human Handoff Integration

## Overview

This feature provides a comprehensive agent console for managing WhatsApp conversations with human handoff capabilities. Agents can monitor conversations, reply manually, and seamlessly transition between AI automation and human support.

## Features

### 1. Conversation Management
- **Real-time Conversation List**: View all assigned or unassigned conversations
- **Status Tracking**: Monitor conversation status (Automated, Human Handoff, Resolved)
- **Auto-Assignment**: Conversations are automatically assigned to agents when they open them
- **RBAC**: Agents only see conversations assigned to them or unassigned conversations requiring human intervention

### 2. Agent Interface
- **Conversation Timeline**: View complete message history with sender indicators
- **Message Types**: Differentiate between user messages, AI responses, and agent replies
- **Real-time Updates**: Conversation list and timeline update dynamically
- **Contact Information**: Display WhatsApp number and contact name

### 3. SLA Management
- **Visual SLA Timer**: Display time remaining until SLA deadline
- **Overdue Indicator**: Clear visual indication when SLA is breached
- **Deadline Tracking**: Each conversation has an associated SLA deadline

### 4. Manual Reply
- **Direct Messaging**: Agents can send manual replies to WhatsApp contacts
- **WhatsApp Integration**: Placeholder for dispatcher integration (sendText API)
- **Audit Trail**: All agent messages are logged for compliance

### 5. AI Summary
- **Conversation Summarization**: Generate AI-powered summaries of conversations
- **Context Understanding**: Quickly understand conversation history
- **On-demand Generation**: Generate or regenerate summaries as needed

### 6. Release to Automation
- **Seamless Handback**: Return conversations to AI automation
- **Status Management**: Automatically updates conversation status
- **Engine Integration**: Placeholder for automation engine resume

### 7. Security & Compliance
- **Role-Based Access Control**: Strict filtering of conversations by agent assignment
- **Full Audit Logging**: All agent actions are logged with user ID, tenant ID, and timestamps
- **Tenant Isolation**: Conversations are scoped to tenant for multi-tenancy support

## Database Schema

### Conversation Model
```python
- id: Primary key
- tenant_id: Foreign key to Tenant
- whatsapp_number: WhatsApp phone number
- contact_name: Optional contact name
- status: Enum (automated, human_handoff, resolved)
- assigned_agent_id: Foreign key to User (agent)
- ai_summary: Optional AI-generated summary
- sla_deadline: DateTime for SLA tracking
- created_at: UTC timestamp
- updated_at: UTC timestamp (auto-updated)
```

### Message Model
```python
- id: Primary key
- conversation_id: Foreign key to Conversation
- sender_type: Enum (user, ai, agent)
- sender_id: Optional foreign key to User (for agent messages)
- content: Message text
- timestamp: UTC timestamp
```

## Usage

### Accessing the Agent Console
1. Navigate to `/agent-console` in the application
2. Login with valid credentials
3. The page will load all conversations assigned to you or unassigned conversations in human_handoff status

### Viewing Conversations
- Click on any conversation card to view its timeline
- The conversation will be auto-assigned to you if unassigned
- View the SLA timer to prioritize responses

### Replying to Conversations
1. Select a conversation
2. Type your reply in the text area
3. Click "Send Reply" to send the message
4. The message is logged in the audit trail

### Generating AI Summaries
1. Select a conversation
2. Click "Generate AI Summary" or "Regenerate" if a summary exists
3. The summary appears at the top of the conversation detail panel

### Releasing to Automation
1. Select a conversation
2. Click "Release to Automation"
3. The conversation status changes to "automated" and is unassigned
4. The conversation is removed from your active list

## Integration Points

### WhatsApp Dispatcher (TODO)
```python
# In conversation_state.py, send_reply method
# TODO: Send via WhatsApp dispatcher (sendText)
# await dispatcher.sendText(
#     self.selected_conversation.whatsapp_number, 
#     self.reply_text
# )
```

### Automation Engine (TODO)
```python
# In conversation_state.py, release_to_automation method
# TODO: Resume automation engine
# await engine.resume_automation(conv.id)
```

### AI Summary Generation (TODO)
```python
# In conversation_state.py, generate_ai_summary method
# Currently uses simple string concatenation
# In production, integrate with OpenAI or similar:
# summary = await openai.summarize_conversation(message_texts)
```

## Database Migration

Apply the migration to create the new tables:
```bash
alembic upgrade head
```

The migration file is located at:
`alembic/versions/aa034e5cfd10_add_whatsapp_conversation_and_message.py`

## Testing

### Create Sample Data
```bash
cd /home/runner/work/Colabe-Test-Labo-scaffold/Colabe-Test-Labo-scaffold
python -m app.scripts.create_sample_conversations
```

This will create sample conversations for testing the agent console.

## Security Considerations

1. **RBAC Enforcement**: Conversations are filtered at the database query level
2. **Tenant Isolation**: All queries include tenant_id filter
3. **Audit Logging**: All agent actions are logged with full context
4. **UTC Timestamps**: All timestamps use UTC to avoid timezone issues
5. **Automatic Updates**: The updated_at field is automatically managed by the database

## Future Enhancements

1. **Real-time WebSocket Updates**: Push updates to agents when new messages arrive
2. **Advanced AI Integration**: Use OpenAI/Anthropic for better summaries
3. **Rich Media Support**: Handle images, videos, and documents
4. **Canned Responses**: Quick reply templates for common scenarios
5. **Agent Status**: Online/offline/busy status indicators
6. **Conversation Transfer**: Transfer conversations between agents
7. **Analytics Dashboard**: Agent performance metrics and KPIs
8. **Mobile Responsive**: Optimize UI for mobile devices
