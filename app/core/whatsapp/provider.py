"""
WhatsApp Provider Interfaces

This module defines the core abstractions for WhatsApp messaging:
- WhatsAppProvider: Interface for sending messages and managing WhatsApp interactions
- WebhookVerifier: Interface for verifying webhook signatures
- WhatsAppEventParser: Interface for parsing WhatsApp webhooks into engine events
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """Types of events that can be parsed from WhatsApp webhooks."""
    MESSAGE_RECEIVED = "message_received"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_READ = "message_read"
    MESSAGE_FAILED = "message_failed"
    BUTTON_CLICKED = "button_clicked"
    LIST_SELECTED = "list_selected"


@dataclass
class MessageReceipt:
    """Receipt returned after sending a message."""
    message_id: str
    timestamp: datetime
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class MessageButton:
    """Button definition for interactive messages."""
    id: str
    title: str
    type: str = "reply"  # or "url", "call"
    payload: Optional[str] = None


@dataclass
class ListItem:
    """List item definition for list messages."""
    id: str
    title: str
    description: Optional[str] = None
    section: Optional[str] = None


@dataclass
class EngineEvent:
    """Event parsed from WhatsApp webhook to be consumed by the engine."""
    event_type: EventType
    timestamp: datetime
    from_number: str
    message_id: Optional[str] = None
    text: Optional[str] = None
    button_id: Optional[str] = None
    list_item_id: Optional[str] = None
    media_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class WhatsAppProvider(ABC):
    """
    Abstract base class for WhatsApp providers.
    
    The engine emits ActionPlans; the connector executes them on WhatsApp.
    Implementations can use real API calls (CloudProvider) or simulation (SimulationProvider).
    """

    @abstractmethod
    def send_text(
        self,
        to: str,
        text: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send a text message.
        
        Args:
            to: Recipient phone number (E.164 format recommended)
            text: Message text content
            meta: Optional metadata for tracking/context
            
        Returns:
            MessageReceipt with send status and message ID
        """
        pass

    @abstractmethod
    def send_buttons(
        self,
        to: str,
        text: str,
        buttons: List[MessageButton],
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send an interactive message with buttons.
        
        Args:
            to: Recipient phone number
            text: Message body text
            buttons: List of buttons to display (max 3 for WhatsApp)
            meta: Optional metadata
            
        Returns:
            MessageReceipt with send status
        """
        pass

    @abstractmethod
    def send_list(
        self,
        to: str,
        header: str,
        items: List[ListItem],
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send an interactive list message.
        
        Args:
            to: Recipient phone number
            header: List header text
            items: List of selectable items (max 10 items)
            meta: Optional metadata
            
        Returns:
            MessageReceipt with send status
        """
        pass

    @abstractmethod
    def send_media(
        self,
        to: str,
        media_url_or_id: str,
        caption: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send a media message (image, video, document, etc.).
        
        Args:
            to: Recipient phone number
            media_url_or_id: URL or WhatsApp media ID
            caption: Optional caption text
            meta: Optional metadata
            
        Returns:
            MessageReceipt with send status
        """
        pass

    @abstractmethod
    def mark_read(self, message_id: str) -> None:
        """
        Mark a message as read.
        
        Args:
            message_id: WhatsApp message ID to mark as read
        """
        pass


class WebhookVerifier(ABC):
    """
    Abstract base class for webhook signature verification.
    
    Ensures incoming webhooks are authentic and from WhatsApp.
    """

    @abstractmethod
    def verify(self, signature: str, raw_body: bytes) -> bool:
        """
        Verify webhook signature.
        
        Args:
            signature: Signature from X-Hub-Signature-256 header
            raw_body: Raw request body bytes
            
        Returns:
            True if signature is valid, False otherwise
        """
        pass


class WhatsAppEventParser(ABC):
    """
    Abstract base class for parsing WhatsApp webhooks.
    
    Converts raw webhook payloads into structured EngineEvents.
    """

    @abstractmethod
    def parse(self, raw_webhook: Dict[str, Any]) -> List[EngineEvent]:
        """
        Parse WhatsApp webhook payload into engine events.
        
        Args:
            raw_webhook: Raw webhook JSON payload
            
        Returns:
            List of EngineEvents (can be empty if no relevant events)
        """
        pass
