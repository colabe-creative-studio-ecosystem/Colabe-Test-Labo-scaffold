"""WhatsApp Event Parser for Inbound Messages

Parses WhatsApp webhook events and converts them to EngineEvent format.
Supports:
- Text messages
- Button replies
- List replies
- Media metadata (reference only)
- Delivery/read receipts (optional)
"""

from typing import Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WhatsAppParserError(Exception):
    """Base exception for WhatsApp parsing errors"""
    pass


class UnsupportedMessageTypeError(WhatsAppParserError):
    """Raised when message type is not supported"""
    pass


class InvalidMessageFormatError(WhatsAppParserError):
    """Raised when message format is invalid"""
    pass


def parse_whatsapp_webhook(webhook_payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Parse WhatsApp webhook payload and extract EngineEvent data.
    
    Args:
        webhook_payload: Raw webhook payload from WhatsApp API
        
    Returns:
        Dictionary containing EngineEvent fields, or None if not a message event
        
    Raises:
        InvalidMessageFormatError: If payload structure is invalid
        UnsupportedMessageTypeError: If message type is not supported
    """
    try:
        # Validate top-level structure
        if not isinstance(webhook_payload, dict):
            raise InvalidMessageFormatError("Webhook payload must be a dictionary")
        
        if "entry" not in webhook_payload:
            raise InvalidMessageFormatError("Missing 'entry' field in webhook payload")
        
        entries = webhook_payload.get("entry", [])
        if not isinstance(entries, list) or len(entries) == 0:
            raise InvalidMessageFormatError("'entry' must be a non-empty list")
        
        # Process first entry
        entry = entries[0]
        if not isinstance(entry, dict):
            raise InvalidMessageFormatError("Entry must be a dictionary")
        
        changes = entry.get("changes", [])
        if not isinstance(changes, list) or len(changes) == 0:
            raise InvalidMessageFormatError("'changes' must be a non-empty list")
        
        # Process first change
        change = changes[0]
        if not isinstance(change, dict):
            raise InvalidMessageFormatError("Change must be a dictionary")
        
        value = change.get("value", {})
        if not isinstance(value, dict):
            raise InvalidMessageFormatError("'value' must be a dictionary")
        
        # Extract metadata
        metadata = value.get("metadata", {})
        if not isinstance(metadata, dict):
            raise InvalidMessageFormatError("'metadata' must be a dictionary")
        
        workspace_id = metadata.get("phone_number_id")
        if not workspace_id:
            raise InvalidMessageFormatError("Missing 'phone_number_id' in metadata")
        
        # Check if this is a message event
        messages = value.get("messages", [])
        if not isinstance(messages, list) or len(messages) == 0:
            # Check for status updates (delivery/read receipts)
            statuses = value.get("statuses", [])
            if isinstance(statuses, list) and len(statuses) > 0:
                return _parse_status_update(statuses[0], workspace_id)
            return None  # Not a message or status event
        
        # Process message
        message = messages[0]
        if not isinstance(message, dict):
            raise InvalidMessageFormatError("Message must be a dictionary")
        
        return _parse_message(message, workspace_id)
        
    except (KeyError, IndexError, TypeError) as e:
        logger.error(f"Error parsing WhatsApp webhook: {e}")
        raise InvalidMessageFormatError(f"Invalid webhook structure: {e}")


def _parse_message(message: Dict[str, Any], workspace_id: str) -> Dict[str, Any]:
    """
    Parse a WhatsApp message and extract EngineEvent fields.
    
    Args:
        message: Message object from webhook
        workspace_id: Phone number ID (workspace identifier)
        
    Returns:
        Dictionary with EngineEvent fields
        
    Raises:
        UnsupportedMessageTypeError: If message type is not supported
        InvalidMessageFormatError: If required fields are missing
    """
    # Extract basic fields
    message_id = message.get("id")
    if not message_id:
        raise InvalidMessageFormatError("Missing 'id' in message")
    
    contact_id = message.get("from")
    if not contact_id:
        raise InvalidMessageFormatError("Missing 'from' in message")
    
    timestamp_str = message.get("timestamp")
    if not timestamp_str:
        raise InvalidMessageFormatError("Missing 'timestamp' in message")
    
    try:
        # WhatsApp timestamps are Unix timestamps in seconds
        timestamp = datetime.fromtimestamp(int(timestamp_str))
    except (ValueError, TypeError) as e:
        raise InvalidMessageFormatError(f"Invalid timestamp format: {e}")
    
    message_type = message.get("type")
    if not message_type:
        raise InvalidMessageFormatError("Missing 'type' in message")
    
    # Use contact_id as conversation_id for now (can be enhanced with context)
    conversation_id = contact_id
    
    # Parse based on message type
    event_data = {
        "type": "message_received",
        "workspace_id": workspace_id,
        "conversation_id": conversation_id,
        "contact_id": contact_id,
        "message_id": message_id,
        "timestamp": timestamp,
    }
    
    if message_type == "text":
        # Text message
        text_obj = message.get("text", {})
        if not isinstance(text_obj, dict):
            raise InvalidMessageFormatError("'text' must be a dictionary")
        
        text = text_obj.get("body", "")
        event_data["text"] = text
        
    elif message_type == "interactive":
        # Button or list reply
        interactive_obj = message.get("interactive", {})
        if not isinstance(interactive_obj, dict):
            raise InvalidMessageFormatError("'interactive' must be a dictionary")
        
        interactive_type = interactive_obj.get("type")
        if not interactive_type:
            raise InvalidMessageFormatError("Missing 'type' in interactive message")
        
        if interactive_type == "button_reply":
            button_reply = interactive_obj.get("button_reply", {})
            if not isinstance(button_reply, dict):
                raise InvalidMessageFormatError("'button_reply' must be a dictionary")
            
            event_data["interactive_type"] = "button"
            event_data["interactive_id"] = button_reply.get("id", "")
            event_data["interactive_title"] = button_reply.get("title", "")
            event_data["text"] = button_reply.get("title", "")
            
        elif interactive_type == "list_reply":
            list_reply = interactive_obj.get("list_reply", {})
            if not isinstance(list_reply, dict):
                raise InvalidMessageFormatError("'list_reply' must be a dictionary")
            
            event_data["interactive_type"] = "list"
            event_data["interactive_id"] = list_reply.get("id", "")
            event_data["interactive_title"] = list_reply.get("title", "")
            event_data["text"] = list_reply.get("title", "")
            
        else:
            raise UnsupportedMessageTypeError(
                f"Unsupported interactive type: {interactive_type}"
            )
    
    elif message_type in ["image", "video", "audio", "document", "sticker", "voice"]:
        # Media message - store reference only
        media_obj = message.get(message_type, {})
        if not isinstance(media_obj, dict):
            raise InvalidMessageFormatError(f"'{message_type}' must be a dictionary")
        
        media_id = media_obj.get("id", "")
        caption = media_obj.get("caption", "")
        
        # Store media reference in text field
        event_data["text"] = f"[{message_type.upper()}:{media_id}]"
        if caption:
            event_data["text"] += f" {caption}"
            
    elif message_type in ["location", "contacts"]:
        # Location and contacts are not supported but we'll log them
        logger.warning(f"Received unsupported message type: {message_type}")
        raise UnsupportedMessageTypeError(f"Message type not supported: {message_type}")
        
    else:
        # Unknown message type
        logger.warning(f"Received unknown message type: {message_type}")
        raise UnsupportedMessageTypeError(f"Unknown message type: {message_type}")
    
    return event_data


def _parse_status_update(status: Dict[str, Any], workspace_id: str) -> Optional[Dict[str, Any]]:
    """
    Parse delivery/read receipt status update (optional feature).
    
    Args:
        status: Status object from webhook
        workspace_id: Phone number ID (workspace identifier)
        
    Returns:
        Dictionary with status event data, or None if not relevant
    """
    # Extract status fields
    message_id = status.get("id")
    recipient_id = status.get("recipient_id")
    status_type = status.get("status")
    timestamp_str = status.get("timestamp")
    
    if not all([message_id, recipient_id, status_type, timestamp_str]):
        logger.warning("Incomplete status update, skipping")
        return None
    
    try:
        timestamp = datetime.fromtimestamp(int(timestamp_str))
    except (ValueError, TypeError):
        logger.warning("Invalid timestamp in status update")
        return None
    
    # Only process delivered and read statuses
    if status_type not in ["delivered", "read"]:
        return None
    
    # Return status event data (not stored in EngineEvent table currently)
    return {
        "type": f"message_{status_type}",
        "workspace_id": workspace_id,
        "message_id": message_id,
        "contact_id": recipient_id,
        "timestamp": timestamp,
    }


def validate_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Validate WhatsApp webhook signature.
    
    Args:
        payload: Raw webhook payload bytes
        signature: Signature from X-Hub-Signature-256 header
        secret: App secret for signature validation
        
    Returns:
        True if signature is valid, False otherwise
    """
    import hmac
    import hashlib
    
    if not signature or not secret:
        return False
    
    # WhatsApp uses sha256 with format: sha256=<hash>
    if not signature.startswith("sha256="):
        return False
    
    expected_signature = signature[7:]  # Remove "sha256=" prefix
    
    # Calculate HMAC
    calculated_signature = hmac.new(
        secret.encode("utf-8"),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(calculated_signature, expected_signature)
