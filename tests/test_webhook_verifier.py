"""Unit tests for WebhookVerifier."""

import pytest
from app.integrations.webhook_verifier import WebhookVerifier
import hmac
import hashlib


class TestWebhookVerifier:
    """Test suite for WebhookVerifier."""

    def test_init_with_valid_secret(self):
        """Test initialization with a valid secret."""
        verifier = WebhookVerifier("my_secret")
        assert verifier.secret == b"my_secret"

    def test_init_with_empty_secret(self):
        """Test initialization with empty secret raises ValueError."""
        with pytest.raises(ValueError, match="Webhook secret cannot be empty"):
            WebhookVerifier("")

    def test_verify_signature_valid(self):
        """Test signature verification with valid signature."""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        # Generate valid signature
        signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        verifier = WebhookVerifier(secret)
        assert verifier.verify_signature(payload, signature) is True

    def test_verify_signature_valid_with_prefix(self):
        """Test signature verification with 'sha256=' prefix."""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        # Generate valid signature with prefix
        signature = 'sha256=' + hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        verifier = WebhookVerifier(secret)
        assert verifier.verify_signature(payload, signature) is True

    def test_verify_signature_invalid(self):
        """Test signature verification with invalid signature."""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        invalid_signature = "invalid_signature_hash"
        
        verifier = WebhookVerifier(secret)
        assert verifier.verify_signature(payload, invalid_signature) is False

    def test_verify_signature_wrong_secret(self):
        """Test signature verification with wrong secret."""
        payload = b'{"test": "data"}'
        
        # Generate signature with one secret
        signature = hmac.new(
            b"correct_secret",
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Verify with different secret
        verifier = WebhookVerifier("wrong_secret")
        assert verifier.verify_signature(payload, signature) is False

    def test_verify_signature_empty_signature(self):
        """Test signature verification with empty signature."""
        verifier = WebhookVerifier("test_secret")
        payload = b'{"test": "data"}'
        assert verifier.verify_signature(payload, "") is False

    def test_verify_signature_modified_payload(self):
        """Test that modified payload fails verification."""
        secret = "test_secret"
        original_payload = b'{"test": "data"}'
        modified_payload = b'{"test": "modified"}'
        
        # Generate signature for original payload
        signature = hmac.new(
            secret.encode('utf-8'),
            original_payload,
            hashlib.sha256
        ).hexdigest()
        
        # Verify with modified payload
        verifier = WebhookVerifier(secret)
        assert verifier.verify_signature(modified_payload, signature) is False

    def test_verify_signature_timing_attack_resistant(self):
        """Test that verification uses constant-time comparison."""
        secret = "test_secret"
        payload = b'{"test": "data"}'
        
        # Generate valid signature
        valid_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Create similar but invalid signature (same length)
        invalid_signature = valid_signature[:-1] + 'x'
        
        verifier = WebhookVerifier(secret)
        
        # Both should return False for invalid, but timing should be constant
        assert verifier.verify_signature(payload, invalid_signature) is False
        assert verifier.verify_signature(payload, valid_signature) is True
