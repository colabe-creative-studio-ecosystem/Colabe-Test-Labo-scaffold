"""
Simulation WhatsApp Provider

A provider implementation that simulates WhatsApp operations without network calls.
All operations are logged to trace for debugging and testing purposes.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

from .provider import (
    WhatsAppProvider,
    WebhookVerifier,
    WhatsAppEventParser,
    MessageReceipt,
    MessageButton,
    ListItem,
    EngineEvent,
    EventType,
)

logger = logging.getLogger(__name__)


class SimulationProvider(WhatsAppProvider):
    """
    Simulation provider for WhatsApp.
    
    No network calls are made. All operations write to trace logs.
    Useful for development, testing, and debugging without hitting real APIs.
    """

    def __init__(self, trace_file: Optional[str] = None):
        """
        Initialize the simulation provider.
        
        Args:
            trace_file: Optional file path to write trace logs (defaults to logger only)
        """
        self.trace_file = trace_file
        self.message_counter = 0
        self._write_trace("SimulationProvider initialized")

    def _write_trace(self, message: str, data: Optional[Dict[str, Any]] = None):
        """Write a trace message to the log and optional file."""
        trace_entry = {
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "data": data or {},
        }
        
        # Log to standard logger
        logger.info(f"[WhatsApp Simulation] {message}", extra={"data": data})
        
        # Optionally write to trace file
        if self.trace_file:
            try:
                with open(self.trace_file, "a") as f:
                    f.write(json.dumps(trace_entry) + "\n")
            except Exception as e:
                logger.error(f"Failed to write to trace file: {e}")

    def _generate_message_id(self) -> str:
        """Generate a simulated message ID."""
        self.message_counter += 1
        return f"sim_msg_{self.message_counter}_{datetime.now().timestamp()}"

    def send_text(
        self,
        to: str,
        text: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """Send a simulated text message."""
        message_id = self._generate_message_id()
        
        self._write_trace(
            "send_text",
            {
                "to": to,
                "text": text,
                "message_id": message_id,
                "meta": meta,
            }
        )
        
        return MessageReceipt(
            message_id=message_id,
            timestamp=datetime.now(),
            success=True,
            metadata=meta,
        )

    def send_buttons(
        self,
        to: str,
        text: str,
        buttons: List[MessageButton],
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """Send a simulated button message."""
        message_id = self._generate_message_id()
        
        self._write_trace(
            "send_buttons",
            {
                "to": to,
                "text": text,
                "buttons": [
                    {"id": btn.id, "title": btn.title, "type": btn.type}
                    for btn in buttons
                ],
                "message_id": message_id,
                "meta": meta,
            }
        )
        
        return MessageReceipt(
            message_id=message_id,
            timestamp=datetime.now(),
            success=True,
            metadata=meta,
        )

    def send_list(
        self,
        to: str,
        header: str,
        items: List[ListItem],
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """Send a simulated list message."""
        message_id = self._generate_message_id()
        
        self._write_trace(
            "send_list",
            {
                "to": to,
                "header": header,
                "items": [
                    {
                        "id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "section": item.section,
                    }
                    for item in items
                ],
                "message_id": message_id,
                "meta": meta,
            }
        )
        
        return MessageReceipt(
            message_id=message_id,
            timestamp=datetime.now(),
            success=True,
            metadata=meta,
        )

    def send_media(
        self,
        to: str,
        media_url_or_id: str,
        caption: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """Send a simulated media message."""
        message_id = self._generate_message_id()
        
        self._write_trace(
            "send_media",
            {
                "to": to,
                "media_url_or_id": media_url_or_id,
                "caption": caption,
                "message_id": message_id,
                "meta": meta,
            }
        )
        
        return MessageReceipt(
            message_id=message_id,
            timestamp=datetime.now(),
            success=True,
            metadata=meta,
        )

    def mark_read(self, message_id: str) -> None:
        """Mark a simulated message as read."""
        self._write_trace(
            "mark_read",
            {"message_id": message_id}
        )


class SimulationWebhookVerifier(WebhookVerifier):
    """
    Simulation webhook verifier.
    
    Always returns True for development/testing purposes.
    In production, use a real verifier with HMAC signature checking.
    """

    def __init__(self, always_valid: bool = True):
        """
        Initialize the simulation verifier.
        
        Args:
            always_valid: If True, always return valid. If False, always invalid.
        """
        self.always_valid = always_valid
        logger.info(f"SimulationWebhookVerifier initialized (always_valid={always_valid})")

    def verify(self, signature: str, raw_body: bytes) -> bool:
        """Simulate webhook verification."""
        logger.info(
            f"[WhatsApp Simulation] Webhook verification (result={self.always_valid})",
            extra={"signature_length": len(signature), "body_length": len(raw_body)}
        )
        return self.always_valid


class SimulationEventParser(WhatsAppEventParser):
    """
    Simulation event parser.
    
    Parses basic webhook structures for testing.
    Real implementation should handle WhatsApp Cloud API webhook format.
    """

    def parse(self, raw_webhook: Dict[str, Any]) -> List[EngineEvent]:
        """
        Parse simulated webhook payload.
        
        Expected format (simplified):
        {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "msg_123",
                            "from": "+1234567890",
                            "text": {"body": "Hello"},
                            "timestamp": "1234567890"
                        }]
                    }
                }]
            }]
        }
        """
        events: List[EngineEvent] = []
        
        try:
            # Parse WhatsApp webhook structure
            entries = raw_webhook.get("entry", [])
            
            for entry in entries:
                changes = entry.get("changes", [])
                
                for change in changes:
                    value = change.get("value", {})
                    messages = value.get("messages", [])
                    
                    for message in messages:
                        event = self._parse_message(message)
                        if event:
                            events.append(event)
                    
                    # Parse statuses (delivery, read receipts, etc.)
                    statuses = value.get("statuses", [])
                    for status in statuses:
                        event = self._parse_status(status)
                        if event:
                            events.append(event)
        
        except Exception as e:
            logger.error(f"Error parsing webhook: {e}", exc_info=True)
        
        logger.info(f"Parsed {len(events)} events from webhook")
        return events

    def _parse_message(self, message: Dict[str, Any]) -> Optional[EngineEvent]:
        """Parse a message object into an EngineEvent."""
        try:
            message_id = message.get("id")
            from_number = message.get("from")
            timestamp_str = message.get("timestamp", str(int(datetime.now().timestamp())))
            
            # Parse timestamp (Unix timestamp)
            timestamp = datetime.fromtimestamp(int(timestamp_str))
            
            # Text message
            if "text" in message:
                text = message["text"].get("body", "")
                return EngineEvent(
                    event_type=EventType.MESSAGE_RECEIVED,
                    timestamp=timestamp,
                    from_number=from_number,
                    message_id=message_id,
                    text=text,
                )
            
            # Button reply
            if "button" in message:
                button_id = message["button"].get("payload")
                return EngineEvent(
                    event_type=EventType.BUTTON_CLICKED,
                    timestamp=timestamp,
                    from_number=from_number,
                    message_id=message_id,
                    button_id=button_id,
                )
            
            # List reply
            if "interactive" in message:
                interactive = message["interactive"]
                if interactive.get("type") == "list_reply":
                    list_reply = interactive.get("list_reply", {})
                    list_item_id = list_reply.get("id")
                    return EngineEvent(
                        event_type=EventType.LIST_SELECTED,
                        timestamp=timestamp,
                        from_number=from_number,
                        message_id=message_id,
                        list_item_id=list_item_id,
                    )
            
            # Media message
            for media_type in ["image", "video", "document", "audio"]:
                if media_type in message:
                    media_url = message[media_type].get("url")
                    caption = message[media_type].get("caption")
                    return EngineEvent(
                        event_type=EventType.MESSAGE_RECEIVED,
                        timestamp=timestamp,
                        from_number=from_number,
                        message_id=message_id,
                        text=caption,
                        media_url=media_url,
                    )
            
            return None
        
        except Exception as e:
            logger.error(f"Error parsing message: {e}", exc_info=True)
            return None

    def _parse_status(self, status: Dict[str, Any]) -> Optional[EngineEvent]:
        """Parse a status update into an EngineEvent."""
        try:
            message_id = status.get("id")
            status_type = status.get("status")
            timestamp_str = status.get("timestamp", str(int(datetime.now().timestamp())))
            timestamp = datetime.fromtimestamp(int(timestamp_str))
            recipient = status.get("recipient_id", "")
            
            event_type_map = {
                "delivered": EventType.MESSAGE_DELIVERED,
                "read": EventType.MESSAGE_READ,
                "failed": EventType.MESSAGE_FAILED,
            }
            
            event_type = event_type_map.get(status_type)
            if event_type:
                return EngineEvent(
                    event_type=event_type,
                    timestamp=timestamp,
                    from_number=recipient,
                    message_id=message_id,
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error parsing status: {e}", exc_info=True)
            return None
