"""Unit tests for WhatsAppEventParser."""

import pytest
from app.integrations.whatsapp_event_parser import WhatsAppEventParser, EngineEvent


class TestWhatsAppEventParser:
    """Test suite for WhatsAppEventParser."""

    def test_parse_webhook_with_text_message(self):
        """Test parsing a webhook with a text message."""
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "123456789",
                                    "display_phone_number": "+1234567890"
                                },
                                "messages": [
                                    {
                                        "id": "msg_123",
                                        "from": "1234567890",
                                        "timestamp": "1234567890",
                                        "type": "text",
                                        "text": {
                                            "body": "Hello, world!"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        events = WhatsAppEventParser.parse_webhook(payload)
        
        assert len(events) == 1
        event = events[0]
        assert event.event_type == "message"
        assert event.phone_number_id == "123456789"
        assert event.from_number == "1234567890"
        assert event.message_id == "msg_123"
        assert event.message_type == "text"
        assert event.text_body == "Hello, world!"

    def test_parse_webhook_with_status(self):
        """Test parsing a webhook with a status update."""
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "123456789",
                                    "display_phone_number": "+1234567890"
                                },
                                "statuses": [
                                    {
                                        "id": "msg_123",
                                        "recipient_id": "1234567890",
                                        "status": "delivered",
                                        "timestamp": "1234567890"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        events = WhatsAppEventParser.parse_webhook(payload)
        
        assert len(events) == 1
        event = events[0]
        assert event.event_type == "status"
        assert event.phone_number_id == "123456789"
        assert event.from_number == "1234567890"
        assert event.message_id == "msg_123"
        assert event.metadata['status'] == "delivered"

    def test_parse_webhook_with_multiple_messages(self):
        """Test parsing a webhook with multiple messages."""
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "123456789"
                                },
                                "messages": [
                                    {
                                        "id": "msg_1",
                                        "from": "1111111111",
                                        "timestamp": "1234567890",
                                        "type": "text",
                                        "text": {"body": "First message"}
                                    },
                                    {
                                        "id": "msg_2",
                                        "from": "2222222222",
                                        "timestamp": "1234567891",
                                        "type": "text",
                                        "text": {"body": "Second message"}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        events = WhatsAppEventParser.parse_webhook(payload)
        
        assert len(events) == 2
        assert events[0].message_id == "msg_1"
        assert events[1].message_id == "msg_2"

    def test_parse_webhook_empty_payload(self):
        """Test parsing an empty webhook payload."""
        payload = {}
        events = WhatsAppEventParser.parse_webhook(payload)
        assert len(events) == 0

    def test_parse_webhook_missing_phone_number_id(self):
        """Test parsing webhook with missing phone_number_id."""
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {},
                                "messages": [
                                    {
                                        "id": "msg_123",
                                        "from": "1234567890",
                                        "timestamp": "1234567890",
                                        "type": "text",
                                        "text": {"body": "Hello"}
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        # Should skip the message due to missing phone_number_id
        events = WhatsAppEventParser.parse_webhook(payload)
        assert len(events) == 0

    def test_parse_webhook_invalid_payload_type(self):
        """Test parsing with invalid payload type."""
        with pytest.raises(ValueError, match="Payload must be a dictionary"):
            WhatsAppEventParser.parse_webhook("invalid")

    def test_redact_pii_phone_numbers(self):
        """Test PII redaction of phone numbers."""
        text = "Call me at 1234567890 or 9876543210"
        redacted = WhatsAppEventParser.redact_pii(text)
        assert "[REDACTED_PHONE]" in redacted
        assert "1234567890" not in redacted

    def test_redact_pii_long_text(self):
        """Test PII redaction truncates long text."""
        long_text = "a" * 150
        redacted = WhatsAppEventParser.redact_pii(long_text)
        assert len(redacted) == 100
        assert redacted.endswith("...")

    def test_redact_pii_none_text(self):
        """Test PII redaction with None."""
        assert WhatsAppEventParser.redact_pii(None) is None

    def test_engine_event_to_dict(self):
        """Test EngineEvent.to_dict() method."""
        event = EngineEvent(
            event_type="message",
            phone_number_id="123456789",
            from_number="1234567890",
            message_id="msg_123",
            timestamp="1234567890",
            message_type="text",
            text_body="Hello",
            metadata={"key": "value"}
        )
        
        result = event.to_dict()
        
        assert result['event_type'] == "message"
        assert result['phone_number_id'] == "123456789"
        assert result['from_number'] == "1234567890"
        assert result['message_id'] == "msg_123"
        assert result['text_body'] == "Hello"
        assert result['metadata']['key'] == "value"

    def test_engine_event_repr(self):
        """Test EngineEvent.__repr__() method."""
        event = EngineEvent(
            event_type="message",
            phone_number_id="123456789"
        )
        
        repr_str = repr(event)
        assert "EngineEvent" in repr_str
        assert "message" in repr_str
        assert "123456789" in repr_str

    def test_parse_webhook_with_image_message(self):
        """Test parsing a webhook with an image message (non-text)."""
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "123456789"
                                },
                                "messages": [
                                    {
                                        "id": "msg_123",
                                        "from": "1234567890",
                                        "timestamp": "1234567890",
                                        "type": "image",
                                        "image": {
                                            "id": "img_123"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        events = WhatsAppEventParser.parse_webhook(payload)
        
        assert len(events) == 1
        event = events[0]
        assert event.event_type == "message"
        assert event.message_type == "image"
        assert event.text_body is None  # No text for image messages
