import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)


class WebhookVerifier:
    """Verifies webhook signatures using HMAC-SHA256."""

    def __init__(self, secret: str):
        """
        Initialize the verifier with a webhook secret.
        
        Args:
            secret: The webhook secret key used for signature verification
        """
        if not secret:
            raise ValueError("Webhook secret cannot be empty")
        self.secret = secret.encode('utf-8')

    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """
        Verify the webhook signature.
        
        Args:
            payload: The raw webhook payload as bytes
            signature: The signature from the webhook header
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not signature:
            logger.warning("Missing signature in webhook request")
            return False
        
        try:
            # Remove 'sha256=' prefix if present
            if signature.startswith('sha256='):
                signature = signature[7:]
            
            # Compute expected signature
            expected_signature = hmac.new(
                self.secret,
                payload,
                hashlib.sha256
            ).hexdigest()
            
            # Use constant-time comparison to prevent timing attacks
            return hmac.compare_digest(expected_signature, signature)
        except Exception as e:
            logger.exception(f"Error verifying signature: {e}")
            return False
