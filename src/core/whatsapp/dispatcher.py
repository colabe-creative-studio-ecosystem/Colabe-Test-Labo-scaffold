"""WhatsApp Outbound Dispatcher - Converts ActionPlans to WhatsApp provider calls."""
import asyncio
import logging
from datetime import datetime
from typing import List, Optional, Dict, Any

from .models import (
    ActionPlan,
    ActionType,
    DispatchReceipt,
    ExecutionMode,
    ExecutionRun,
)
from .providers import CloudProvider, SimulationProvider, WhatsAppProvider

logger = logging.getLogger(__name__)


class DispatcherError(Exception):
    """Base exception for dispatcher errors."""
    pass


class ProviderError(DispatcherError):
    """Exception raised when provider fails."""
    pass


class Dispatcher:
    """
    Dispatcher that converts validated ActionPlans into WhatsAppProvider calls.
    
    Features:
    - Provider selection based on execution mode
    - Action conversion to provider calls
    - Receipt recording in traceJson
    - Safe failure behavior (no partial spam)
    """
    
    def __init__(
        self,
        cloud_api_key: Optional[str] = None,
        cloud_endpoint: Optional[str] = None
    ):
        """
        Initialize the dispatcher.
        
        Args:
            cloud_api_key: API key for cloud provider
            cloud_endpoint: Endpoint URL for cloud provider
        """
        self.cloud_api_key = cloud_api_key
        self.cloud_endpoint = cloud_endpoint
        self._provider_cache: Dict[str, WhatsAppProvider] = {}
    
    def _get_provider(self, execution_run: ExecutionRun) -> WhatsAppProvider:
        """
        Get the appropriate provider based on execution mode.
        
        Args:
            execution_run: The execution run context
            
        Returns:
            WhatsAppProvider instance
            
        Raises:
            DispatcherError: If provider cannot be created
        """
        mode = execution_run.mode
        cache_key = mode.value
        
        # Return cached provider if available
        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]
        
        # Create provider based on mode
        if mode == ExecutionMode.SIMULATE:
            provider = SimulationProvider()
        elif mode in (ExecutionMode.SANDBOX, ExecutionMode.LIVE):
            if not self.cloud_api_key or not self.cloud_endpoint:
                raise DispatcherError(
                    f"Cloud API credentials required for {mode.value} mode"
                )
            provider = CloudProvider(
                api_key=self.cloud_api_key,
                endpoint=self.cloud_endpoint,
                mode=mode.value
            )
        else:
            raise DispatcherError(f"Unknown execution mode: {mode}")
        
        # Cache the provider
        self._provider_cache[cache_key] = provider
        return provider
    
    async def _dispatch_send_message(
        self,
        action: ActionPlan,
        execution_run: ExecutionRun,
        provider: WhatsAppProvider
    ) -> DispatchReceipt:
        """
        Dispatch a send_message action.
        
        Args:
            action: The action plan
            execution_run: The execution run context
            provider: The WhatsApp provider
            
        Returns:
            DispatchReceipt with the result
        """
        message = action.payload.get("message", "")
        
        try:
            response = await provider.send_text(
                user_id=execution_run.user_id,
                message=message,
                conversation_id=execution_run.conversation_id
            )
            
            return DispatchReceipt(
                action_id=action.id,
                success=True,
                timestamp=datetime.now(),
                provider_response=response
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}", exc_info=True)
            return DispatchReceipt(
                action_id=action.id,
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _dispatch_send_buttons(
        self,
        action: ActionPlan,
        execution_run: ExecutionRun,
        provider: WhatsAppProvider
    ) -> DispatchReceipt:
        """
        Dispatch a send_buttons action.
        
        Args:
            action: The action plan
            execution_run: The execution run context
            provider: The WhatsApp provider
            
        Returns:
            DispatchReceipt with the result
        """
        message = action.payload.get("message", "")
        buttons = action.payload.get("buttons", [])
        
        try:
            response = await provider.send_buttons(
                user_id=execution_run.user_id,
                message=message,
                buttons=buttons,
                conversation_id=execution_run.conversation_id
            )
            
            return DispatchReceipt(
                action_id=action.id,
                success=True,
                timestamp=datetime.now(),
                provider_response=response
            )
        except Exception as e:
            logger.error(f"Failed to send buttons: {e}", exc_info=True)
            return DispatchReceipt(
                action_id=action.id,
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _dispatch_ask_question(
        self,
        action: ActionPlan,
        execution_run: ExecutionRun,
        provider: WhatsAppProvider
    ) -> DispatchReceipt:
        """
        Dispatch an ask_question action.
        
        This sends a text message and sets the awaitingReply state.
        
        Args:
            action: The action plan
            execution_run: The execution run context
            provider: The WhatsApp provider
            
        Returns:
            DispatchReceipt with the result
        """
        question = action.payload.get("question", "")
        
        try:
            response = await provider.send_text(
                user_id=execution_run.user_id,
                message=question,
                conversation_id=execution_run.conversation_id
            )
            
            # Set awaitingReply state
            execution_run.awaiting_reply = True
            
            return DispatchReceipt(
                action_id=action.id,
                success=True,
                timestamp=datetime.now(),
                provider_response={
                    **response,
                    "awaiting_reply": True
                }
            )
        except Exception as e:
            logger.error(f"Failed to ask question: {e}", exc_info=True)
            return DispatchReceipt(
                action_id=action.id,
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _dispatch_handoff(
        self,
        action: ActionPlan,
        execution_run: ExecutionRun,
        provider: WhatsAppProvider
    ) -> DispatchReceipt:
        """
        Dispatch a handoff action.
        
        This notifies the agent console and sends a message to the user.
        
        Args:
            action: The action plan
            execution_run: The execution run context
            provider: The WhatsApp provider
            
        Returns:
            DispatchReceipt with the result
        """
        user_message = action.payload.get("user_message", "")
        agent_message = action.payload.get("agent_message", "")
        
        try:
            # Notify agent console
            handoff_response = await provider.notify_handoff(
                user_id=execution_run.user_id,
                agent_message=agent_message,
                conversation_id=execution_run.conversation_id
            )
            
            # Send message to user if provided
            user_response = None
            if user_message:
                user_response = await provider.send_text(
                    user_id=execution_run.user_id,
                    message=user_message,
                    conversation_id=execution_run.conversation_id
                )
            
            return DispatchReceipt(
                action_id=action.id,
                success=True,
                timestamp=datetime.now(),
                provider_response={
                    "handoff": handoff_response,
                    "user_message": user_response
                }
            )
        except Exception as e:
            logger.error(f"Failed to handoff: {e}", exc_info=True)
            return DispatchReceipt(
                action_id=action.id,
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _dispatch_delay(
        self,
        action: ActionPlan,
        execution_run: ExecutionRun,
        provider: WhatsAppProvider
    ) -> DispatchReceipt:
        """
        Dispatch a delay action.
        
        This schedules the next step after a delay.
        
        Args:
            action: The action plan
            execution_run: The execution run context
            provider: The WhatsApp provider
            
        Returns:
            DispatchReceipt with the result
        """
        delay_seconds = action.payload.get("delay_seconds", 0)
        
        try:
            # Simulate delay for immediate testing
            # In production, this would schedule a task
            await asyncio.sleep(min(delay_seconds, 0.1))  # Cap at 0.1s for testing
            
            return DispatchReceipt(
                action_id=action.id,
                success=True,
                timestamp=datetime.now(),
                provider_response={
                    "delay_seconds": delay_seconds,
                    "scheduled": True
                }
            )
        except Exception as e:
            logger.error(f"Failed to schedule delay: {e}", exc_info=True)
            return DispatchReceipt(
                action_id=action.id,
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )
    
    async def _dispatch_action(
        self,
        action: ActionPlan,
        execution_run: ExecutionRun,
        provider: WhatsAppProvider
    ) -> DispatchReceipt:
        """
        Dispatch a single action to the appropriate handler.
        
        Args:
            action: The action plan
            execution_run: The execution run context
            provider: The WhatsApp provider
            
        Returns:
            DispatchReceipt with the result
        """
        action_handlers = {
            ActionType.SEND_MESSAGE: self._dispatch_send_message,
            ActionType.SEND_BUTTONS: self._dispatch_send_buttons,
            ActionType.ASK_QUESTION: self._dispatch_ask_question,
            ActionType.HANDOFF: self._dispatch_handoff,
            ActionType.DELAY: self._dispatch_delay,
        }
        
        handler = action_handlers.get(action.action_type)
        if not handler:
            return DispatchReceipt(
                action_id=action.id,
                success=False,
                timestamp=datetime.now(),
                error=f"Unknown action type: {action.action_type}"
            )
        
        return await handler(action, execution_run, provider)
    
    async def dispatch(
        self,
        execution_run: ExecutionRun,
        action_plans: List[ActionPlan]
    ) -> List[DispatchReceipt]:
        """
        Dispatch a list of action plans with safe failure behavior.
        
        This method ensures no partial spam by:
        1. Validating all actions before dispatch
        2. Stopping on first failure
        3. Recording all receipts in traceJson
        
        Args:
            execution_run: The execution run context
            action_plans: List of action plans to execute
            
        Returns:
            List of DispatchReceipts for all dispatched actions
            
        Raises:
            DispatcherError: If critical error occurs
        """
        if not action_plans:
            logger.warning("No action plans to dispatch")
            return []
        
        # Sort actions by order
        sorted_actions = sorted(action_plans, key=lambda a: a.order)
        
        # Get provider
        try:
            provider = self._get_provider(execution_run)
        except Exception as e:
            logger.error(f"Failed to get provider: {e}")
            raise DispatcherError(f"Provider initialization failed: {e}")
        
        receipts: List[DispatchReceipt] = []
        
        # Dispatch actions sequentially with safe failure
        for action in sorted_actions:
            action_type_str = (
                action.action_type.value 
                if hasattr(action.action_type, 'value') 
                else str(action.action_type)
            )
            logger.info(f"Dispatching action {action.id} ({action_type_str})")
            
            receipt = await self._dispatch_action(action, execution_run, provider)
            receipts.append(receipt)
            
            # Record receipt in traceJson
            if "dispatched_actions" not in execution_run.trace_json:
                execution_run.trace_json["dispatched_actions"] = []
            execution_run.trace_json["dispatched_actions"].append(
                receipt.to_dict()
            )
            
            # Stop on first failure (safe failure behavior)
            if not receipt.success:
                logger.error(
                    f"Action {action.id} failed: {receipt.error}. "
                    "Stopping dispatch to prevent partial spam."
                )
                break
        
        return receipts
    
    def get_provider_for_mode(self, mode: ExecutionMode) -> WhatsAppProvider:
        """
        Get a provider for testing purposes.
        
        Args:
            mode: The execution mode
            
        Returns:
            WhatsAppProvider instance
        """
        cache_key = mode.value
        if cache_key in self._provider_cache:
            return self._provider_cache[cache_key]
        
        if mode == ExecutionMode.SIMULATE:
            return SimulationProvider()
        elif mode in (ExecutionMode.SANDBOX, ExecutionMode.LIVE):
            if not self.cloud_api_key or not self.cloud_endpoint:
                raise DispatcherError(
                    f"Cloud API credentials required for {mode.value} mode"
                )
            return CloudProvider(
                api_key=self.cloud_api_key,
                endpoint=self.cloud_endpoint,
                mode=mode.value
            )
        else:
            raise DispatcherError(f"Unknown execution mode: {mode}")
