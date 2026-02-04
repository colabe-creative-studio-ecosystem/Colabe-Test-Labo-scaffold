"""
Inbound Processor Pipeline

Flow: Webhook event → normalize → load live automations → run engine → dispatch actions

Steps:
1. Resolve workspace + conversation context
2. Load automations with status=live for workspace
3. Find trigger-matched flows (TRIGGER_MESSAGE)
4. Run executor in mode based on workspace setting (default: simulate in staging, live in prod)
5. Dispatch emitted actions via dispatcher
6. Write ExecutionRun trace + status
7. Write AuditLog for notable actions (handoff, payment link sent, etc.)
"""

import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import reflex as rx
import sqlmodel
from sqlalchemy import select

from app.core.models import (
    Tenant,
    Conversation,
    Automation,
    AutomationTriggerEnum,
    AutomationStatusEnum,
    ExecutionRun,
    ExecutionRunStatusEnum,
    AuditLog,
    WorkspaceSettings,
)

logger = logging.getLogger(__name__)


class InboundProcessorError(Exception):
    """Base exception for inbound processor errors"""
    pass


class TransientError(InboundProcessorError):
    """Transient error that should trigger retry"""
    pass


class PermanentError(InboundProcessorError):
    """Permanent error that should not retry"""
    pass


class InboundProcessor:
    """
    Main processor for handling incoming webhook events and executing automations
    """

    def __init__(self, max_retries: int = 3, retry_delay_base: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay_base = retry_delay_base

    async def process_event(
        self, event_data: Dict[str, Any], retry_count: int = 0
    ) -> Dict[str, Any]:
        """
        Main entry point for processing inbound webhook events

        Args:
            event_data: Raw webhook event data
            retry_count: Current retry attempt number

        Returns:
            Dict with processing results

        Raises:
            TransientError: For retryable errors
            PermanentError: For non-retryable errors
        """
        try:
            # Step 1: Normalize the event
            normalized_event = self._normalize_event(event_data)
            logger.info(f"Normalized event: {normalized_event.get('event_type')}")

            # Step 2: Resolve workspace and conversation context
            workspace_id, conversation = await self._resolve_context(normalized_event)
            logger.info(
                f"Resolved context - workspace: {workspace_id}, "
                f"conversation: {conversation.id if conversation else None}"
            )

            # Step 3: Load live automations for workspace
            automations = await self._load_live_automations(
                workspace_id, normalized_event["event_type"]
            )
            logger.info(f"Found {len(automations)} live automations")

            if not automations:
                return {
                    "status": "skipped",
                    "reason": "no_matching_automations",
                    "workspace_id": workspace_id,
                }

            # Step 4: Get workspace execution settings
            execution_mode = await self._get_execution_mode(workspace_id)
            logger.info(f"Execution mode: {execution_mode}")

            results = []
            for automation in automations:
                try:
                    # Step 5: Run executor for each automation
                    execution_result = await self._run_executor(
                        automation, normalized_event, conversation, execution_mode
                    )

                    # Step 6: Dispatch emitted actions
                    dispatch_result = await self._dispatch_actions(
                        automation, execution_result, conversation
                    )

                    # Step 7: Write ExecutionRun trace
                    execution_run = await self._write_execution_trace(
                        automation,
                        conversation,
                        execution_result,
                        dispatch_result,
                        execution_mode,
                        retry_count,
                    )

                    # Step 8: Write AuditLog for notable actions
                    await self._write_audit_logs(
                        automation, execution_run, dispatch_result
                    )

                    results.append(
                        {
                            "automation_id": automation.id,
                            "execution_run_id": execution_run.id,
                            "status": "success",
                        }
                    )

                except TransientError as e:
                    logger.warning(
                        f"Transient error processing automation {automation.id}: {e}"
                    )
                    results.append(
                        {
                            "automation_id": automation.id,
                            "status": "transient_error",
                            "error": str(e),
                        }
                    )
                    # Re-raise to trigger retry at top level
                    if retry_count < self.max_retries:
                        raise

                except PermanentError as e:
                    logger.error(
                        f"Permanent error processing automation {automation.id}: {e}"
                    )
                    results.append(
                        {
                            "automation_id": automation.id,
                            "status": "permanent_error",
                            "error": str(e),
                        }
                    )
                    # Don't re-raise, continue with other automations

            return {
                "status": "completed",
                "workspace_id": workspace_id,
                "conversation_id": conversation.id if conversation else None,
                "results": results,
            }

        except TransientError:
            # Re-raise transient errors for retry logic
            raise
        except Exception as e:
            logger.exception(f"Unexpected error in process_event: {e}")
            raise PermanentError(f"Unexpected error: {e}") from e

    def _normalize_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize incoming webhook event to standard format

        Expected input format:
        {
            "type": "message.received",
            "workspace_id": "123",
            "conversation_id": "conv_456",
            "channel": "slack",
            "payload": {...}
        }
        """
        # Extract and validate required fields
        event_type = event_data.get("type")
        if not event_type:
            raise PermanentError("Missing event type")

        workspace_id = event_data.get("workspace_id") or event_data.get("tenant_id")
        if not workspace_id:
            raise PermanentError("Missing workspace_id or tenant_id")

        return {
            "event_type": event_type,
            "workspace_id": int(workspace_id),
            "conversation_id": event_data.get("conversation_id"),
            "channel": event_data.get("channel", "unknown"),
            "payload": event_data.get("payload", {}),
            "timestamp": event_data.get("timestamp", datetime.now().isoformat()),
        }

    async def _resolve_context(
        self, normalized_event: Dict[str, Any]
    ) -> tuple[int, Optional[Conversation]]:
        """
        Resolve workspace and conversation context

        Returns:
            Tuple of (workspace_id, conversation or None)
        """
        workspace_id = normalized_event["workspace_id"]

        # Verify workspace exists
        with rx.session() as db_session:
            tenant = db_session.exec(
                select(Tenant).where(Tenant.id == workspace_id)
            ).first()

            if not tenant:
                raise PermanentError(f"Workspace {workspace_id} not found")

            # Get or create conversation if conversation_id provided
            conversation = None
            conversation_external_id = normalized_event.get("conversation_id")

            if conversation_external_id:
                conversation = db_session.exec(
                    select(Conversation).where(
                        Conversation.tenant_id == workspace_id,
                        Conversation.external_id == conversation_external_id,
                    )
                ).first()

                if not conversation:
                    # Create new conversation
                    conversation = Conversation(
                        tenant_id=workspace_id,
                        external_id=conversation_external_id,
                        channel=normalized_event.get("channel", "unknown"),
                        status="active",
                        metadata=json.dumps(normalized_event.get("payload", {})),
                    )
                    db_session.add(conversation)
                    db_session.commit()
                    db_session.refresh(conversation)
                    logger.info(f"Created new conversation: {conversation.id}")
                else:
                    # Update conversation timestamp
                    conversation.updated_at = datetime.now()
                    db_session.add(conversation)
                    db_session.commit()

            return workspace_id, conversation

    async def _load_live_automations(
        self, workspace_id: int, event_type: str
    ) -> List[Automation]:
        """
        Load automations with status=live for workspace that match the event type

        Args:
            workspace_id: The workspace/tenant ID
            event_type: The type of event to match against

        Returns:
            List of matching Automation objects
        """
        with rx.session() as db_session:
            # Map event type to trigger type
            trigger_type = self._map_event_to_trigger(event_type)

            # Query automations
            query = select(Automation).where(
                Automation.tenant_id == workspace_id,
                Automation.status == AutomationStatusEnum.LIVE,
                Automation.trigger_type == trigger_type,
            )

            automations = db_session.exec(query).all()
            return list(automations)

    def _map_event_to_trigger(self, event_type: str) -> AutomationTriggerEnum:
        """
        Map event type to automation trigger type

        Args:
            event_type: Event type from webhook (e.g., "message.received")

        Returns:
            AutomationTriggerEnum value
        """
        # Map common event types to trigger types
        event_trigger_map = {
            "message.received": AutomationTriggerEnum.TRIGGER_MESSAGE,
            "message.sent": AutomationTriggerEnum.TRIGGER_MESSAGE,
            "webhook": AutomationTriggerEnum.TRIGGER_WEBHOOK,
            "scheduled": AutomationTriggerEnum.TRIGGER_SCHEDULE,
        }

        # Default to TRIGGER_EVENT for unknown types
        return event_trigger_map.get(event_type, AutomationTriggerEnum.TRIGGER_EVENT)

    async def _get_execution_mode(self, workspace_id: int) -> str:
        """
        Get execution mode based on workspace settings

        Default behavior:
        - In staging environment: simulate
        - In production environment: live
        - Can be overridden by workspace settings

        Returns:
            "simulate" or "live"
        """
        with rx.session() as db_session:
            settings = db_session.exec(
                select(WorkspaceSettings).where(
                    WorkspaceSettings.tenant_id == workspace_id
                )
            ).first()

            if not settings:
                # Default behavior based on environment
                # In a real system, check environment variable
                return "live"  # Default to live for production

            # Auto mode uses environment-based logic
            if settings.execution_mode == "auto":
                return "simulate" if settings.environment == "staging" else "live"

            # Otherwise use explicit setting
            return settings.execution_mode

    async def _run_executor(
        self,
        automation: Automation,
        normalized_event: Dict[str, Any],
        conversation: Optional[Conversation],
        execution_mode: str,
    ) -> Dict[str, Any]:
        """
        Run the automation executor

        Args:
            automation: The automation to execute
            normalized_event: The normalized event data
            conversation: The conversation context (if any)
            execution_mode: "simulate" or "live"

        Returns:
            Execution result with actions to dispatch
        """
        try:
            # Parse flow definition
            flow_definition = json.loads(automation.flow_definition)

            # Execute flow steps
            execution_trace = []
            actions = []

            for step in flow_definition.get("steps", []):
                step_result = {
                    "step": step.get("name"),
                    "type": step.get("type"),
                    "timestamp": datetime.now().isoformat(),
                    "mode": execution_mode,
                }

                # In simulate mode, log but don't execute
                if execution_mode == "simulate":
                    step_result["simulated"] = True
                    step_result["would_execute"] = step.get("action")
                else:
                    step_result["executed"] = True
                    # Extract action from step
                    if step.get("action"):
                        actions.append(step["action"])

                execution_trace.append(step_result)

            return {
                "status": "success",
                "mode": execution_mode,
                "execution_trace": execution_trace,
                "actions": actions,
            }

        except json.JSONDecodeError as e:
            raise PermanentError(f"Invalid flow definition JSON: {e}") from e
        except Exception as e:
            # Database errors, network issues, etc. are transient
            raise TransientError(f"Executor error: {e}") from e

    async def _dispatch_actions(
        self,
        automation: Automation,
        execution_result: Dict[str, Any],
        conversation: Optional[Conversation],
    ) -> Dict[str, Any]:
        """
        Dispatch emitted actions from the executor

        Args:
            automation: The automation that generated actions
            execution_result: Result from executor with actions
            conversation: The conversation context

        Returns:
            Dispatch results
        """
        dispatched = []
        actions = execution_result.get("actions", [])

        for action in actions:
            try:
                action_type = action.get("type")
                action_data = action.get("data", {})

                # In simulate mode, log but don't dispatch
                if execution_result.get("mode") == "simulate":
                    dispatched.append(
                        {
                            "action_type": action_type,
                            "simulated": True,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                    continue

                # Dispatch based on action type
                dispatch_result = await self._dispatch_action_type(
                    action_type, action_data, conversation
                )

                dispatched.append(
                    {
                        "action_type": action_type,
                        "executed": True,
                        "result": dispatch_result,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            except Exception as e:
                logger.exception(f"Error dispatching action {action.get('type')}: {e}")
                dispatched.append(
                    {
                        "action_type": action.get("type"),
                        "error": str(e),
                        "timestamp": datetime.now().isoformat(),
                    }
                )

        return {"dispatched_actions": dispatched}

    async def _dispatch_action_type(
        self, action_type: str, action_data: Dict[str, Any], conversation: Optional[Conversation]
    ) -> Dict[str, Any]:
        """
        Dispatch a specific action type

        Notable action types that should be audited:
        - handoff: Transfer conversation to human agent
        - payment_link: Send payment link
        - notification: Send notification
        """
        # In a real system, this would integrate with external services
        # For now, we'll log the action

        logger.info(f"Dispatching action: {action_type} with data: {action_data}")

        # Simulate action dispatch
        return {
            "status": "dispatched",
            "action_type": action_type,
            "conversation_id": conversation.id if conversation else None,
        }

    async def _write_execution_trace(
        self,
        automation: Automation,
        conversation: Optional[Conversation],
        execution_result: Dict[str, Any],
        dispatch_result: Dict[str, Any],
        execution_mode: str,
        retry_count: int,
    ) -> ExecutionRun:
        """
        Write ExecutionRun trace with status

        Args:
            automation: The executed automation
            conversation: The conversation context
            execution_result: Result from executor
            dispatch_result: Result from dispatcher
            execution_mode: The execution mode used
            retry_count: Number of retries attempted

        Returns:
            Created ExecutionRun object
        """
        with rx.session() as db_session:
            execution_run = ExecutionRun(
                automation_id=automation.id,
                conversation_id=conversation.id if conversation else None,
                tenant_id=automation.tenant_id,
                status=ExecutionRunStatusEnum.COMPLETED,
                mode=execution_mode,
                trigger_data=json.dumps(execution_result.get("execution_trace", [])),
                execution_trace=json.dumps(execution_result.get("execution_trace", [])),
                actions_dispatched=json.dumps(
                    dispatch_result.get("dispatched_actions", [])
                ),
                retry_count=retry_count,
                started_at=datetime.now(),
                completed_at=datetime.now(),
            )

            db_session.add(execution_run)
            db_session.commit()
            db_session.refresh(execution_run)

            logger.info(f"Created ExecutionRun: {execution_run.id}")
            return execution_run

    async def _write_audit_logs(
        self,
        automation: Automation,
        execution_run: ExecutionRun,
        dispatch_result: Dict[str, Any],
    ) -> None:
        """
        Write AuditLog entries for notable actions

        Notable actions:
        - handoff: Conversation transferred to human
        - payment_link: Payment link sent
        - notification: Important notification sent
        """
        notable_action_types = {"handoff", "payment_link", "notification", "escalation"}

        dispatched_actions = dispatch_result.get("dispatched_actions", [])

        with rx.session() as db_session:
            for action in dispatched_actions:
                action_type = action.get("action_type")

                if action_type in notable_action_types:
                    audit_log = AuditLog(
                        tenant_id=automation.tenant_id,
                        user_id=automation.created_by,
                        action=f"automation.{action_type}",
                        details=json.dumps(
                            {
                                "automation_id": automation.id,
                                "automation_name": automation.name,
                                "execution_run_id": execution_run.id,
                                "action": action,
                            }
                        ),
                        timestamp=datetime.now(),
                    )
                    db_session.add(audit_log)

            db_session.commit()
            logger.info(
                f"Created audit logs for {len(dispatched_actions)} notable actions"
            )


# Retry decorator for transient errors
def with_retry(max_retries: int = 3, base_delay: float = 2.0):
    """
    Decorator to add retry logic with exponential backoff

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds (will be exponentially increased)
    """
    import time
    from functools import wraps

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs, retry_count=attempt)
                except TransientError as e:
                    last_exception = e
                    if attempt < max_retries:
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            f"Transient error on attempt {attempt + 1}/{max_retries + 1}, "
                            f"retrying in {delay}s: {e}"
                        )
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"Max retries ({max_retries}) exceeded for transient error: {e}"
                        )
                except PermanentError:
                    # Don't retry permanent errors
                    raise

            # If we get here, we've exhausted retries
            raise last_exception

        return wrapper

    return decorator


# Main entry point with retry logic
@with_retry(max_retries=3, base_delay=2.0)
async def process_inbound_event(
    event_data: Dict[str, Any], retry_count: int = 0
) -> Dict[str, Any]:
    """
    Main entry point for processing inbound webhook events with retry logic

    Args:
        event_data: Raw webhook event data
        retry_count: Current retry attempt (managed by decorator)

    Returns:
        Processing results

    Raises:
        PermanentError: For non-retryable errors
    """
    processor = InboundProcessor()
    return await processor.process_event(event_data, retry_count)
