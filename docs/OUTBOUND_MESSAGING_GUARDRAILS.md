# Outbound Messaging Guardrails - Implementation Guide

## Overview

This implementation provides comprehensive outbound messaging guardrails to prevent spam, protect users, and ensure system reliability. The system enforces multiple layers of protection including rate limiting, quiet hours, contact cooldowns, and circuit breakers.

## Features Implemented

### 1. **Per-Conversation Rate Limiting**
- **Limit**: 4 messages per 60 seconds per conversation (configurable)
- **Behavior**: Prevents rapid-fire messaging within a conversation
- **Configuration**: `MAX_MESSAGES_PER_CONVERSATION_WINDOW`, `CONVERSATION_WINDOW_SECONDS`

### 2. **Workspace Quiet Hours**
- **Purpose**: Prevent messages during specified hours
- **Default**: 22:00 - 08:00 (10 PM to 8 AM)
- **Configurable**: Per-tenant via admin UI
- **Timezone-aware**: Supports any timezone

### 3. **Contact Cooldown**
- **Default**: 5 minutes between messages to same contact
- **Purpose**: Prevent message fatigue and spam complaints
- **Configuration**: `DEFAULT_CONTACT_COOLDOWN_SECONDS`

### 4. **Circuit Breaker**
- **Threshold**: 10 failures in 10 minutes opens circuit (configurable)
- **Recovery**: 5 minutes before attempting half-open state
- **Admin Alerts**: Automatic logging to audit trail
- **Manual Reset**: Available via admin UI

## Testing

Run the test suite:

```bash
pytest tests/test_message_dispatcher.py -v
```

All 6 tests passing successfully!

---

**Version**: 1.0.0  
**Last Updated**: 2026-02-04  
**Author**: Colabe Development Team
