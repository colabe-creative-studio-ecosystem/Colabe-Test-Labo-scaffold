#!/usr/bin/env python3
"""
Demonstration script for WhatsApp connector abstraction layer.

This script shows how to use the WhatsApp provider interfaces for:
- Sending various types of messages
- Parsing incoming webhooks
- Verifying webhook signatures
"""
import sys
import json
import os
from datetime import datetime

# Add parent directory to path for imports (dynamic path resolution)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.insert(0, project_root)

from app.core.whatsapp import (
    SimulationProvider,
    SimulationEventParser,
    CloudWebhookVerifier,
    MessageButton,
    ListItem,
    EventType,
)


def demo_simulation_provider():
    """Demonstrate the SimulationProvider capabilities."""
    print("=" * 60)
    print("SIMULATION PROVIDER DEMO")
    print("=" * 60)
    print()
    
    # Initialize provider
    provider = SimulationProvider()
    
    # 1. Send text message
    print("1. Sending text message...")
    receipt = provider.send_text(
        to="+1234567890",
        text="Hello! This is a test message from the WhatsApp connector.",
        meta={"flow": "demo", "step": 1}
    )
    print(f"   ✓ Message sent: {receipt.message_id}")
    print(f"   ✓ Timestamp: {receipt.timestamp}")
    print(f"   ✓ Success: {receipt.success}")
    print()
    
    # 2. Send button message
    print("2. Sending button message...")
    buttons = [
        MessageButton(id="btn_yes", title="✓ Yes, continue"),
        MessageButton(id="btn_no", title="✗ No, thanks"),
        MessageButton(id="btn_later", title="⏰ Remind me later"),
    ]
    receipt = provider.send_buttons(
        to="+1234567890",
        text="Would you like to proceed with the demo?",
        buttons=buttons
    )
    print(f"   ✓ Button message sent: {receipt.message_id}")
    print(f"   ✓ Buttons: {len(buttons)} options")
    print()
    
    # 3. Send list message
    print("3. Sending list message...")
    items = [
        ListItem(
            id="demo_basic",
            title="Basic Features",
            description="Text, buttons, and lists",
            section="Demos"
        ),
        ListItem(
            id="demo_media",
            title="Media Messages",
            description="Images, videos, documents",
            section="Demos"
        ),
        ListItem(
            id="demo_webhook",
            title="Webhook Processing",
            description="Parse incoming events",
            section="Demos"
        ),
    ]
    receipt = provider.send_list(
        to="+1234567890",
        header="Choose a demo to explore:",
        items=items
    )
    print(f"   ✓ List message sent: {receipt.message_id}")
    print(f"   ✓ Items: {len(items)} options")
    print()
    
    # 4. Send media message
    print("4. Sending media message...")
    receipt = provider.send_media(
        to="+1234567890",
        media_url_or_id="https://example.com/demo-image.jpg",
        caption="This is a demo image from the WhatsApp connector"
    )
    print(f"   ✓ Media message sent: {receipt.message_id}")
    print()
    
    # 5. Mark message as read
    print("5. Marking message as read...")
    provider.mark_read("msg_incoming_123")
    print(f"   ✓ Message marked as read")
    print()


def demo_event_parser():
    """Demonstrate the event parsing capabilities."""
    print("=" * 60)
    print("EVENT PARSER DEMO")
    print("=" * 60)
    print()
    
    parser = SimulationEventParser()
    
    # 1. Parse text message
    print("1. Parsing text message webhook...")
    webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "msg_abc123",
                        "from": "+1234567890",
                        "text": {"body": "Hello, I need help!"},
                        "timestamp": str(int(datetime.now().timestamp()))
                    }]
                }
            }]
        }]
    }
    events = parser.parse(webhook)
    for event in events:
        print(f"   ✓ Event: {event.event_type}")
        print(f"   ✓ From: {event.from_number}")
        print(f"   ✓ Text: {event.text}")
    print()
    
    # 2. Parse button click
    print("2. Parsing button click webhook...")
    webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "msg_def456",
                        "from": "+1234567890",
                        "button": {"payload": "btn_yes"},
                        "timestamp": str(int(datetime.now().timestamp()))
                    }]
                }
            }]
        }]
    }
    events = parser.parse(webhook)
    for event in events:
        print(f"   ✓ Event: {event.event_type}")
        print(f"   ✓ Button ID: {event.button_id}")
    print()
    
    # 3. Parse list selection
    print("3. Parsing list selection webhook...")
    webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "msg_ghi789",
                        "from": "+1234567890",
                        "interactive": {
                            "type": "list_reply",
                            "list_reply": {"id": "demo_basic"}
                        },
                        "timestamp": str(int(datetime.now().timestamp()))
                    }]
                }
            }]
        }]
    }
    events = parser.parse(webhook)
    for event in events:
        print(f"   ✓ Event: {event.event_type}")
        print(f"   ✓ List item ID: {event.list_item_id}")
    print()
    
    # 4. Parse delivery status
    print("4. Parsing delivery status webhook...")
    webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "statuses": [{
                        "id": "msg_abc123",
                        "status": "delivered",
                        "timestamp": str(int(datetime.now().timestamp())),
                        "recipient_id": "+1234567890"
                    }]
                }
            }]
        }]
    }
    events = parser.parse(webhook)
    for event in events:
        print(f"   ✓ Event: {event.event_type}")
        print(f"   ✓ Message ID: {event.message_id}")
    print()


def demo_webhook_verification():
    """Demonstrate webhook signature verification."""
    print("=" * 60)
    print("WEBHOOK VERIFICATION DEMO")
    print("=" * 60)
    print()
    
    import hmac
    import hashlib
    
    app_secret = "demo_secret_key_12345"
    verifier = CloudWebhookVerifier(app_secret)
    
    # 1. Valid signature
    print("1. Verifying valid webhook signature...")
    webhook_body = b'{"entry":[{"changes":[{"value":{"messages":[]}}]}]}'
    valid_signature = hmac.new(
        app_secret.encode(),
        webhook_body,
        hashlib.sha256
    ).hexdigest()
    
    is_valid = verifier.verify(f"sha256={valid_signature}", webhook_body)
    print(f"   ✓ Verification result: {is_valid}")
    print(f"   ✓ Expected: True")
    print()
    
    # 2. Invalid signature
    print("2. Verifying invalid webhook signature...")
    invalid_signature = "invalid_signature_abc123"
    is_valid = verifier.verify(f"sha256={invalid_signature}", webhook_body)
    print(f"   ✓ Verification result: {is_valid}")
    print(f"   ✓ Expected: False")
    print()


def demo_integration_flow():
    """Demonstrate a complete integration flow."""
    print("=" * 60)
    print("INTEGRATION FLOW DEMO")
    print("=" * 60)
    print()
    
    provider = SimulationProvider()
    parser = SimulationEventParser()
    
    # Simulate an outbound-inbound cycle
    print("Scenario: User onboarding flow")
    print()
    
    # Step 1: Bot sends welcome message
    print("1. Bot → User: Welcome message with buttons")
    buttons = [
        MessageButton(id="start", title="Get Started"),
        MessageButton(id="info", title="Learn More"),
    ]
    receipt = provider.send_buttons(
        to="+1234567890",
        text="Welcome! Ready to get started?",
        buttons=buttons
    )
    print(f"   ✓ Sent: {receipt.message_id}")
    print()
    
    # Step 2: User clicks button (simulated webhook)
    print("2. User → Bot: Clicks 'Get Started' button")
    webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "id": "msg_user_001",
                        "from": "+1234567890",
                        "button": {"payload": "start"},
                        "timestamp": str(int(datetime.now().timestamp()))
                    }]
                }
            }]
        }]
    }
    events = parser.parse(webhook)
    for event in events:
        print(f"   ✓ Received: {event.event_type}")
        print(f"   ✓ Button clicked: {event.button_id}")
    print()
    
    # Step 3: Bot responds with next step
    print("3. Bot → User: Next steps list")
    items = [
        ListItem(id="step1", title="Step 1: Setup", description="Configure your account"),
        ListItem(id="step2", title="Step 2: Connect", description="Link your services"),
        ListItem(id="step3", title="Step 3: Launch", description="Go live!"),
    ]
    receipt = provider.send_list(
        to="+1234567890",
        header="Choose your next step:",
        items=items
    )
    print(f"   ✓ Sent: {receipt.message_id}")
    print()
    
    print("✓ Integration flow completed successfully!")
    print()


def main():
    """Run all demonstrations."""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  WhatsApp Connector Abstraction Layer Demo".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    try:
        demo_simulation_provider()
        demo_event_parser()
        demo_webhook_verification()
        demo_integration_flow()
        
        print("=" * 60)
        print("ALL DEMOS COMPLETED SUCCESSFULLY! ✓")
        print("=" * 60)
        print()
        print("Next steps:")
        print("  1. Review the README.md for detailed usage examples")
        print("  2. Run tests with: python3 -m pytest tests/test_whatsapp_provider.py -v")
        print("  3. Integrate with your engine's ActionPlan system")
        print("  4. Implement CloudProvider for production use")
        print()
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
