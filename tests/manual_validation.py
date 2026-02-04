#!/usr/bin/env python3
"""
Manual validation script for WhatsApp event parser.
Demonstrates parsing of various message types.
"""

from app.integrations.whatsapp_parser import parse_whatsapp_webhook
from datetime import datetime
import json


def print_event(event):
    """Pretty print an event"""
    if event:
        print(json.dumps({
            k: str(v) if isinstance(v, datetime) else v 
            for k, v in event.items()
        }, indent=2))
    else:
        print("None (not a message event)")


def main():
    print("=" * 80)
    print("WhatsApp Event Parser - Manual Validation")
    print("=" * 80)
    
    # Test 1: Text Message
    print("\n1. TEXT MESSAGE:")
    print("-" * 80)
    text_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {"phone_number_id": "workspace123"},
                    "messages": [{
                        "from": "contact123",
                        "id": "msg_text_001",
                        "timestamp": "1234567890",
                        "type": "text",
                        "text": {"body": "Hello, this is a test message!"}
                    }]
                }
            }]
        }]
    }
    event = parse_whatsapp_webhook(text_webhook)
    print_event(event)
    
    # Test 2: Button Reply
    print("\n2. BUTTON REPLY:")
    print("-" * 80)
    button_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {"phone_number_id": "workspace456"},
                    "messages": [{
                        "from": "contact456",
                        "id": "msg_button_002",
                        "timestamp": "1234567891",
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {
                                "id": "btn_confirm",
                                "title": "Confirm Order"
                            }
                        }
                    }]
                }
            }]
        }]
    }
    event = parse_whatsapp_webhook(button_webhook)
    print_event(event)
    
    # Test 3: List Reply
    print("\n3. LIST REPLY:")
    print("-" * 80)
    list_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {"phone_number_id": "workspace789"},
                    "messages": [{
                        "from": "contact789",
                        "id": "msg_list_003",
                        "timestamp": "1234567892",
                        "type": "interactive",
                        "interactive": {
                            "type": "list_reply",
                            "list_reply": {
                                "id": "product_123",
                                "title": "Premium Plan"
                            }
                        }
                    }]
                }
            }]
        }]
    }
    event = parse_whatsapp_webhook(list_webhook)
    print_event(event)
    
    # Test 4: Media Message (Image)
    print("\n4. IMAGE MESSAGE:")
    print("-" * 80)
    image_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {"phone_number_id": "workspace101"},
                    "messages": [{
                        "from": "contact101",
                        "id": "msg_image_004",
                        "timestamp": "1234567893",
                        "type": "image",
                        "image": {
                            "id": "img_abc123",
                            "mime_type": "image/jpeg",
                            "caption": "Product photo"
                        }
                    }]
                }
            }]
        }]
    }
    event = parse_whatsapp_webhook(image_webhook)
    print_event(event)
    
    # Test 5: Delivery Receipt
    print("\n5. DELIVERY RECEIPT:")
    print("-" * 80)
    status_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {"phone_number_id": "workspace102"},
                    "statuses": [{
                        "id": "msg_original_005",
                        "status": "delivered",
                        "timestamp": "1234567894",
                        "recipient_id": "contact102"
                    }]
                }
            }]
        }]
    }
    event = parse_whatsapp_webhook(status_webhook)
    print_event(event)
    
    # Test 6: Error handling - Unsupported type
    print("\n6. UNSUPPORTED MESSAGE TYPE (Location):")
    print("-" * 80)
    location_webhook = {
        "entry": [{
            "changes": [{
                "value": {
                    "metadata": {"phone_number_id": "workspace103"},
                    "messages": [{
                        "from": "contact103",
                        "id": "msg_location_006",
                        "timestamp": "1234567895",
                        "type": "location",
                        "location": {
                            "latitude": 37.7749,
                            "longitude": -122.4194
                        }
                    }]
                }
            }]
        }]
    }
    try:
        event = parse_whatsapp_webhook(location_webhook)
        print_event(event)
    except Exception as e:
        print(f"✓ Correctly rejected: {type(e).__name__}: {e}")
    
    print("\n" + "=" * 80)
    print("Validation Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
