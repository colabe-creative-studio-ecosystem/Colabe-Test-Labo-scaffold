# WhatsApp Outbound Dispatcher

The WhatsApp Outbound Dispatcher converts validated ActionPlans into WhatsAppProvider calls with safe failure behavior.

## Overview

The dispatcher provides a robust mechanism for executing WhatsApp actions with the following key features:

- **Provider Selection**: Automatically selects the appropriate provider based on execution mode
- **Action Conversion**: Converts high-level action plans to provider-specific calls
- **Receipt Recording**: Records all dispatch receipts in traceJson for auditing
- **Safe Failure Behavior**: Stops on first failure to prevent partial spam

## Architecture

### Components

1. **Dispatcher**: Main orchestration class that converts ActionPlans to provider calls
2. **Providers**: Abstract interfaces and concrete implementations for different environments
   - `SimulationProvider`: For testing without actual message sending
   - `CloudProvider`: For sandbox and live environments
3. **Models**: Data structures for actions, runs, and receipts

## Usage

### Basic Example

```python
from src.core.whatsapp import (
    Dispatcher,
    ExecutionRun,
    ExecutionMode,
    ActionPlan,
    ActionType,
)

# Create dispatcher with cloud credentials
dispatcher = Dispatcher(
    cloud_api_key="your_api_key",
    cloud_endpoint="https://api.example.com"
)

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
        payload={"message": "Hello, how can I help you?"},
        order=1
    ),
    ActionPlan(
        id="action_002",
        action_type=ActionType.ASK_QUESTION,
        payload={"question": "What is your name?"},
        order=2
    )
]

# Dispatch actions
receipts = await dispatcher.dispatch(execution_run, action_plans)

# Check results
for receipt in receipts:
    if receipt.success:
        print(f"Action {receipt.action_id} succeeded")
    else:
        print(f"Action {receipt.action_id} failed: {receipt.error}")
```

## Execution Modes

### Simulate Mode
- Uses `SimulationProvider`
- No actual messages sent
- Records all actions for testing
- Perfect for development and testing

```python
execution_run = ExecutionRun(
    id="run_001",
    mode=ExecutionMode.SIMULATE,
    user_id="user_123",
    conversation_id="conv_456"
)
```

### Sandbox Mode
- Uses `CloudProvider` in sandbox mode
- Sends messages to test phone numbers
- Requires API credentials

```python
execution_run = ExecutionRun(
    id="run_002",
    mode=ExecutionMode.SANDBOX,
    user_id="user_123",
    conversation_id="conv_456"
)
```

### Live Mode
- Uses `CloudProvider` in production mode
- Sends messages to real users
- Requires API credentials

```python
execution_run = ExecutionRun(
    id="run_003",
    mode=ExecutionMode.LIVE,
    user_id="user_123",
    conversation_id="conv_456"
)
```

## Action Types

### 1. Send Message
Sends a simple text message to the user.

```python
ActionPlan(
    id="action_001",
    action_type=ActionType.SEND_MESSAGE,
    payload={"message": "Hello, World!"},
    order=1
)
```

### 2. Send Buttons
Sends a message with interactive buttons.

```python
ActionPlan(
    id="action_002",
    action_type=ActionType.SEND_BUTTONS,
    payload={
        "message": "Choose an option:",
        "buttons": [
            {"id": "btn1", "text": "Option 1"},
            {"id": "btn2", "text": "Option 2"},
            {"id": "btn3", "text": "Option 3"}
        ]
    },
    order=2
)
```

### 3. Ask Question
Sends a question and sets the `awaitingReply` state.

```python
ActionPlan(
    id="action_003",
    action_type=ActionType.ASK_QUESTION,
    payload={"question": "What is your email address?"},
    order=3
)
```

After execution, `execution_run.awaiting_reply` will be set to `True`.

### 4. Handoff
Transfers the conversation to an agent.

```python
ActionPlan(
    id="action_004",
    action_type=ActionType.HANDOFF,
    payload={
        "agent_message": "User needs assistance with billing",
        "user_message": "Connecting you to an agent..."
    },
    order=4
)
```

### 5. Delay
Schedules a delay before the next action.

```python
ActionPlan(
    id="action_005",
    action_type=ActionType.DELAY,
    payload={"delay_seconds": 5},
    order=5
)
```

## Safe Failure Behavior

The dispatcher implements safe failure behavior to prevent partial spam:

1. **Sequential Execution**: Actions are executed in order
2. **Stop on Failure**: If any action fails, subsequent actions are not executed
3. **Complete Receipts**: All attempted actions generate receipts in traceJson
4. **No Partial Spam**: Users never receive incomplete conversation flows

### Example

```python
actions = [
    ActionPlan(id="1", action_type=ActionType.SEND_MESSAGE, 
               payload={"message": "First"}, order=1),
    ActionPlan(id="2", action_type=ActionType.SEND_MESSAGE, 
               payload={"message": "Second"}, order=2),  # This fails
    ActionPlan(id="3", action_type=ActionType.SEND_MESSAGE, 
               payload={"message": "Third"}, order=3),   # Not executed
]

receipts = await dispatcher.dispatch(execution_run, actions)
# Result: Only actions 1 and 2 are attempted, action 3 is skipped
```

## Receipt Tracking

All dispatched actions are recorded in the execution run's `trace_json`:

```python
receipts = await dispatcher.dispatch(execution_run, action_plans)

# Check trace JSON
print(execution_run.trace_json["dispatched_actions"])
# [
#   {
#     "action_id": "action_001",
#     "success": true,
#     "timestamp": "2024-02-04T12:00:00",
#     "provider_response": {...}
#   },
#   ...
# ]
```

## Testing

Run the test suite:

```bash
pytest tests/core/whatsapp/test_dispatcher.py -v
```

### Test Coverage

- Provider selection for all modes
- All action types
- Multiple actions in sequence
- Action ordering
- Safe failure behavior
- Receipt recording in traceJson
- Simulation provider functionality

## Error Handling

### DispatcherError
Raised for critical dispatcher errors (e.g., missing credentials).

```python
try:
    dispatcher = Dispatcher()  # No credentials
    provider = dispatcher._get_provider(sandbox_run)
except DispatcherError as e:
    print(f"Dispatcher error: {e}")
```

### ProviderError
Raised when a provider operation fails.

### Graceful Degradation
Individual action failures are captured in receipts without raising exceptions:

```python
receipts = await dispatcher.dispatch(execution_run, action_plans)

for receipt in receipts:
    if not receipt.success:
        logger.error(f"Action failed: {receipt.error}")
        # Handle failure gracefully
```

## Best Practices

1. **Always use simulation mode for testing**: Test your action flows without sending real messages
2. **Handle receipts**: Check receipt success status and handle failures appropriately
3. **Order matters**: Set action order explicitly to ensure correct execution sequence
4. **Provide complete payloads**: Include all required fields in action payloads
5. **Monitor traceJson**: Use traceJson for debugging and auditing

## Integration

### With Existing Systems

```python
# In your application
from src.core.whatsapp import Dispatcher, ExecutionRun, ActionPlan

class ConversationOrchestrator:
    def __init__(self):
        self.dispatcher = Dispatcher(
            cloud_api_key=settings.WHATSAPP_API_KEY,
            cloud_endpoint=settings.WHATSAPP_ENDPOINT
        )
    
    async def execute_conversation_flow(
        self, 
        user_id: str, 
        conversation_id: str,
        actions: List[ActionPlan]
    ):
        run = ExecutionRun(
            id=generate_run_id(),
            mode=ExecutionMode.LIVE,
            user_id=user_id,
            conversation_id=conversation_id
        )
        
        receipts = await self.dispatcher.dispatch(run, actions)
        
        # Store receipts in database
        await self.save_execution_receipts(receipts)
        
        return receipts
```

## License

See project LICENSE file.
