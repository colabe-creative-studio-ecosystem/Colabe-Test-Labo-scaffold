"""WhatsApp provider interfaces and implementations."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class WhatsAppProvider(ABC):
    """Abstract base class for WhatsApp providers."""
    
    @abstractmethod
    async def send_text(
        self,
        user_id: str,
        message: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Send a text message to a user.
        
        Args:
            user_id: The recipient user ID
            message: The text message to send
            conversation_id: The conversation context
            
        Returns:
            Provider response with message ID and status
        """
        pass
    
    @abstractmethod
    async def send_buttons(
        self,
        user_id: str,
        message: str,
        buttons: List[Dict[str, str]],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Send a message with interactive buttons.
        
        Args:
            user_id: The recipient user ID
            message: The text message to send
            buttons: List of button configurations
            conversation_id: The conversation context
            
        Returns:
            Provider response with message ID and status
        """
        pass
    
    @abstractmethod
    async def notify_handoff(
        self,
        user_id: str,
        agent_message: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Notify an agent console about a handoff.
        
        Args:
            user_id: The user being handed off
            agent_message: Message for the agent
            conversation_id: The conversation context
            
        Returns:
            Provider response with handoff status
        """
        pass


class SimulationProvider(WhatsAppProvider):
    """Simulation provider for testing without actual message sending."""
    
    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []
        self.message_counter = 0
    
    async def send_text(
        self,
        user_id: str,
        message: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Simulate sending a text message."""
        self.message_counter += 1
        msg_id = f"sim_msg_{self.message_counter}"
        
        record = {
            "type": "text",
            "message_id": msg_id,
            "user_id": user_id,
            "message": message,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
        self.sent_messages.append(record)
        
        logger.info(f"[SIMULATION] Sent text to {user_id}: {message[:50]}...")
        
        return {
            "message_id": msg_id,
            "status": "simulated",
            "timestamp": record["timestamp"]
        }
    
    async def send_buttons(
        self,
        user_id: str,
        message: str,
        buttons: List[Dict[str, str]],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Simulate sending a message with buttons."""
        self.message_counter += 1
        msg_id = f"sim_msg_{self.message_counter}"
        
        record = {
            "type": "buttons",
            "message_id": msg_id,
            "user_id": user_id,
            "message": message,
            "buttons": buttons,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
        self.sent_messages.append(record)
        
        logger.info(
            f"[SIMULATION] Sent buttons to {user_id}: {len(buttons)} buttons"
        )
        
        return {
            "message_id": msg_id,
            "status": "simulated",
            "button_count": len(buttons),
            "timestamp": record["timestamp"]
        }
    
    async def notify_handoff(
        self,
        user_id: str,
        agent_message: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Simulate notifying an agent console."""
        self.message_counter += 1
        handoff_id = f"sim_handoff_{self.message_counter}"
        
        record = {
            "type": "handoff",
            "handoff_id": handoff_id,
            "user_id": user_id,
            "agent_message": agent_message,
            "conversation_id": conversation_id,
            "timestamp": datetime.now().isoformat()
        }
        self.sent_messages.append(record)
        
        logger.info(f"[SIMULATION] Handoff for {user_id}")
        
        return {
            "handoff_id": handoff_id,
            "status": "simulated",
            "timestamp": record["timestamp"]
        }
    
    def get_sent_messages(self) -> List[Dict[str, Any]]:
        """Get all messages sent during simulation."""
        return self.sent_messages.copy()


class CloudProvider(WhatsAppProvider):
    """Cloud provider for sandbox and live environments."""
    
    def __init__(self, api_key: str, endpoint: str, mode: str = "sandbox"):
        self.api_key = api_key
        self.endpoint = endpoint
        self.mode = mode  # "sandbox" or "live"
    
    async def send_text(
        self,
        user_id: str,
        message: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Send a text message via cloud API."""
        # In a real implementation, this would make an HTTP request
        # to the WhatsApp Business API
        logger.info(
            f"[{self.mode.upper()}] Sending text to {user_id}: {message[:50]}..."
        )
        
        # Placeholder for actual API call
        return {
            "message_id": f"{self.mode}_msg_{datetime.now().timestamp()}",
            "status": "sent",
            "mode": self.mode,
            "timestamp": datetime.now().isoformat()
        }
    
    async def send_buttons(
        self,
        user_id: str,
        message: str,
        buttons: List[Dict[str, str]],
        conversation_id: str
    ) -> Dict[str, Any]:
        """Send a message with buttons via cloud API."""
        logger.info(
            f"[{self.mode.upper()}] Sending buttons to {user_id}: "
            f"{len(buttons)} buttons"
        )
        
        # Placeholder for actual API call
        return {
            "message_id": f"{self.mode}_msg_{datetime.now().timestamp()}",
            "status": "sent",
            "mode": self.mode,
            "button_count": len(buttons),
            "timestamp": datetime.now().isoformat()
        }
    
    async def notify_handoff(
        self,
        user_id: str,
        agent_message: str,
        conversation_id: str
    ) -> Dict[str, Any]:
        """Notify agent console via cloud API."""
        logger.info(f"[{self.mode.upper()}] Handoff notification for {user_id}")
        
        # Placeholder for actual API call
        return {
            "handoff_id": f"{self.mode}_handoff_{datetime.now().timestamp()}",
            "status": "notified",
            "mode": self.mode,
            "timestamp": datetime.now().isoformat()
        }
