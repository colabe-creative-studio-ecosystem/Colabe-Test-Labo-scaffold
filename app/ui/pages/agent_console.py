import reflex as rx
from app.ui.components.footer import footer
from app.ui.components.sidebar import sidebar
from app.ui.states.auth_state import AuthState
from app.ui.states.conversation_state import (
    ConversationState,
    ConversationDisplay,
    MessageDisplay,
)
from app.ui.styles import page_style, page_content_style, header_style


def render_conversation_card(conversation: ConversationDisplay) -> rx.Component:
    """Render a conversation card in the list"""
    status_colors = {
        "automated": "bg-blue-500/20 text-blue-400",
        "human_handoff": "bg-yellow-500/20 text-yellow-400",
        "resolved": "bg-green-500/20 text-green-400",
    }

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        conversation.contact_name
                        or conversation.whatsapp_number,
                        class_name="font-semibold text-[#E8F0FF]",
                    ),
                    rx.el.span(
                        conversation.status.replace("_", " ").upper(),
                        class_name=f"px-2 py-1 text-xs rounded {status_colors.get(conversation.status, 'bg-gray-500/20 text-gray-400')}",
                    ),
                    class_name="flex items-center justify-between mb-2",
                ),
                rx.el.p(
                    f"📱 {conversation.whatsapp_number}",
                    class_name="text-sm text-[#A9B3C1] mb-1",
                ),
                rx.cond(
                    conversation.assigned_agent_name,
                    rx.el.p(
                        f"👤 Agent: {conversation.assigned_agent_name}",
                        class_name="text-sm text-[#A9B3C1] mb-1",
                    ),
                    rx.el.p(
                        "👤 Unassigned",
                        class_name="text-sm text-orange-400 mb-1",
                    ),
                ),
                rx.el.p(
                    f"💬 {conversation.message_count} messages",
                    class_name="text-sm text-[#A9B3C1] mb-2",
                ),
                rx.cond(
                    conversation.time_remaining,
                    rx.el.div(
                        rx.el.span(
                            "⏱️ SLA: ",
                            class_name="text-sm text-[#A9B3C1]",
                        ),
                        rx.el.span(
                            conversation.time_remaining,
                            class_name=rx.cond(
                                conversation.time_remaining == "OVERDUE",
                                "text-sm font-bold text-red-500",
                                "text-sm font-semibold text-green-400",
                            ),
                        ),
                        class_name="mb-2",
                    ),
                ),
            ),
            class_name="p-4 bg-[#1A1F36] rounded-lg hover:bg-[#252B42] cursor-pointer transition-colors border border-white/5",
            on_click=lambda: ConversationState.select_conversation(conversation.id),
        ),
        class_name="mb-3",
    )


def render_message(message: MessageDisplay) -> rx.Component:
    """Render a message in the conversation timeline"""
    sender_colors = {
        "user": "bg-blue-500/20 border-blue-500/30",
        "ai": "bg-purple-500/20 border-purple-500/30",
        "agent": "bg-green-500/20 border-green-500/30",
    }

    sender_icons = {
        "user": "👤",
        "ai": "🤖",
        "agent": "👨‍💼",
    }

    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    sender_icons.get(message.sender_type, "💬"),
                    class_name="mr-2",
                ),
                rx.el.span(
                    message.sender_name or message.sender_type.upper(),
                    class_name="font-semibold text-[#E8F0FF]",
                ),
                rx.el.span(
                    message.timestamp.split("T")[1][:5],
                    class_name="ml-3 text-xs text-[#A9B3C1]",
                ),
                class_name="mb-2",
            ),
            rx.el.p(
                message.content,
                class_name="text-[#E8F0FF]",
            ),
            class_name=f"p-4 rounded-lg border {sender_colors.get(message.sender_type, 'bg-gray-500/20 border-gray-500/30')}",
        ),
        class_name="mb-3",
    )


def conversation_list_panel() -> rx.Component:
    """Left panel showing list of conversations"""
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Conversations",
                class_name="text-xl font-bold text-[#E8F0FF] mb-4",
            ),
            rx.el.button(
                "🔄 Refresh",
                on_click=ConversationState.load_conversations,
                class_name="px-4 py-2 bg-[#4169E1] text-white rounded hover:bg-[#3658c7] transition-colors mb-4 w-full",
            ),
            class_name="mb-4",
        ),
        rx.cond(
            ConversationState.loading,
            rx.el.div(
                rx.el.p(
                    "Loading conversations...",
                    class_name="text-[#A9B3C1] text-center",
                ),
                class_name="p-4",
            ),
            rx.cond(
                ConversationState.conversations,
                rx.el.div(
                    rx.foreach(ConversationState.conversations, render_conversation_card),
                    class_name="overflow-y-auto max-h-[calc(100vh-250px)]",
                ),
                rx.el.div(
                    rx.el.p(
                        "No conversations found",
                        class_name="text-[#A9B3C1] text-center p-4",
                    ),
                ),
            ),
        ),
        class_name="w-full md:w-1/3 p-4 bg-[#0F1419] rounded-lg border border-white/10",
    )


def conversation_detail_panel() -> rx.Component:
    """Right panel showing selected conversation details"""
    return rx.el.div(
        rx.cond(
            ConversationState.selected_conversation,
            rx.el.div(
                # Header
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            rx.cond(
                                ConversationState.selected_conversation.contact_name,
                                ConversationState.selected_conversation.contact_name,
                                ConversationState.selected_conversation.whatsapp_number,
                            ),
                            class_name="text-xl font-bold text-[#E8F0FF]",
                        ),
                        rx.el.p(
                            f"📱 {ConversationState.selected_conversation.whatsapp_number}",
                            class_name="text-sm text-[#A9B3C1]",
                        ),
                    ),
                    rx.el.div(
                        rx.cond(
                            ConversationState.selected_conversation.time_remaining,
                            rx.el.div(
                                rx.el.p(
                                    "⏱️ SLA Timer",
                                    class_name="text-xs text-[#A9B3C1]",
                                ),
                                rx.el.p(
                                    ConversationState.selected_conversation.time_remaining,
                                    class_name=rx.cond(
                                        ConversationState.selected_conversation.time_remaining
                                        == "OVERDUE",
                                        "text-lg font-bold text-red-500",
                                        "text-lg font-bold text-green-400",
                                    ),
                                ),
                                class_name="text-center",
                            ),
                        ),
                    ),
                    class_name="flex justify-between items-start mb-4 pb-4 border-b border-white/10",
                ),
                # AI Summary
                rx.cond(
                    ConversationState.selected_conversation.ai_summary,
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "🤖 AI Summary",
                                class_name="text-sm font-semibold text-[#E8F0FF] mb-2",
                            ),
                            rx.el.button(
                                "🔄 Regenerate",
                                on_click=ConversationState.generate_ai_summary,
                                class_name="px-3 py-1 text-xs bg-[#4169E1] text-white rounded hover:bg-[#3658c7] transition-colors",
                            ),
                            class_name="flex justify-between items-center mb-2",
                        ),
                        rx.el.p(
                            ConversationState.selected_conversation.ai_summary,
                            class_name="text-sm text-[#A9B3C1] mb-4 p-3 bg-[#1A1F36] rounded",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "✨ Generate AI Summary",
                            on_click=ConversationState.generate_ai_summary,
                            class_name="px-4 py-2 bg-[#4169E1] text-white rounded hover:bg-[#3658c7] transition-colors mb-4",
                        ),
                        class_name="mb-4",
                    ),
                ),
                # Message Timeline
                rx.el.div(
                    rx.el.h3(
                        "💬 Conversation Timeline",
                        class_name="text-sm font-semibold text-[#E8F0FF] mb-3",
                    ),
                    rx.el.div(
                        rx.cond(
                            ConversationState.messages,
                            rx.foreach(ConversationState.messages, render_message),
                            rx.el.p(
                                "No messages yet",
                                class_name="text-[#A9B3C1] text-center",
                            ),
                        ),
                        class_name="overflow-y-auto max-h-[400px] mb-4",
                    ),
                ),
                # Reply Box
                rx.el.div(
                    rx.el.h3(
                        "✉️ Send Reply",
                        class_name="text-sm font-semibold text-[#E8F0FF] mb-2",
                    ),
                    rx.el.textarea(
                        value=ConversationState.reply_text,
                        on_change=ConversationState.update_reply_text,
                        placeholder="Type your reply here...",
                        class_name="w-full p-3 bg-[#1A1F36] border border-white/10 rounded text-[#E8F0FF] mb-2 min-h-[100px]",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "📤 Send Reply",
                            on_click=ConversationState.send_reply,
                            class_name="px-6 py-2 bg-[#4169E1] text-white rounded hover:bg-[#3658c7] transition-colors mr-2",
                        ),
                        rx.el.button(
                            "🤖 Release to Automation",
                            on_click=ConversationState.release_to_automation,
                            class_name="px-6 py-2 bg-green-600 text-white rounded hover:bg-green-700 transition-colors",
                        ),
                        class_name="flex gap-2",
                    ),
                    class_name="border-t border-white/10 pt-4",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    "Select a conversation to view details",
                    class_name="text-[#A9B3C1] text-center p-8",
                ),
            ),
        ),
        class_name="w-full md:w-2/3 p-4 bg-[#0F1419] rounded-lg border border-white/10",
    )


def agent_console_page() -> rx.Component:
    """Main agent console page"""
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    rx.el.main(
                        rx.el.header(
                            rx.el.div(
                                rx.el.h1(
                                    "Agent Console",
                                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                                ),
                                rx.el.p(
                                    "Manage WhatsApp conversations with human handoff support",
                                    class_name="text-[#A9B3C1]",
                                ),
                            ),
                            class_name=header_style,
                        ),
                        # Error message
                        rx.cond(
                            ConversationState.error_message,
                            rx.el.div(
                                rx.el.p(
                                    ConversationState.error_message,
                                    class_name="text-red-400",
                                ),
                                rx.el.button(
                                    "✕",
                                    on_click=ConversationState.clear_error,
                                    class_name="ml-2 text-red-400 hover:text-red-300",
                                ),
                                class_name="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded flex justify-between items-center",
                            ),
                        ),
                        # Main content
                        rx.el.div(
                            rx.el.div(
                                conversation_list_panel(),
                                conversation_detail_panel(),
                                class_name="flex flex-col md:flex-row gap-4",
                            ),
                            class_name="p-4",
                        ),
                        class_name=page_content_style,
                    ),
                    class_name=page_style,
                ),
            ),
            rx.redirect("/login"),
        ),
    )
