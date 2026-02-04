"""
Cloud WhatsApp Provider (Stub)

Placeholder implementation for WhatsApp Cloud API integration.
Actual API calls will be implemented later.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
import hmac
import hashlib

from .provider import (
    WhatsAppProvider,
    WebhookVerifier,
    WhatsAppEventParser,
    MessageReceipt,
    MessageButton,
    ListItem,
    EngineEvent,
    EventType,
)

logger = logging.getLogger(__name__)


class CloudProvider(WhatsAppProvider):
    """
    Cloud provider for WhatsApp Business API.
    
    This is a placeholder/stub implementation. Actual API integration
    will be added in a future iteration.
    
    For production use, this would:
    - Use WhatsApp Cloud API (https://developers.facebook.com/docs/whatsapp/cloud-api)
    - Handle authentication via access tokens
    - Make HTTP requests to WhatsApp API endpoints
    - Handle rate limiting and retries
    - Process error responses appropriately
    """

    def __init__(
        self,
        phone_number_id: str,
        access_token: str,
        api_version: str = "v18.0"
    ):
        """
        Initialize the cloud provider.
        
        Args:
            phone_number_id: WhatsApp Business phone number ID
            access_token: Access token for WhatsApp Cloud API
            api_version: API version to use (default: v18.0)
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://graph.facebook.com/{api_version}"
        
        logger.info(
            f"CloudProvider initialized (phone_number_id={phone_number_id}, "
            f"api_version={api_version})"
        )

    def send_text(
        self,
        to: str,
        text: str,
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send a text message via WhatsApp Cloud API.
        
        TODO: Implement actual API call to:
        POST /{phone-number-id}/messages
        {
            "messaging_product": "whatsapp",
            "to": "{to}",
            "type": "text",
            "text": {"body": "{text}"}
        }
        """
        logger.warning(
            "CloudProvider.send_text called but not implemented. "
            "Returning mock receipt."
        )
        
        # Placeholder implementation
        return MessageReceipt(
            message_id="stub_msg_id",
            timestamp=datetime.now(),
            success=False,
            error_message="CloudProvider not yet implemented",
            metadata=meta,
        )

    def send_buttons(
        self,
        to: str,
        text: str,
        buttons: List[MessageButton],
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send an interactive button message via WhatsApp Cloud API.
        
        TODO: Implement actual API call with interactive message type.
        """
        logger.warning(
            "CloudProvider.send_buttons called but not implemented. "
            "Returning mock receipt."
        )
        
        return MessageReceipt(
            message_id="stub_msg_id",
            timestamp=datetime.now(),
            success=False,
            error_message="CloudProvider not yet implemented",
            metadata=meta,
        )

    def send_list(
        self,
        to: str,
        header: str,
        items: List[ListItem],
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send an interactive list message via WhatsApp Cloud API.
        
        TODO: Implement actual API call with list message type.
        """
        logger.warning(
            "CloudProvider.send_list called but not implemented. "
            "Returning mock receipt."
        )
        
        return MessageReceipt(
            message_id="stub_msg_id",
            timestamp=datetime.now(),
            success=False,
            error_message="CloudProvider not yet implemented",
            metadata=meta,
        )

    def send_media(
        self,
        to: str,
        media_url_or_id: str,
        caption: Optional[str] = None,
        meta: Optional[Dict[str, Any]] = None
    ) -> MessageReceipt:
        """
        Send a media message via WhatsApp Cloud API.
        
        TODO: Implement actual API call with media message type.
        Supports image, video, document, audio types.
        """
        logger.warning(
            "CloudProvider.send_media called but not implemented. "
            "Returning mock receipt."
        )
        
        return MessageReceipt(
            message_id="stub_msg_id",
            timestamp=datetime.now(),
            success=False,
            error_message="CloudProvider not yet implemented",
            metadata=meta,
        )

    def mark_read(self, message_id: str) -> None:
        """
        Mark a message as read via WhatsApp Cloud API.
        
        TODO: Implement actual API call to mark message as read.
        POST /{phone-number-id}/messages
        {
            "messaging_product": "whatsapp",
            "status": "read",
            "message_id": "{message_id}"
        }
        """
        logger.warning(
            f"CloudProvider.mark_read called for message_id={message_id} "
            "but not implemented."
        )


class CloudWebhookVerifier(WebhookVerifier):
    """
    Cloud webhook verifier for WhatsApp.
    
    Verifies webhook signatures using HMAC SHA-256.
    """

    def __init__(self, app_secret: str):
        """
        Initialize the verifier.
        
        Args:
            app_secret: App secret from Meta for Business dashboard
        """
        self.app_secret = app_secret
        logger.info("CloudWebhookVerifier initialized")

    def verify(self, signature: str, raw_body: bytes) -> bool:
        """
        Verify webhook signature using HMAC SHA-256.
        
        WhatsApp sends signature in X-Hub-Signature-256 header as:
        "sha256={hash}"
        
        Args:
            signature: Signature from X-Hub-Signature-256 header
            raw_body: Raw request body bytes
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            # Remove "sha256=" prefix if present
            if signature.startswith("sha256="):
                signature = signature[7:]
            
            # Calculate expected signature
            expected_signature = hmac.new(
                self.app_secret.encode(),
                raw_body,
                hashlib.sha256
            ).hexdigest()
            
            # Compare using constant-time comparison
            is_valid = hmac.compare_digest(signature, expected_signature)
            
            if not is_valid:
                logger.warning("Webhook signature verification failed")
            
            return is_valid
        
        except Exception as e:
            logger.error(f"Error verifying webhook signature: {e}", exc_info=True)
            return False


class CloudEventParser(WhatsAppEventParser):
    """
    Cloud event parser for WhatsApp Cloud API webhooks.
    
    Parses the official WhatsApp Cloud API webhook format.
    """

    def parse(self, raw_webhook: Dict[str, Any]) -> List[EngineEvent]:
        """
        Parse WhatsApp Cloud API webhook payload.
        
        Official format:
        {
            "object": "whatsapp_business_account",
            "entry": [{
                "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
                "changes": [{
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {...},
                        "messages": [...],
                        "statuses": [...]
                    },
                    "field": "messages"
                }]
            }]
        }
        """
        events: List[EngineEvent] = []
        
        try:
            # Verify this is a WhatsApp webhook
            if raw_webhook.get("object") != "whatsapp_business_account":
                logger.warning("Received non-WhatsApp webhook")
                return events
            
            entries = raw_webhook.get("entry", [])
            
            for entry in entries:
                changes = entry.get("changes", [])
                
                for change in changes:
                    value = change.get("value", {})
                    
                    # Parse messages
                    messages = value.get("messages", [])
                    for message in messages:
                        event = self._parse_message(message)
                        if event:
                            events.append(event)
                    
                    # Parse statuses (delivery, read receipts, etc.)
                    statuses = value.get("statuses", [])
                    for status in statuses:
                        event = self._parse_status(status)
                        if event:
                            events.append(event)
        
        except Exception as e:
            logger.error(f"Error parsing Cloud API webhook: {e}", exc_info=True)
        
        logger.info(f"Parsed {len(events)} events from Cloud API webhook")
        return events

    def _parse_message(self, message: Dict[str, Any]) -> Optional[EngineEvent]:
        """Parse a message object into an EngineEvent."""
        try:
            message_id = message.get("id")
            from_number = message.get("from")
            timestamp_str = message.get("timestamp", str(int(datetime.now().timestamp())))
            timestamp = datetime.fromtimestamp(int(timestamp_str))
            
            message_type = message.get("type")
            
            # Text message
            if message_type == "text":
                text = message.get("text", {}).get("body", "")
                return EngineEvent(
                    event_type=EventType.MESSAGE_RECEIVED,
                    timestamp=timestamp,
                    from_number=from_number,
                    message_id=message_id,
                    text=text,
                )
            
            # Button reply
            if message_type == "button":
                button_payload = message.get("button", {}).get("payload")
                button_text = message.get("button", {}).get("text")
                return EngineEvent(
                    event_type=EventType.BUTTON_CLICKED,
                    timestamp=timestamp,
                    from_number=from_number,
                    message_id=message_id,
                    button_id=button_payload,
                    text=button_text,
                )
            
            # Interactive list reply
            if message_type == "interactive":
                interactive = message.get("interactive", {})
                if interactive.get("type") == "list_reply":
                    list_reply = interactive.get("list_reply", {})
                    list_item_id = list_reply.get("id")
                    list_item_title = list_reply.get("title")
                    return EngineEvent(
                        event_type=EventType.LIST_SELECTED,
                        timestamp=timestamp,
                        from_number=from_number,
                        message_id=message_id,
                        list_item_id=list_item_id,
                        text=list_item_title,
                    )
            
            # Media messages
            if message_type in ["image", "video", "document", "audio", "voice", "sticker"]:
                media_obj = message.get(message_type, {})
                media_id = media_obj.get("id")
                media_url = media_obj.get("url")  # May not be present
                caption = media_obj.get("caption")
                
                return EngineEvent(
                    event_type=EventType.MESSAGE_RECEIVED,
                    timestamp=timestamp,
                    from_number=from_number,
                    message_id=message_id,
                    text=caption,
                    media_url=media_url,
                    metadata={"media_id": media_id, "media_type": message_type},
                )
            
            # Location message
            if message_type == "location":
                location = message.get("location", {})
                return EngineEvent(
                    event_type=EventType.MESSAGE_RECEIVED,
                    timestamp=timestamp,
                    from_number=from_number,
                    message_id=message_id,
                    metadata={"location": location},
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error parsing message: {e}", exc_info=True)
            return None

    def _parse_status(self, status: Dict[str, Any]) -> Optional[EngineEvent]:
        """Parse a status update into an EngineEvent."""
        try:
            message_id = status.get("id")
            status_type = status.get("status")
            timestamp_str = status.get("timestamp", str(int(datetime.now().timestamp())))
            timestamp = datetime.fromtimestamp(int(timestamp_str))
            recipient = status.get("recipient_id", "")
            
            event_type_map = {
                "sent": None,  # Ignore sent status
                "delivered": EventType.MESSAGE_DELIVERED,
                "read": EventType.MESSAGE_READ,
                "failed": EventType.MESSAGE_FAILED,
            }
            
            event_type = event_type_map.get(status_type)
            if event_type:
                metadata = {}
                
                # Include error information if failed
                if status_type == "failed":
                    errors = status.get("errors", [])
                    if errors:
                        metadata["errors"] = errors
                
                return EngineEvent(
                    event_type=event_type,
                    timestamp=timestamp,
                    from_number=recipient,
                    message_id=message_id,
                    metadata=metadata if metadata else None,
                )
            
            return None
        
        except Exception as e:
            logger.error(f"Error parsing status: {e}", exc_info=True)
            return None
