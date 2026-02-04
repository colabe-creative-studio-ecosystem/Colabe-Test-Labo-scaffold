"""WhatsApp message pipeline handler."""
from typing import Optional, Dict, Any
from app.storage.conversation_service import ConversationService


class MessagePipeline:
    """Pipeline for processing incoming WhatsApp messages."""

    @staticmethod
    def process_message_received(
        workspace_id: int,
        phone_e164: str,
        content: str,
        display_name: Optional[str] = None,
        locale: Optional[str] = None,
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Process an incoming WhatsApp message.
        
        Pipeline steps:
        1. Upsert Contact by phone
        2. Upsert Conversation
        3. Attach message to conversation history
        
        Args:
            workspace_id: The workspace/tenant ID
            phone_e164: Phone number in E.164 format
            content: Message content
            display_name: Optional display name for the contact
            locale: Optional locale for the contact
            tags: Optional tags for the contact
            metadata: Optional WhatsApp-specific metadata
            
        Returns:
            Dictionary with contact_id, conversation_id, and message_id
        """
        # Step 1: Upsert Contact
        contact = ConversationService.upsert_contact(
            workspace_id=workspace_id,
            phone_e164=phone_e164,
            display_name=display_name,
            locale=locale,
            tags=tags,
        )

        # Step 2: Upsert Conversation
        conversation = ConversationService.upsert_conversation(
            workspace_id=workspace_id,
            contact_id=contact.id,
            channel="whatsapp",
        )

        # Step 3: Attach message to conversation history
        message = ConversationService.add_message(
            conversation_id=conversation.id,
            direction="inbound",
            content=content,
            metadata=metadata,
        )

        return {
            "contact_id": contact.id,
            "conversation_id": conversation.id,
            "message_id": message.id,
        }
