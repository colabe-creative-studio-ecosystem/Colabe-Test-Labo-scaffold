"""
Example usage of the WhatsApp conversation state store.

This script demonstrates how to use the MessagePipeline and ConversationService
to handle incoming WhatsApp messages.
"""

from app.storage import MessagePipeline, ConversationService
from app.core.models import ConversationStatusEnum


def example_message_received():
    """Example of processing an incoming WhatsApp message."""
    
    # Simulate receiving a message from a WhatsApp user
    workspace_id = 1  # Example workspace ID
    phone_e164 = "+14155552671"  # Example phone in E.164 format
    content = "Hello, I need help with my order"
    display_name = "John Doe"
    locale = "en_US"
    tags = ["customer", "vip"]
    metadata = {
        "whatsapp_message_id": "wamid.12345",
        "timestamp": "2026-02-04T13:45:00Z",
    }
    
    # Process the message through the pipeline
    result = MessagePipeline.process_message_received(
        workspace_id=workspace_id,
        phone_e164=phone_e164,
        content=content,
        display_name=display_name,
        locale=locale,
        tags=tags,
        metadata=metadata,
    )
    
    print(f"✓ Message processed successfully:")
    print(f"  - Contact ID: {result['contact_id']}")
    print(f"  - Conversation ID: {result['conversation_id']}")
    print(f"  - Message ID: {result['message_id']}")
    
    return result


def example_get_conversation_history(conversation_id: int):
    """Example of retrieving conversation history."""
    
    messages = ConversationService.get_conversation_history(
        conversation_id=conversation_id,
        limit=10
    )
    
    print(f"\n✓ Retrieved {len(messages)} messages:")
    for msg in messages:
        print(f"  - [{msg.direction}] {msg.content[:50]}...")
    
    return messages


def example_get_active_conversations(workspace_id: int):
    """Example of retrieving active conversations."""
    
    conversations = ConversationService.get_active_conversations(
        workspace_id=workspace_id
    )
    
    print(f"\n✓ Active conversations: {len(conversations)}")
    for conv in conversations:
        print(f"  - Conversation #{conv.id} (Contact: {conv.contact_id}, Status: {conv.status})")
    
    return conversations


def example_close_conversation(conversation_id: int):
    """Example of closing a conversation."""
    
    conversation = ConversationService.close_conversation(
        conversation_id=conversation_id
    )
    
    print(f"\n✓ Conversation #{conversation_id} closed")
    print(f"  - Status: {conversation.status}")
    
    return conversation


if __name__ == "__main__":
    print("WhatsApp Conversation State Store - Example Usage")
    print("=" * 60)
    
    # Note: This example requires a database connection and proper setup
    # In a real scenario, you would:
    # 1. Run the Alembic migration to create the tables
    # 2. Have a valid workspace_id (tenant) in the database
    # 3. Configure the database connection in settings
    
    print("\nExample pipeline flow:")
    print("1. Process incoming message -> upsert Contact + Conversation + Message")
    print("2. Retrieve conversation history")
    print("3. Get active conversations for workspace")
    print("4. Close conversation when done")
    
    print("\n" + "=" * 60)
    print("To use in production:")
    print("1. Run migration: alembic upgrade head")
    print("2. Import and use MessagePipeline.process_message_received()")
    print("3. Use ConversationService methods for conversation management")
