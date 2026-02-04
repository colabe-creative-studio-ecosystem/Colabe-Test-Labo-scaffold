"""Conversation state management service for WhatsApp threads."""
import reflex as rx
from sqlmodel import select, and_
from datetime import datetime, timezone
from typing import Optional, List
from app.core.models import Contact, Conversation, Message, ConversationStatusEnum


class ConversationService:
    """Service for managing WhatsApp conversation state."""

    @staticmethod
    def upsert_contact(
        workspace_id: int,
        phone_e164: str,
        display_name: Optional[str] = None,
        locale: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Contact:
        """Create or update a contact by phone number."""
        import json

        with rx.session() as session:
            # Try to find existing contact
            statement = select(Contact).where(
                and_(
                    Contact.workspace_id == workspace_id,
                    Contact.phone_e164 == phone_e164,
                )
            )
            contact = session.exec(statement).first()

            if contact:
                # Update existing contact
                if display_name:
                    contact.display_name = display_name
                if locale:
                    contact.locale = locale
                if tags is not None:
                    contact.tags = json.dumps(tags)
            else:
                # Create new contact
                contact = Contact(
                    workspace_id=workspace_id,
                    phone_e164=phone_e164,
                    display_name=display_name,
                    locale=locale,
                    tags=json.dumps(tags) if tags else None,
                )
                session.add(contact)

            session.commit()
            session.refresh(contact)
            return contact

    @staticmethod
    def upsert_conversation(
        workspace_id: int,
        contact_id: int,
        channel: str = "whatsapp",
        status: ConversationStatusEnum = ConversationStatusEnum.OPEN,
        last_intent: Optional[str] = None,
        stage: Optional[str] = None,
        assigned_agent_id: Optional[int] = None,
        awaiting_reply_key: Optional[str] = None,
    ) -> Conversation:
        """Create or update a conversation for a contact."""
        with rx.session() as session:
            # Try to find existing open conversation
            statement = select(Conversation).where(
                and_(
                    Conversation.workspace_id == workspace_id,
                    Conversation.contact_id == contact_id,
                    Conversation.channel == channel,
                    Conversation.status == ConversationStatusEnum.OPEN,
                )
            )
            conversation = session.exec(statement).first()

            if conversation:
                # Update existing conversation
                conversation.last_message_at = datetime.now(timezone.utc)
                if last_intent:
                    conversation.last_intent = last_intent
                if stage is not None:
                    conversation.stage = stage
                if assigned_agent_id is not None:
                    conversation.assigned_agent_id = assigned_agent_id
                if awaiting_reply_key is not None:
                    conversation.awaiting_reply_key = awaiting_reply_key
            else:
                # Create new conversation
                conversation = Conversation(
                    workspace_id=workspace_id,
                    channel=channel,
                    contact_id=contact_id,
                    status=status,
                    last_message_at=datetime.now(timezone.utc),
                    last_intent=last_intent,
                    stage=stage,
                    assigned_agent_id=assigned_agent_id,
                    awaiting_reply_key=awaiting_reply_key,
                )
                session.add(conversation)

            session.commit()
            session.refresh(conversation)
            return conversation

    @staticmethod
    def add_message(
        conversation_id: int,
        direction: str,
        content: str,
        metadata: Optional[dict] = None,
    ) -> Message:
        """Add a message to a conversation."""
        import json

        with rx.session() as session:
            message = Message(
                conversation_id=conversation_id,
                direction=direction,
                content=content,
                message_metadata=json.dumps(metadata) if metadata else None,
            )
            session.add(message)

            # Update conversation last_message_at
            conversation = session.get(Conversation, conversation_id)
            if conversation:
                conversation.last_message_at = datetime.now(timezone.utc)

            session.commit()
            session.refresh(message)
            return message

    @staticmethod
    def get_conversation_history(
        conversation_id: int, limit: int = 100
    ) -> List[Message]:
        """Get message history for a conversation."""
        with rx.session() as session:
            statement = (
                select(Message)
                .where(Message.conversation_id == conversation_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
            )
            messages = session.exec(statement).all()
            return list(messages)

    @staticmethod
    def close_conversation(conversation_id: int) -> Conversation:
        """Close a conversation."""
        with rx.session() as session:
            conversation = session.get(Conversation, conversation_id)
            if conversation:
                conversation.status = ConversationStatusEnum.CLOSED
                session.commit()
                session.refresh(conversation)
            return conversation

    @staticmethod
    def get_active_conversations(workspace_id: int) -> List[Conversation]:
        """Get all active conversations for a workspace."""
        with rx.session() as session:
            statement = (
                select(Conversation)
                .where(
                    and_(
                        Conversation.workspace_id == workspace_id,
                        Conversation.status == ConversationStatusEnum.OPEN,
                    )
                )
                .order_by(Conversation.last_message_at.desc())
            )
            conversations = session.exec(statement).all()
            return list(conversations)
