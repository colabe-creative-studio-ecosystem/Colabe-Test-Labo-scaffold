"""Tests for WhatsApp Outbound Dispatcher."""
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from src.core.whatsapp.dispatcher import Dispatcher, DispatcherError
from src.core.whatsapp.models import (
    ActionPlan,
    ActionType,
    ExecutionMode,
    ExecutionRun,
)
from src.core.whatsapp.providers import SimulationProvider


class MockFailingProvider:
    """Mock provider that fails on specific messages."""
    
    def __init__(self, fail_on_message=None):
        self.fail_on_message = fail_on_message
        self.calls = []
    
    async def send_text(self, user_id, message, conversation_id):
        self.calls.append(("send_text", message))
        if self.fail_on_message and self.fail_on_message in message:
            raise Exception(f"Simulated failure on message: {message}")
        return {"message_id": "test_id", "status": "sent"}
    
    async def send_buttons(self, user_id, message, buttons, conversation_id):
        self.calls.append(("send_buttons", message))
        return {"message_id": "test_id", "status": "sent"}
    
    async def notify_handoff(self, user_id, agent_message, conversation_id):
        self.calls.append(("notify_handoff", agent_message))
        return {"handoff_id": "test_id", "status": "notified"}


class TestDispatcher:
    """Test suite for Dispatcher class."""
    
    @pytest.fixture
    def dispatcher(self):
        """Create a dispatcher instance for testing."""
        return Dispatcher(
            cloud_api_key="test_api_key",
            cloud_endpoint="https://test.example.com"
        )
    
    @pytest.fixture
    def simulation_run(self):
        """Create a simulation execution run."""
        return ExecutionRun(
            id="run_001",
            mode=ExecutionMode.SIMULATE,
            user_id="user_123",
            conversation_id="conv_456"
        )
    
    @pytest.fixture
    def sandbox_run(self):
        """Create a sandbox execution run."""
        return ExecutionRun(
            id="run_002",
            mode=ExecutionMode.SANDBOX,
            user_id="user_123",
            conversation_id="conv_456"
        )
    
    def test_provider_selection_simulate(self, dispatcher, simulation_run):
        """Test that simulate mode selects SimulationProvider."""
        provider = dispatcher._get_provider(simulation_run)
        assert isinstance(provider, SimulationProvider)
    
    def test_provider_selection_sandbox(self, dispatcher, sandbox_run):
        """Test that sandbox mode selects CloudProvider."""
        provider = dispatcher._get_provider(sandbox_run)
        assert provider is not None
        assert hasattr(provider, 'mode')
        assert provider.mode == 'sandbox'
    
    def test_provider_selection_without_credentials(self, sandbox_run):
        """Test that cloud modes fail without credentials."""
        dispatcher_no_creds = Dispatcher()
        with pytest.raises(DispatcherError, match="Cloud API credentials required"):
            dispatcher_no_creds._get_provider(sandbox_run)
    
    @pytest.mark.asyncio
    async def test_dispatch_send_message(self, dispatcher, simulation_run):
        """Test dispatching a send_message action."""
        action = ActionPlan(
            id="action_001",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "Hello, World!"},
            order=1
        )
        
        receipts = await dispatcher.dispatch(simulation_run, [action])
        
        assert len(receipts) == 1
        assert receipts[0].success
        assert receipts[0].action_id == "action_001"
        assert "message_id" in receipts[0].provider_response
    
    @pytest.mark.asyncio
    async def test_dispatch_send_buttons(self, dispatcher, simulation_run):
        """Test dispatching a send_buttons action."""
        action = ActionPlan(
            id="action_002",
            action_type=ActionType.SEND_BUTTONS,
            payload={
                "message": "Choose an option:",
                "buttons": [
                    {"id": "btn1", "text": "Option 1"},
                    {"id": "btn2", "text": "Option 2"}
                ]
            },
            order=1
        )
        
        receipts = await dispatcher.dispatch(simulation_run, [action])
        
        assert len(receipts) == 1
        assert receipts[0].success
        assert receipts[0].provider_response["button_count"] == 2
    
    @pytest.mark.asyncio
    async def test_dispatch_ask_question(self, dispatcher, simulation_run):
        """Test dispatching an ask_question action."""
        action = ActionPlan(
            id="action_003",
            action_type=ActionType.ASK_QUESTION,
            payload={"question": "What is your name?"},
            order=1
        )
        
        receipts = await dispatcher.dispatch(simulation_run, [action])
        
        assert len(receipts) == 1
        assert receipts[0].success
        assert simulation_run.awaiting_reply is True
        assert receipts[0].provider_response["awaiting_reply"] is True
    
    @pytest.mark.asyncio
    async def test_dispatch_handoff(self, dispatcher, simulation_run):
        """Test dispatching a handoff action."""
        action = ActionPlan(
            id="action_004",
            action_type=ActionType.HANDOFF,
            payload={
                "agent_message": "User needs assistance",
                "user_message": "Connecting you to an agent..."
            },
            order=1
        )
        
        receipts = await dispatcher.dispatch(simulation_run, [action])
        
        assert len(receipts) == 1
        assert receipts[0].success
        assert "handoff" in receipts[0].provider_response
        assert "user_message" in receipts[0].provider_response
    
    @pytest.mark.asyncio
    async def test_dispatch_delay(self, dispatcher, simulation_run):
        """Test dispatching a delay action."""
        action = ActionPlan(
            id="action_005",
            action_type=ActionType.DELAY,
            payload={"delay_seconds": 5},
            order=1
        )
        
        receipts = await dispatcher.dispatch(simulation_run, [action])
        
        assert len(receipts) == 1
        assert receipts[0].success
        assert receipts[0].provider_response["scheduled"] is True
    
    @pytest.mark.asyncio
    async def test_dispatch_multiple_actions_ordered(self, dispatcher, simulation_run):
        """Test dispatching multiple actions in order."""
        actions = [
            ActionPlan(
                id="action_001",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "First message"},
                order=1
            ),
            ActionPlan(
                id="action_002",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "Second message"},
                order=2
            ),
            ActionPlan(
                id="action_003",
                action_type=ActionType.ASK_QUESTION,
                payload={"question": "What do you think?"},
                order=3
            )
        ]
        
        receipts = await dispatcher.dispatch(simulation_run, actions)
        
        assert len(receipts) == 3
        assert all(r.success for r in receipts)
        assert receipts[0].action_id == "action_001"
        assert receipts[1].action_id == "action_002"
        assert receipts[2].action_id == "action_003"
    
    @pytest.mark.asyncio
    async def test_dispatch_respects_action_order(self, dispatcher, simulation_run):
        """Test that actions are dispatched in order regardless of input order."""
        actions = [
            ActionPlan(
                id="action_003",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "Third"},
                order=3
            ),
            ActionPlan(
                id="action_001",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "First"},
                order=1
            ),
            ActionPlan(
                id="action_002",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "Second"},
                order=2
            )
        ]
        
        receipts = await dispatcher.dispatch(simulation_run, actions)
        
        assert len(receipts) == 3
        assert receipts[0].action_id == "action_001"
        assert receipts[1].action_id == "action_002"
        assert receipts[2].action_id == "action_003"
    
    @pytest.mark.asyncio
    async def test_trace_json_recording(self, dispatcher, simulation_run):
        """Test that receipts are recorded in traceJson."""
        action = ActionPlan(
            id="action_001",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "Test message"},
            order=1
        )
        
        await dispatcher.dispatch(simulation_run, [action])
        
        assert "dispatched_actions" in simulation_run.trace_json
        assert len(simulation_run.trace_json["dispatched_actions"]) == 1
        assert simulation_run.trace_json["dispatched_actions"][0]["action_id"] == "action_001"
        assert simulation_run.trace_json["dispatched_actions"][0]["success"] is True
    
    @pytest.mark.asyncio
    async def test_empty_action_list(self, dispatcher, simulation_run):
        """Test dispatching an empty action list."""
        receipts = await dispatcher.dispatch(simulation_run, [])
        assert len(receipts) == 0
    
    @pytest.mark.asyncio
    async def test_unknown_action_type_handling(self, dispatcher, simulation_run):
        """Test handling of unknown action types via missing payload."""
        # Create an action with missing required payload fields
        # This will cause the action handler to fail gracefully
        action = ActionPlan(
            id="action_999",
            action_type=ActionType.SEND_MESSAGE,
            payload={},  # Empty payload - missing "message" field
            order=1
        )
        
        # This should succeed but with empty message
        receipts = await dispatcher.dispatch(simulation_run, [action])
        
        assert len(receipts) == 1
        assert receipts[0].success  # It will succeed with empty string


class TestSafeFailureBehavior:
    """Test suite for safe failure behavior (no partial spam)."""
    
    @pytest.fixture
    def dispatcher(self):
        """Create a dispatcher instance for testing."""
        return Dispatcher()
    
    @pytest.fixture
    def simulation_run(self):
        """Create a simulation execution run."""
        return ExecutionRun(
            id="run_001",
            mode=ExecutionMode.SIMULATE,
            user_id="user_123",
            conversation_id="conv_456"
        )
    
    @pytest.mark.asyncio
    async def test_stops_on_first_failure(self, dispatcher, simulation_run):
        """Test that dispatch stops on first failure to prevent partial spam."""
        actions = [
            ActionPlan(
                id="action_001",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "First message"},
                order=1
            ),
            ActionPlan(
                id="action_002",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "FAIL_HERE"},  # Will cause mock to fail
                order=2
            ),
            ActionPlan(
                id="action_003",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "Third message - should not be sent"},
                order=3
            )
        ]
        
        # Create mock provider that fails on "FAIL_HERE"
        mock_provider = MockFailingProvider(fail_on_message="FAIL_HERE")
        
        # Patch the provider
        with patch.object(dispatcher, '_get_provider', return_value=mock_provider):
            receipts = await dispatcher.dispatch(simulation_run, actions)
        
        # Only first two actions should be attempted
        assert len(receipts) == 2
        assert receipts[0].success is True
        assert receipts[1].success is False
        # Third action should not be attempted
        assert len(mock_provider.calls) == 2
    
    @pytest.mark.asyncio
    async def test_trace_json_records_partial_execution(
        self, dispatcher, simulation_run
    ):
        """Test that traceJson records partial execution on failure."""
        actions = [
            ActionPlan(
                id="action_001",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "First message"},
                order=1
            ),
            ActionPlan(
                id="action_002",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "FAIL_HERE"},
                order=2
            ),
            ActionPlan(
                id="action_003",
                action_type=ActionType.SEND_MESSAGE,
                payload={"message": "Third message"},
                order=3
            )
        ]
        
        # Create mock provider that fails on "FAIL_HERE"
        mock_provider = MockFailingProvider(fail_on_message="FAIL_HERE")
        
        # Patch the provider
        with patch.object(dispatcher, '_get_provider', return_value=mock_provider):
            receipts = await dispatcher.dispatch(simulation_run, actions)
        
        # Check traceJson
        assert "dispatched_actions" in simulation_run.trace_json
        dispatched = simulation_run.trace_json["dispatched_actions"]
        
        # Should have records for first two actions only
        assert len(dispatched) == 2
        assert dispatched[0]["success"] is True
        assert dispatched[1]["success"] is False


class TestSimulationProvider:
    """Test suite for SimulationProvider."""
    
    @pytest.fixture
    def provider(self):
        """Create a simulation provider instance."""
        return SimulationProvider()
    
    @pytest.mark.asyncio
    async def test_send_text_records_message(self, provider):
        """Test that send_text records messages."""
        response = await provider.send_text(
            user_id="user_123",
            message="Test message",
            conversation_id="conv_456"
        )
        
        assert response["status"] == "simulated"
        assert "message_id" in response
        
        messages = provider.get_sent_messages()
        assert len(messages) == 1
        assert messages[0]["type"] == "text"
        assert messages[0]["message"] == "Test message"
    
    @pytest.mark.asyncio
    async def test_send_buttons_records_buttons(self, provider):
        """Test that send_buttons records button messages."""
        buttons = [
            {"id": "btn1", "text": "Yes"},
            {"id": "btn2", "text": "No"}
        ]
        
        response = await provider.send_buttons(
            user_id="user_123",
            message="Do you agree?",
            buttons=buttons,
            conversation_id="conv_456"
        )
        
        assert response["status"] == "simulated"
        assert response["button_count"] == 2
        
        messages = provider.get_sent_messages()
        assert len(messages) == 1
        assert messages[0]["type"] == "buttons"
        assert len(messages[0]["buttons"]) == 2
    
    @pytest.mark.asyncio
    async def test_notify_handoff_records_handoff(self, provider):
        """Test that notify_handoff records handoff events."""
        response = await provider.notify_handoff(
            user_id="user_123",
            agent_message="User needs help",
            conversation_id="conv_456"
        )
        
        assert response["status"] == "simulated"
        assert "handoff_id" in response
        
        messages = provider.get_sent_messages()
        assert len(messages) == 1
        assert messages[0]["type"] == "handoff"
        assert messages[0]["agent_message"] == "User needs help"
    
    @pytest.mark.asyncio
    async def test_multiple_messages_increment_counter(self, provider):
        """Test that message counter increments for multiple messages."""
        await provider.send_text("user_1", "Message 1", "conv_1")
        await provider.send_text("user_2", "Message 2", "conv_2")
        await provider.send_buttons("user_3", "Message 3", [], "conv_3")
        
        messages = provider.get_sent_messages()
        assert len(messages) == 3
        assert provider.message_counter == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
