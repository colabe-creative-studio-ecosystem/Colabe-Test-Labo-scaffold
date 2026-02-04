"""Tests for WhatsApp event parser"""

import pytest
from datetime import datetime
from app.integrations.whatsapp_parser import (
    parse_whatsapp_webhook,
    validate_webhook_signature,
    WhatsAppParserError,
    UnsupportedMessageTypeError,
    InvalidMessageFormatError,
)


class TestWhatsAppParser:
    """Test WhatsApp webhook parsing functionality"""

    def test_parse_text_message(self):
        """Test parsing a simple text message"""
        webhook_payload = {
            "object": "whatsapp_business_account",
            "entry": [
                {
                    "id": "123456",
                    "changes": [
                        {
                            "value": {
                                "messaging_product": "whatsapp",
                                "metadata": {
                                    "display_phone_number": "1234567890",
                                    "phone_number_id": "workspace123"
                                },
                                "contacts": [
                                    {
                                        "profile": {"name": "John Doe"},
                                        "wa_id": "contact123"
                                    }
                                ],
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
                            },
                            "field": "messages"
                        }
                    ]
                }
            ]
        }
        
        result = parse_whatsapp_webhook(webhook_payload)
        
        assert result is not None
        assert result["type"] == "message_received"
        assert result["workspace_id"] == "workspace123"
        assert result["contact_id"] == "contact123"
        assert result["conversation_id"] == "contact123"
        assert result["message_id"] == "message123"
        assert result["text"] == "Hello, World!"
        assert isinstance(result["timestamp"], datetime)

    def test_parse_button_reply(self):
        """Test parsing a button reply"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "messages": [
                                    {
                                        "from": "contact123",
                                        "id": "message456",
                                        "timestamp": "1234567890",
                                        "type": "interactive",
                                        "interactive": {
                                            "type": "button_reply",
                                            "button_reply": {
                                                "id": "btn_yes",
                                                "title": "Yes"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = parse_whatsapp_webhook(webhook_payload)
        
        assert result is not None
        assert result["type"] == "message_received"
        assert result["interactive_type"] == "button"
        assert result["interactive_id"] == "btn_yes"
        assert result["interactive_title"] == "Yes"
        assert result["text"] == "Yes"

    def test_parse_list_reply(self):
        """Test parsing a list reply"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "messages": [
                                    {
                                        "from": "contact123",
                                        "id": "message789",
                                        "timestamp": "1234567890",
                                        "type": "interactive",
                                        "interactive": {
                                            "type": "list_reply",
                                            "list_reply": {
                                                "id": "option_1",
                                                "title": "Option 1"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = parse_whatsapp_webhook(webhook_payload)
        
        assert result is not None
        assert result["interactive_type"] == "list"
        assert result["interactive_id"] == "option_1"
        assert result["interactive_title"] == "Option 1"

    def test_parse_image_message(self):
        """Test parsing an image message with caption"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "messages": [
                                    {
                                        "from": "contact123",
                                        "id": "message999",
                                        "timestamp": "1234567890",
                                        "type": "image",
                                        "image": {
                                            "id": "img_12345",
                                            "mime_type": "image/jpeg",
                                            "caption": "Check this out!"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = parse_whatsapp_webhook(webhook_payload)
        
        assert result is not None
        assert result["text"] == "[IMAGE:img_12345] Check this out!"

    def test_parse_video_message(self):
        """Test parsing a video message without caption"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "messages": [
                                    {
                                        "from": "contact123",
                                        "id": "message888",
                                        "timestamp": "1234567890",
                                        "type": "video",
                                        "video": {
                                            "id": "vid_67890",
                                            "mime_type": "video/mp4"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = parse_whatsapp_webhook(webhook_payload)
        
        assert result is not None
        assert result["text"] == "[VIDEO:vid_67890]"

    def test_parse_status_update(self):
        """Test parsing delivery receipt"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "statuses": [
                                    {
                                        "id": "message123",
                                        "status": "delivered",
                                        "timestamp": "1234567890",
                                        "recipient_id": "contact123"
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        result = parse_whatsapp_webhook(webhook_payload)
        
        assert result is not None
        assert result["type"] == "message_delivered"
        assert result["message_id"] == "message123"

    def test_unsupported_message_type(self):
        """Test that unsupported message types raise proper exception"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "messages": [
                                    {
                                        "from": "contact123",
                                        "id": "message111",
                                        "timestamp": "1234567890",
                                        "type": "location",
                                        "location": {
                                            "latitude": 37.7749,
                                            "longitude": -122.4194
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        with pytest.raises(UnsupportedMessageTypeError):
            parse_whatsapp_webhook(webhook_payload)

    def test_invalid_payload_structure(self):
        """Test that invalid payload structure raises proper exception"""
        # Missing 'entry' field
        webhook_payload = {"object": "whatsapp_business_account"}
        
        with pytest.raises(InvalidMessageFormatError):
            parse_whatsapp_webhook(webhook_payload)

    def test_missing_required_field(self):
        """Test that missing required fields raise proper exception"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "messages": [
                                    {
                                        # Missing 'from' field
                                        "id": "message123",
                                        "timestamp": "1234567890",
                                        "type": "text",
                                        "text": {
                                            "body": "Hello"
                                        }
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }
        
        with pytest.raises(InvalidMessageFormatError):
            parse_whatsapp_webhook(webhook_payload)

    def test_empty_messages_returns_none(self):
        """Test that webhook without messages returns None"""
        webhook_payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "metadata": {
                                    "phone_number_id": "workspace123"
                                },
                                "messages": []
                            }
                        }
                    ]
                }
            ]
        }
        
        result = parse_whatsapp_webhook(webhook_payload)
        assert result is None

    def test_validate_webhook_signature_valid(self):
        """Test webhook signature validation with valid signature"""
        payload = b'{"test": "data"}'
        secret = "my_secret"
        
        # Calculate expected signature
        import hmac
        import hashlib
        expected_sig = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()
        signature = f"sha256={expected_sig}"
        
        assert validate_webhook_signature(payload, signature, secret) is True

    def test_validate_webhook_signature_invalid(self):
        """Test webhook signature validation with invalid signature"""
        payload = b'{"test": "data"}'
        secret = "my_secret"
        signature = "sha256=invalid_signature"
        
        assert validate_webhook_signature(payload, signature, secret) is False

    def test_validate_webhook_signature_wrong_format(self):
        """Test webhook signature validation with wrong format"""
        payload = b'{"test": "data"}'
        secret = "my_secret"
        signature = "invalid_format"
        
        assert validate_webhook_signature(payload, signature, secret) is False
