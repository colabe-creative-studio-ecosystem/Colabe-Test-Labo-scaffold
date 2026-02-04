"""
Tests for inbound processor pipeline
"""

import pytest
import json
from datetime import datetime
from unittest.mock import MagicMock, patch
from app.server.inbound_processor import (
    InboundProcessor,
    TransientError,
    PermanentError,
)


class TestInboundProcessor:
    """Test suite for InboundProcessor"""

    def test_normalize_event_success(self):
        """Test successful event normalization"""
        processor = InboundProcessor()
        event_data = {
            "type": "message.received",
            "workspace_id": "123",
            "conversation_id": "conv_456",
            "channel": "slack",
            "payload": {"text": "Hello"},
        }

        result = processor._normalize_event(event_data)

        assert result["event_type"] == "message.received"
        assert result["workspace_id"] == 123
        assert result["conversation_id"] == "conv_456"
        assert result["channel"] == "slack"
        assert result["payload"] == {"text": "Hello"}

    def test_normalize_event_missing_type(self):
        """Test normalization fails with missing type"""
        processor = InboundProcessor()
        event_data = {
            "workspace_id": "123",
        }

        with pytest.raises(PermanentError, match="Missing event type"):
            processor._normalize_event(event_data)

    def test_normalize_event_missing_workspace(self):
        """Test normalization fails with missing workspace_id"""
        processor = InboundProcessor()
        event_data = {
            "type": "message.received",
        }

        with pytest.raises(PermanentError, match="Missing workspace_id"):
            processor._normalize_event(event_data)

    def test_map_event_to_trigger(self):
        """Test event type to trigger type mapping"""
        processor = InboundProcessor()

        from app.core.models import AutomationTriggerEnum

        # Test known mappings
        assert (
            processor._map_event_to_trigger("message.received")
            == AutomationTriggerEnum.TRIGGER_MESSAGE
        )
        assert (
            processor._map_event_to_trigger("message.sent")
            == AutomationTriggerEnum.TRIGGER_MESSAGE
        )
        assert (
            processor._map_event_to_trigger("webhook")
            == AutomationTriggerEnum.TRIGGER_WEBHOOK
        )
        assert (
            processor._map_event_to_trigger("scheduled")
            == AutomationTriggerEnum.TRIGGER_SCHEDULE
        )

        # Test unknown type defaults to TRIGGER_EVENT
        assert (
            processor._map_event_to_trigger("unknown_type")
            == AutomationTriggerEnum.TRIGGER_EVENT
        )

    @pytest.mark.asyncio
    async def test_run_executor_simulate_mode(self):
        """Test executor in simulate mode"""
        processor = InboundProcessor()

        # Mock automation with simple flow
        automation = MagicMock()
        automation.flow_definition = json.dumps(
            {
                "steps": [
                    {"name": "step1", "type": "action", "action": {"type": "send_message"}},
                    {"name": "step2", "type": "condition", "action": {"type": "check_status"}},
                ]
            }
        )

        normalized_event = {"event_type": "message.received"}
        conversation = None
        execution_mode = "simulate"

        result = await processor._run_executor(
            automation, normalized_event, conversation, execution_mode
        )

        assert result["status"] == "success"
        assert result["mode"] == "simulate"
        assert len(result["execution_trace"]) == 2
        assert result["execution_trace"][0]["simulated"] is True
        assert result["actions"] == []  # No actions in simulate mode

    @pytest.mark.asyncio
    async def test_run_executor_live_mode(self):
        """Test executor in live mode"""
        processor = InboundProcessor()

        # Mock automation with simple flow
        automation = MagicMock()
        automation.flow_definition = json.dumps(
            {
                "steps": [
                    {"name": "step1", "type": "action", "action": {"type": "send_message"}},
                ]
            }
        )

        normalized_event = {"event_type": "message.received"}
        conversation = None
        execution_mode = "live"

        result = await processor._run_executor(
            automation, normalized_event, conversation, execution_mode
        )

        assert result["status"] == "success"
        assert result["mode"] == "live"
        assert len(result["execution_trace"]) == 1
        assert result["execution_trace"][0]["executed"] is True
        assert len(result["actions"]) == 1
        assert result["actions"][0]["type"] == "send_message"

    @pytest.mark.asyncio
    async def test_run_executor_invalid_json(self):
        """Test executor with invalid flow definition"""
        processor = InboundProcessor()

        automation = MagicMock()
        automation.flow_definition = "invalid json"

        with pytest.raises(PermanentError, match="Invalid flow definition JSON"):
            await processor._run_executor(automation, {}, None, "live")

    @pytest.mark.asyncio
    async def test_dispatch_actions_simulate_mode(self):
        """Test action dispatcher in simulate mode"""
        processor = InboundProcessor()

        automation = MagicMock()
        execution_result = {
            "mode": "simulate",
            "actions": [
                {"type": "send_message", "data": {"text": "Hello"}},
                {"type": "handoff", "data": {"agent": "support"}},
            ],
        }
        conversation = None

        result = await processor._dispatch_actions(
            automation, execution_result, conversation
        )

        assert len(result["dispatched_actions"]) == 2
        assert result["dispatched_actions"][0]["simulated"] is True
        assert result["dispatched_actions"][1]["simulated"] is True

    @pytest.mark.asyncio
    async def test_dispatch_actions_live_mode(self):
        """Test action dispatcher in live mode"""
        processor = InboundProcessor()

        automation = MagicMock()
        execution_result = {
            "mode": "live",
            "actions": [
                {"type": "send_message", "data": {"text": "Hello"}},
            ],
        }
        conversation = MagicMock()
        conversation.id = 123

        result = await processor._dispatch_actions(
            automation, execution_result, conversation
        )

        assert len(result["dispatched_actions"]) == 1
        assert result["dispatched_actions"][0]["executed"] is True
        assert result["dispatched_actions"][0]["result"]["status"] == "dispatched"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
