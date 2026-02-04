import reflex as rx
import sqlmodel
from datetime import datetime, timedelta
from sqlalchemy.orm import selectinload
from typing import Optional
from pydantic import BaseModel
from app.ui.states.auth_state import AuthState
from app.core.models import (
    Conversation,
    Message,
    ConversationStatusEnum,
    MessageSenderEnum,
    AuditLog,
    User,
)


class MessageDisplay(BaseModel):
    id: int
    sender_type: str
    sender_name: Optional[str] = None
    content: str
    timestamp: str


class ConversationDisplay(BaseModel):
    id: int
    whatsapp_number: str
    contact_name: Optional[str] = None
    status: str
    assigned_agent_name: Optional[str] = None
    ai_summary: Optional[str] = None
    sla_deadline: Optional[str] = None
    time_remaining: Optional[str] = None
    created_at: str
    updated_at: str
    message_count: int = 0


class ConversationState(rx.State):
    conversations: list[ConversationDisplay] = []
    selected_conversation: Optional[ConversationDisplay] = None
    messages: list[MessageDisplay] = []
    reply_text: str = ""
    loading: bool = False
    error_message: str = ""

    @rx.event
    async def load_conversations(self):
        """Load all conversations assigned to the current agent"""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return rx.redirect("/login")

        self.loading = True
        with rx.session() as session:
            # Load conversations assigned to this agent or unassigned ones in human_handoff status
            query = sqlmodel.select(Conversation).where(
                Conversation.tenant_id == auth_state.user.tenant_id
            )
            
            # RBAC: Agents only see their assigned conversations
            query = query.where(
                sqlmodel.or_(
                    Conversation.assigned_agent_id == auth_state.user.id,
                    sqlmodel.and_(
                        Conversation.assigned_agent_id.is_(None),
                        Conversation.status == ConversationStatusEnum.HUMAN_HANDOFF,
                    ),
                )
            )

            conversations = session.exec(
                query.options(
                    selectinload(Conversation.assigned_agent),
                    selectinload(Conversation.messages),
                ).order_by(sqlmodel.desc(Conversation.updated_at))
            ).all()

            self.conversations = [
                self._convert_conversation_to_display(conv) for conv in conversations
            ]
        self.loading = False

    def _convert_conversation_to_display(
        self, conv: Conversation
    ) -> ConversationDisplay:
        """Convert a Conversation model to ConversationDisplay"""
        time_remaining = None
        if conv.sla_deadline:
            delta = conv.sla_deadline - datetime.utcnow()
            if delta.total_seconds() > 0:
                hours = int(delta.total_seconds() // 3600)
                minutes = int((delta.total_seconds() % 3600) // 60)
                time_remaining = f"{hours}h {minutes}m"
            else:
                time_remaining = "OVERDUE"

        return ConversationDisplay(
            id=conv.id,
            whatsapp_number=conv.whatsapp_number,
            contact_name=conv.contact_name,
            status=conv.status,
            assigned_agent_name=conv.assigned_agent.username
            if conv.assigned_agent
            else None,
            ai_summary=conv.ai_summary,
            sla_deadline=conv.sla_deadline.isoformat() if conv.sla_deadline else None,
            time_remaining=time_remaining,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat(),
            message_count=len(conv.messages) if conv.messages else 0,
        )

    @rx.event
    async def select_conversation(self, conversation_id: int):
        """Select a conversation and load its messages"""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return rx.redirect("/login")

        self.loading = True
        with rx.session() as session:
            # Verify agent has access to this conversation (RBAC)
            conv = session.exec(
                sqlmodel.select(Conversation)
                .where(Conversation.id == conversation_id)
                .where(Conversation.tenant_id == auth_state.user.tenant_id)
                .options(
                    selectinload(Conversation.assigned_agent),
                    selectinload(Conversation.messages).selectinload(Message.sender),
                )
            ).first()

            if not conv:
                self.error_message = "Conversation not found or access denied"
                self.loading = False
                return

            # Check RBAC: agent can only access assigned conversations
            if conv.assigned_agent_id and conv.assigned_agent_id != auth_state.user.id:
                self.error_message = "You do not have access to this conversation"
                self.loading = False
                return

            # Auto-assign if unassigned
            if not conv.assigned_agent_id:
                conv.assigned_agent_id = auth_state.user.id
                session.add(conv)
                session.commit()
                session.refresh(conv)

            self.selected_conversation = self._convert_conversation_to_display(conv)

            # Load messages
            self.messages = [
                MessageDisplay(
                    id=msg.id,
                    sender_type=msg.sender_type,
                    sender_name=msg.sender.username if msg.sender else "AI",
                    content=msg.content,
                    timestamp=msg.timestamp.isoformat(),
                )
                for msg in sorted(conv.messages, key=lambda m: m.timestamp)
            ]

        self.loading = False

    @rx.event
    async def send_reply(self):
        """Send a manual reply from the agent"""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user or not self.selected_conversation:
            return

        if not self.reply_text.strip():
            self.error_message = "Reply text cannot be empty"
            return

        self.loading = True
        with rx.session() as session:
            # Create new message
            new_message = Message(
                conversation_id=self.selected_conversation.id,
                sender_type=MessageSenderEnum.AGENT,
                sender_id=auth_state.user.id,
                content=self.reply_text,
                timestamp=datetime.utcnow(),
            )
            session.add(new_message)

            # Note: Conversation updated_at will be automatically updated by onupdate trigger

            # Audit log for agent message
            audit_log = AuditLog(
                user_id=auth_state.user.id,
                tenant_id=auth_state.user.tenant_id,
                action="agent.message.sent",
                details=f"Agent sent message in conversation {self.selected_conversation.id}: {self.reply_text[:50]}...",
            )
            session.add(audit_log)

            session.commit()
            session.refresh(new_message)

            # TODO: Send via WhatsApp dispatcher (sendText)
            # This would integrate with the actual WhatsApp API
            # await dispatcher.sendText(self.selected_conversation.whatsapp_number, self.reply_text)

        # Refresh messages
        await self.select_conversation(self.selected_conversation.id)
        self.reply_text = ""
        self.loading = False
        return rx.toast("Message sent successfully", duration=3000)

    @rx.event
    async def release_to_automation(self):
        """Release conversation back to automation"""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user or not self.selected_conversation:
            return

        self.loading = True
        with rx.session() as session:
            conv = session.exec(
                sqlmodel.select(Conversation).where(
                    Conversation.id == self.selected_conversation.id
                )
            ).first()

            if conv:
                conv.status = ConversationStatusEnum.AUTOMATED
                conv.assigned_agent_id = None
                session.add(conv)

                # Audit log
                audit_log = AuditLog(
                    user_id=auth_state.user.id,
                    tenant_id=auth_state.user.tenant_id,
                    action="conversation.released",
                    details=f"Conversation {conv.id} released to automation",
                )
                session.add(audit_log)

                session.commit()

                # TODO: Resume automation engine
                # await engine.resume_automation(conv.id)

        await self.load_conversations()
        self.selected_conversation = None
        self.messages = []
        self.loading = False
        return rx.toast("Conversation released to automation", duration=3000)

    @rx.event
    async def generate_ai_summary(self):
        """Generate AI summary for the selected conversation"""
        auth_state = await self.get_state(AuthState)
        if not auth_state.user or not self.selected_conversation:
            return

        self.loading = True
        with rx.session() as session:
            conv = session.exec(
                sqlmodel.select(Conversation)
                .where(Conversation.id == self.selected_conversation.id)
                .options(selectinload(Conversation.messages))
            ).first()

            if conv and conv.messages:
                # Generate summary from messages with content truncation
                message_texts = [
                    msg.content[:100] for msg in conv.messages[-10:]
                ]  # Last 10 messages, truncate to 100 chars each
                summary = f"Recent conversation with {len(conv.messages)} messages. Last topics discussed: {', '.join(message_texts[:3])}"

                conv.ai_summary = summary
                session.add(conv)
                session.commit()

                self.selected_conversation.ai_summary = summary

        self.loading = False
        return rx.toast("AI Summary generated", duration=3000)

    @rx.event
    def update_reply_text(self, value: str):
        """Update the reply text"""
        self.reply_text = value

    @rx.event
    def clear_error(self):
        """Clear error message"""
        self.error_message = ""
