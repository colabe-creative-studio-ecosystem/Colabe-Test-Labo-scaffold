#!/usr/bin/env python3
"""
Example usage of the WhatsApp Outbound Dispatcher.

This script demonstrates how to use the dispatcher to send messages,
ask questions, and handle conversations.
"""
import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.whatsapp import (
    Dispatcher,
    ExecutionRun,
    ExecutionMode,
    ActionPlan,
    ActionType,
)


async def example_basic_conversation():
    """Example: Basic conversation flow with multiple messages."""
    print("=" * 60)
    print("Example 1: Basic Conversation Flow")
    print("=" * 60)
    
    # Create dispatcher in simulation mode (no real messages sent)
    dispatcher = Dispatcher(max_delay_for_testing=0.1)
    
    # Create execution run
    execution_run = ExecutionRun(
        id="run_001",
        mode=ExecutionMode.SIMULATE,
        user_id="user_123",
        conversation_id="conv_456"
    )
    
    # Define action plans
    action_plans = [
        ActionPlan(
            id="action_001",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "👋 Welcome to our service!"},
            order=1
        ),
        ActionPlan(
            id="action_002",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "I'm here to help you today."},
            order=2
        ),
        ActionPlan(
            id="action_003",
            action_type=ActionType.ASK_QUESTION,
            payload={"question": "What's your name?"},
            order=3
        )
    ]
    
    # Dispatch actions
    receipts = await dispatcher.dispatch(execution_run, action_plans)
    
    # Display results
    print(f"\nDispatched {len(receipts)} actions:")
    for receipt in receipts:
        status = "✓" if receipt.success else "✗"
        print(f"  {status} Action {receipt.action_id}: {receipt.provider_response.get('status', 'N/A')}")
    
    print(f"\nAwaiting reply: {execution_run.awaiting_reply}")
    print(f"\nTrace JSON contains {len(execution_run.trace_json.get('dispatched_actions', []))} records")


async def example_interactive_buttons():
    """Example: Sending a message with interactive buttons."""
    print("\n" + "=" * 60)
    print("Example 2: Interactive Buttons")
    print("=" * 60)
    
    dispatcher = Dispatcher(max_delay_for_testing=0.1)
    
    execution_run = ExecutionRun(
        id="run_002",
        mode=ExecutionMode.SIMULATE,
        user_id="user_456",
        conversation_id="conv_789"
    )
    
    action_plans = [
        ActionPlan(
            id="action_001",
            action_type=ActionType.SEND_BUTTONS,
            payload={
                "message": "How can I help you today?",
                "buttons": [
                    {"id": "btn1", "text": "📦 Track Order"},
                    {"id": "btn2", "text": "💬 Talk to Agent"},
                    {"id": "btn3", "text": "❓ FAQ"}
                ]
            },
            order=1
        )
    ]
    
    receipts = await dispatcher.dispatch(execution_run, action_plans)
    
    for receipt in receipts:
        print(f"\n✓ Sent message with {receipt.provider_response.get('button_count', 0)} buttons")
        print(f"  Message ID: {receipt.provider_response.get('message_id')}")


async def example_handoff_to_agent():
    """Example: Handing off conversation to a human agent."""
    print("\n" + "=" * 60)
    print("Example 3: Handoff to Agent")
    print("=" * 60)
    
    dispatcher = Dispatcher(max_delay_for_testing=0.1)
    
    execution_run = ExecutionRun(
        id="run_003",
        mode=ExecutionMode.SIMULATE,
        user_id="user_789",
        conversation_id="conv_101"
    )
    
    action_plans = [
        ActionPlan(
            id="action_001",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "I understand you need specialized help."},
            order=1
        ),
        ActionPlan(
            id="action_002",
            action_type=ActionType.HANDOFF,
            payload={
                "agent_message": "Customer needs help with billing issue",
                "user_message": "Connecting you with a support specialist..."
            },
            order=2
        )
    ]
    
    receipts = await dispatcher.dispatch(execution_run, action_plans)
    
    for i, receipt in enumerate(receipts, 1):
        if receipt.success:
            print(f"\n✓ Step {i} completed successfully")


async def example_safe_failure():
    """Example: Demonstrating safe failure behavior."""
    print("\n" + "=" * 60)
    print("Example 4: Safe Failure Behavior")
    print("=" * 60)
    
    # Simulate a provider that will fail
    from unittest.mock import AsyncMock, patch
    from src.core.whatsapp.providers import SimulationProvider
    
    class FailingProvider(SimulationProvider):
        async def send_text(self, user_id, message, conversation_id):
            if "FAIL" in message:
                raise Exception("Simulated provider failure")
            return await super().send_text(user_id, message, conversation_id)
    
    dispatcher = Dispatcher(max_delay_for_testing=0.1)
    
    execution_run = ExecutionRun(
        id="run_004",
        mode=ExecutionMode.SIMULATE,
        user_id="user_999",
        conversation_id="conv_999"
    )
    
    action_plans = [
        ActionPlan(
            id="action_001",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "First message - will succeed"},
            order=1
        ),
        ActionPlan(
            id="action_002",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "FAIL - this will fail"},
            order=2
        ),
        ActionPlan(
            id="action_003",
            action_type=ActionType.SEND_MESSAGE,
            payload={"message": "Third message - will NOT be sent"},
            order=3
        )
    ]
    
    # Patch provider to use our failing provider
    with patch.object(dispatcher, '_get_provider', return_value=FailingProvider()):
        receipts = await dispatcher.dispatch(execution_run, action_plans)
    
    print(f"\nTotal actions planned: 3")
    print(f"Actions attempted: {len(receipts)}")
    print(f"\nResults:")
    for receipt in receipts:
        status = "✓ Success" if receipt.success else "✗ Failed"
        print(f"  {status}: Action {receipt.action_id}")
        if not receipt.success:
            print(f"    Error: {receipt.error}")
    
    print(f"\n⚠️  Notice: Action 3 was NOT attempted (preventing partial spam)")


async def main():
    """Run all examples."""
    print("\n")
    print("=" * 60)
    print("WhatsApp Outbound Dispatcher - Examples")
    print("=" * 60)
    
    await example_basic_conversation()
    await example_interactive_buttons()
    await example_handoff_to_agent()
    await example_safe_failure()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)
    print("\nNote: All examples ran in SIMULATION mode.")
    print("No actual WhatsApp messages were sent.\n")


if __name__ == "__main__":
    asyncio.run(main())
