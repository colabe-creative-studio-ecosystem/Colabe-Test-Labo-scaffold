"""Tests for WhatsApp provider interfaces and implementations."""
import pytest
from datetime import datetime
from app.core.whatsapp import (
    SimulationProvider,
    SimulationWebhookVerifier,
    SimulationEventParser,
    CloudWebhookVerifier,
    CloudEventParser,
    MessageButton,
    ListItem,
    EventType,
)


class TestSimulationProvider:
    """Tests for SimulationProvider."""

    def test_send_text(self):
        """Test sending a text message."""
        provider = SimulationProvider()
        receipt = provider.send_text(
            to="+1234567890",
            text="Hello, World!",
            meta={"test": "value"}
        )
        
        assert receipt.success is True
        assert receipt.message_id.startswith("sim_msg_")
        assert receipt.metadata == {"test": "value"}
        assert isinstance(receipt.timestamp, datetime)

    def test_send_buttons(self):
        """Test sending a button message."""
        provider = SimulationProvider()
        buttons = [
            MessageButton(id="btn1", title="Option 1"),
            MessageButton(id="btn2", title="Option 2"),
        ]
        
        receipt = provider.send_buttons(
            to="+1234567890",
            text="Choose an option:",
            buttons=buttons
        )
        
        assert receipt.success is True
        assert receipt.message_id.startswith("sim_msg_")

    def test_send_list(self):
        """Test sending a list message."""
        provider = SimulationProvider()
        items = [
            ListItem(id="item1", title="Item 1", description="First item"),
            ListItem(id="item2", title="Item 2", description="Second item"),
        ]
        
        receipt = provider.send_list(
            to="+1234567890",
            header="Select an item:",
            items=items
        )
        
        assert receipt.success is True
        assert receipt.message_id.startswith("sim_msg_")

    def test_send_media(self):
        """Test sending a media message."""
        provider = SimulationProvider()
        receipt = provider.send_media(
            to="+1234567890",
            media_url_or_id="https://example.com/image.jpg",
            caption="Check this out!"
        )
        
        assert receipt.success is True
        assert receipt.message_id.startswith("sim_msg_")

    def test_mark_read(self):
        """Test marking a message as read."""
        provider = SimulationProvider()
        # Should not raise an exception
        provider.mark_read("msg_123")

    def test_message_counter_increments(self):
        """Test that message IDs increment."""
        provider = SimulationProvider()
        receipt1 = provider.send_text("+1234567890", "Test 1")
        receipt2 = provider.send_text("+1234567890", "Test 2")
        
        assert receipt1.message_id != receipt2.message_id


class TestSimulationWebhookVerifier:
    """Tests for SimulationWebhookVerifier."""

    def test_always_valid(self):
        """Test verifier that always returns valid."""
        verifier = SimulationWebhookVerifier(always_valid=True)
        result = verifier.verify("any_signature", b"any_body")
        assert result is True

    def test_always_invalid(self):
        """Test verifier that always returns invalid."""
        verifier = SimulationWebhookVerifier(always_valid=False)
        result = verifier.verify("any_signature", b"any_body")
        assert result is False


class TestSimulationEventParser:
    """Tests for SimulationEventParser."""

    def test_parse_text_message(self):
        """Test parsing a text message."""
        parser = SimulationEventParser()
        webhook = {
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
        
        events = parser.parse(webhook)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == EventType.MESSAGE_RECEIVED
        assert event.from_number == "+1234567890"
        assert event.text == "Hello"
        assert event.message_id == "msg_123"

    def test_parse_button_click(self):
        """Test parsing a button click."""
        parser = SimulationEventParser()
        webhook = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "msg_456",
                            "from": "+1234567890",
                            "button": {"payload": "btn_1"},
                            "timestamp": "1234567890"
                        }]
                    }
                }]
            }]
        }
        
        events = parser.parse(webhook)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == EventType.BUTTON_CLICKED
        assert event.button_id == "btn_1"

    def test_parse_list_selection(self):
        """Test parsing a list selection."""
        parser = SimulationEventParser()
        webhook = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "msg_789",
                            "from": "+1234567890",
                            "interactive": {
                                "type": "list_reply",
                                "list_reply": {"id": "list_item_1"}
                            },
                            "timestamp": "1234567890"
                        }]
                    }
                }]
            }]
        }
        
        events = parser.parse(webhook)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == EventType.LIST_SELECTED
        assert event.list_item_id == "list_item_1"

    def test_parse_status_delivered(self):
        """Test parsing a delivery status."""
        parser = SimulationEventParser()
        webhook = {
            "entry": [{
                "changes": [{
                    "value": {
                        "statuses": [{
                            "id": "msg_123",
                            "status": "delivered",
                            "timestamp": "1234567890",
                            "recipient_id": "+1234567890"
                        }]
                    }
                }]
            }]
        }
        
        events = parser.parse(webhook)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == EventType.MESSAGE_DELIVERED
        assert event.message_id == "msg_123"

    def test_parse_empty_webhook(self):
        """Test parsing an empty webhook."""
        parser = SimulationEventParser()
        events = parser.parse({})
        assert len(events) == 0

    def test_parse_multiple_messages(self):
        """Test parsing multiple messages in one webhook."""
        parser = SimulationEventParser()
        webhook = {
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [
                            {
                                "id": "msg_1",
                                "from": "+1234567890",
                                "text": {"body": "First"},
                                "timestamp": "1234567890"
                            },
                            {
                                "id": "msg_2",
                                "from": "+1234567890",
                                "text": {"body": "Second"},
                                "timestamp": "1234567891"
                            }
                        ]
                    }
                }]
            }]
        }
        
        events = parser.parse(webhook)
        assert len(events) == 2
        assert events[0].text == "First"
        assert events[1].text == "Second"


class TestCloudWebhookVerifier:
    """Tests for CloudWebhookVerifier."""

    def test_verify_valid_signature(self):
        """Test verification with a valid signature."""
        import hmac
        import hashlib
        
        app_secret = "test_secret"
        verifier = CloudWebhookVerifier(app_secret)
        
        raw_body = b'{"test": "data"}'
        expected_signature = hmac.new(
            app_secret.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        
        result = verifier.verify(f"sha256={expected_signature}", raw_body)
        assert result is True

    def test_verify_invalid_signature(self):
        """Test verification with an invalid signature."""
        verifier = CloudWebhookVerifier("test_secret")
        result = verifier.verify("sha256=invalid_signature", b'{"test": "data"}')
        assert result is False

    def test_verify_signature_without_prefix(self):
        """Test verification when signature doesn't have sha256= prefix."""
        import hmac
        import hashlib
        
        app_secret = "test_secret"
        verifier = CloudWebhookVerifier(app_secret)
        
        raw_body = b'{"test": "data"}'
        expected_signature = hmac.new(
            app_secret.encode(),
            raw_body,
            hashlib.sha256
        ).hexdigest()
        
        result = verifier.verify(expected_signature, raw_body)
        assert result is True


class TestCloudEventParser:
    """Tests for CloudEventParser."""

    def test_parse_cloud_api_text_message(self):
        """Test parsing WhatsApp Cloud API text message format."""
        parser = CloudEventParser()
        webhook = {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "BUSINESS_ACCOUNT_ID",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "messages": [{
                            "id": "wamid.123",
                            "from": "1234567890",
                            "type": "text",
                            "text": {"body": "Hello from Cloud API"},
                            "timestamp": "1234567890"
                        }]
                    },
                    "field": "messages"
                }]
            }]
        }
        
        events = parser.parse(webhook)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == EventType.MESSAGE_RECEIVED
        assert event.text == "Hello from Cloud API"
        assert event.message_id == "wamid.123"

    def test_parse_cloud_api_button_reply(self):
        """Test parsing WhatsApp Cloud API button reply format."""
        parser = CloudEventParser()
        webhook = {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "wamid.456",
                            "from": "1234567890",
                            "type": "button",
                            "button": {
                                "payload": "button_payload_1",
                                "text": "Yes"
                            },
                            "timestamp": "1234567890"
                        }]
                    }
                }]
            }]
        }
        
        events = parser.parse(webhook)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == EventType.BUTTON_CLICKED
        assert event.button_id == "button_payload_1"
        assert event.text == "Yes"

    def test_parse_cloud_api_image_message(self):
        """Test parsing WhatsApp Cloud API image message format."""
        parser = CloudEventParser()
        webhook = {
            "object": "whatsapp_business_account",
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "id": "wamid.789",
                            "from": "1234567890",
                            "type": "image",
                            "image": {
                                "id": "media_123",
                                "caption": "Check this out"
                            },
                            "timestamp": "1234567890"
                        }]
                    }
                }]
            }]
        }
        
        events = parser.parse(webhook)
        assert len(events) == 1
        
        event = events[0]
        assert event.event_type == EventType.MESSAGE_RECEIVED
        assert event.text == "Check this out"
        assert event.metadata["media_id"] == "media_123"
        assert event.metadata["media_type"] == "image"

    def test_parse_non_whatsapp_webhook(self):
        """Test parsing a non-WhatsApp webhook."""
        parser = CloudEventParser()
        webhook = {
            "object": "instagram",
            "entry": []
        }
        
        events = parser.parse(webhook)
        assert len(events) == 0
