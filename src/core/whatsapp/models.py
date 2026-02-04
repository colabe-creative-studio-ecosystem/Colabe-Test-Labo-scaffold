"""Data models for WhatsApp dispatcher system."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ExecutionMode(str, Enum):
    """Execution mode for WhatsApp operations."""
    SIMULATE = "simulate"
    SANDBOX = "sandbox"
    LIVE = "live"


class ActionType(str, Enum):
    """Types of actions that can be performed."""
    SEND_MESSAGE = "send_message"
    SEND_BUTTONS = "send_buttons"
    ASK_QUESTION = "ask_question"
    HANDOFF = "handoff"
    DELAY = "delay"


@dataclass
class ActionPlan:
    """Represents a planned action to be executed."""
    id: str
    action_type: ActionType
    payload: Dict[str, Any]
    order: int = 0
    
    def __post_init__(self):
        """Ensure action_type is an ActionType enum."""
        if isinstance(self.action_type, str):
            self.action_type = ActionType(self.action_type)


@dataclass
class ExecutionRun:
    """Represents a run execution context."""
    id: str
    mode: ExecutionMode
    user_id: str
    conversation_id: str
    trace_json: Dict[str, Any] = field(default_factory=dict)
    awaiting_reply: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Ensure mode is an ExecutionMode enum."""
        if isinstance(self.mode, str):
            self.mode = ExecutionMode(self.mode)


@dataclass
class DispatchReceipt:
    """Receipt for a dispatched action."""
    action_id: str
    success: bool
    timestamp: datetime
    provider_response: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert receipt to dictionary for traceJson storage."""
        return {
            "action_id": self.action_id,
            "success": self.success,
            "timestamp": self.timestamp.isoformat(),
            "provider_response": self.provider_response,
            "error": self.error
        }
