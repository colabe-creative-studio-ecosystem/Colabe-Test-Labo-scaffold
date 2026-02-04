"""
Simple script to create sample WhatsApp conversation data for testing the agent console.
Run this after the database migration is applied.
"""
import sys
from datetime import datetime, timedelta
from app.core.models import (
    Conversation,
    Message,
    ConversationStatusEnum,
    MessageSenderEnum,
    User,
    Tenant,
)
import reflex as rx


def create_sample_data():
    """Create sample conversations and messages for testing"""
    with rx.session() as session:
        # Get first tenant and user
        tenant = session.query(Tenant).first()
        user = session.query(User).first()

        if not tenant or not user:
            print("Error: No tenant or user found. Please register a user first.")
            return

        print(f"Creating sample data for tenant: {tenant.name}, user: {user.username}")

        # Create sample conversations
        conversations = [
            {
                "whatsapp_number": "+1234567890",
                "contact_name": "John Doe",
                "status": ConversationStatusEnum.HUMAN_HANDOFF,
                "assigned_agent_id": user.id,
                "sla_deadline": datetime.utcnow() + timedelta(hours=2),
                "ai_summary": "Customer asking about product pricing and availability",
            },
            {
                "whatsapp_number": "+0987654321",
                "contact_name": "Jane Smith",
                "status": ConversationStatusEnum.HUMAN_HANDOFF,
                "assigned_agent_id": None,
                "sla_deadline": datetime.utcnow() + timedelta(hours=4),
                "ai_summary": "Technical support request for integration issues",
            },
            {
                "whatsapp_number": "+5555555555",
                "contact_name": "Bob Johnson",
                "status": ConversationStatusEnum.AUTOMATED,
                "assigned_agent_id": None,
                "sla_deadline": datetime.utcnow() + timedelta(hours=24),
                "ai_summary": "General inquiry about services",
            },
        ]

        for conv_data in conversations:
            # Check if conversation already exists
            existing = session.query(Conversation).filter(
                Conversation.whatsapp_number == conv_data["whatsapp_number"]
            ).first()

            if existing:
                print(f"Conversation with {conv_data['whatsapp_number']} already exists")
                continue

            conv = Conversation(
                tenant_id=tenant.id,
                whatsapp_number=conv_data["whatsapp_number"],
                contact_name=conv_data["contact_name"],
                status=conv_data["status"],
                assigned_agent_id=conv_data["assigned_agent_id"],
                sla_deadline=conv_data["sla_deadline"],
                ai_summary=conv_data["ai_summary"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            session.add(conv)
            session.flush()

            # Add sample messages
            messages = [
                {
                    "sender_type": MessageSenderEnum.USER,
                    "content": "Hi, I need help with your service",
                    "timestamp": datetime.utcnow() - timedelta(minutes=30),
                },
                {
                    "sender_type": MessageSenderEnum.AI,
                    "content": "Hello! I'd be happy to help. What can I assist you with today?",
                    "timestamp": datetime.utcnow() - timedelta(minutes=29),
                },
                {
                    "sender_type": MessageSenderEnum.USER,
                    "content": "I have some questions about pricing",
                    "timestamp": datetime.utcnow() - timedelta(minutes=28),
                },
            ]

            for msg_data in messages:
                msg = Message(
                    conversation_id=conv.id,
                    sender_type=msg_data["sender_type"],
                    sender_id=user.id if msg_data["sender_type"] == MessageSenderEnum.AGENT else None,
                    content=msg_data["content"],
                    timestamp=msg_data["timestamp"],
                )
                session.add(msg)

            print(f"Created conversation with {conv_data['contact_name']} ({conv_data['whatsapp_number']})")

        session.commit()
        print("Sample data created successfully!")


if __name__ == "__main__":
    try:
        create_sample_data()
    except Exception as e:
        print(f"Error creating sample data: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
