import logging
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class EngineEvent:
    """Represents a parsed WhatsApp event."""

    def __init__(
        self,
        event_type: str,
        phone_number_id: str,
        from_number: Optional[str] = None,
        message_id: Optional[str] = None,
        timestamp: Optional[str] = None,
        message_type: Optional[str] = None,
        text_body: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.event_type = event_type
        self.phone_number_id = phone_number_id
        self.from_number = from_number
        self.message_id = message_id
        self.timestamp = timestamp
        self.message_type = message_type
        self.text_body = text_body
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            'event_type': self.event_type,
            'phone_number_id': self.phone_number_id,
            'from_number': self.from_number,
            'message_id': self.message_id,
            'timestamp': self.timestamp,
            'message_type': self.message_type,
            'text_body': self.text_body,
            'metadata': self.metadata
        }

    def __repr__(self):
        return f"EngineEvent(event_type={self.event_type}, phone_number_id={self.phone_number_id})"


class WhatsAppEventParser:
    """Parses WhatsApp webhook payloads into EngineEvents."""

    @staticmethod
    def redact_pii(text: Optional[str]) -> Optional[str]:
        """
        Redact PII from text.
        For now, this is a simple implementation that truncates long text.
        In production, this should use more sophisticated PII detection.
        """
        if not text:
            return text
        
        # Redact phone numbers (basic pattern)
        text = re.sub(r'\b\d{10,15}\b', '[REDACTED_PHONE]', text)
        
        # Truncate long messages
        if len(text) > 100:
            return text[:97] + '...'
        
        return text

    @staticmethod
    def parse_webhook(payload: Dict[str, Any]) -> List[EngineEvent]:
        """
        Parse WhatsApp webhook payload into EngineEvents.
        
        Args:
            payload: The webhook JSON payload as a dictionary
            
        Returns:
            List of EngineEvent objects
            
        Raises:
            ValueError: If payload is invalid or missing required fields
        """
        events = []
        
        try:
            # Validate payload structure
            if not isinstance(payload, dict):
                raise ValueError("Payload must be a dictionary")
            
            # WhatsApp webhooks have an 'entry' field containing an array
            entry_list = payload.get('entry', [])
            if not entry_list:
                logger.warning("No entries found in webhook payload")
                return events
            
            for entry in entry_list:
                changes = entry.get('changes', [])
                
                for change in changes:
                    value = change.get('value', {})
                    
                    # Get phone number ID from metadata
                    metadata = value.get('metadata', {})
                    phone_number_id = metadata.get('phone_number_id')
                    
                    if not phone_number_id:
                        logger.warning("Missing phone_number_id in webhook")
                        continue
                    
                    # Parse messages
                    messages = value.get('messages', [])
                    for message in messages:
                        event = WhatsAppEventParser._parse_message(
                            message, phone_number_id, metadata
                        )
                        if event:
                            events.append(event)
                    
                    # Parse statuses
                    statuses = value.get('statuses', [])
                    for status in statuses:
                        event = WhatsAppEventParser._parse_status(
                            status, phone_number_id, metadata
                        )
                        if event:
                            events.append(event)
        
        except Exception as e:
            logger.exception(f"Error parsing webhook payload: {e}")
            raise ValueError(f"Failed to parse webhook: {str(e)}")
        
        return events

    @staticmethod
    def _parse_message(
        message: Dict[str, Any],
        phone_number_id: str,
        metadata: Dict[str, Any]
    ) -> Optional[EngineEvent]:
        """Parse a message object into an EngineEvent."""
        try:
            message_id = message.get('id')
            from_number = message.get('from')
            timestamp = message.get('timestamp')
            message_type = message.get('type')
            
            # Extract text body if it's a text message
            text_body = None
            if message_type == 'text':
                text_obj = message.get('text', {})
                text_body = WhatsAppEventParser.redact_pii(text_obj.get('body'))
            
            return EngineEvent(
                event_type='message',
                phone_number_id=phone_number_id,
                from_number=from_number,
                message_id=message_id,
                timestamp=timestamp,
                message_type=message_type,
                text_body=text_body,
                metadata={
                    'display_phone_number': metadata.get('display_phone_number'),
                    'raw_message_type': message_type
                }
            )
        except Exception as e:
            logger.exception(f"Error parsing message: {e}")
            return None

    @staticmethod
    def _parse_status(
        status: Dict[str, Any],
        phone_number_id: str,
        metadata: Dict[str, Any]
    ) -> Optional[EngineEvent]:
        """Parse a status update into an EngineEvent."""
        try:
            message_id = status.get('id')
            recipient_id = status.get('recipient_id')
            status_value = status.get('status')
            timestamp = status.get('timestamp')
            
            return EngineEvent(
                event_type='status',
                phone_number_id=phone_number_id,
                from_number=recipient_id,
                message_id=message_id,
                timestamp=timestamp,
                message_type='status',
                text_body=None,
                metadata={
                    'status': status_value,
                    'display_phone_number': metadata.get('display_phone_number')
                }
            )
        except Exception as e:
            logger.exception(f"Error parsing status: {e}")
            return None
