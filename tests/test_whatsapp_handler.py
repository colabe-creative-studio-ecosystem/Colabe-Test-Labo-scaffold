"""Tests for WhatsApp webhook handler production safety features"""
import pytest
import json
from datetime import datetime, date
from unittest.mock import Mock, patch, AsyncMock
from starlette.requests import Request
from app.integrations.whatsapp_handler import (
    whatsapp_webhook,
    extract_message_id,
    is_duplicate_event,
    process_webhook_event,
    record_processed_event,
    log_to_dead_letter,
    increment_metric,
    is_circuit_breaker_open,
    increment_circuit_breaker_failure,
    reset_circuit_breaker,
    circuit_breaker_state,
    CIRCUIT_BREAKER_THRESHOLD,
    MAX_RETRIES
)


@pytest.fixture
def sample_whatsapp_payload():
    """Sample WhatsApp webhook payload"""
    return {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "id": "wamid.test123456",
                                    "from": "1234567890",
                                    "timestamp": "1234567890",
                                    "text": {
                                        "body": "Hello, World!"
                                    }
                                }
                            ]
                        }
                    }
                ]
            }
        ],
        "type": "message"
    }


@pytest.fixture
def mock_request(sample_whatsapp_payload):
    """Create a mock Starlette request"""
    request = Mock(spec=Request)
    payload = json.dumps(sample_whatsapp_payload).encode('utf-8')
    request.body = AsyncMock(return_value=payload)
    request.headers = {}
    return request


class TestMessageIdExtraction:
    """Test message ID extraction from webhook payload"""
    
    def test_extract_message_id_success(self, sample_whatsapp_payload):
        """Should extract message ID from valid WhatsApp payload"""
        message_id = extract_message_id(sample_whatsapp_payload)
        assert message_id == "wamid.test123456"
    
    def test_extract_message_id_fallback(self):
        """Should use fallback ID field if main path fails"""
        payload = {"id": "fallback_id_123"}
        message_id = extract_message_id(payload)
        assert message_id == "fallback_id_123"
    
    def test_extract_message_id_missing(self):
        """Should return None if no message ID found"""
        payload = {"entry": []}
        message_id = extract_message_id(payload)
        assert message_id is None


class TestIdempotency:
    """Test idempotency checks"""
    
    @pytest.mark.asyncio
    async def test_duplicate_detection(self):
        """Should detect duplicate message IDs"""
        message_id = "wamid.duplicate_test"
        
        # First processing - not a duplicate
        with patch('app.integrations.whatsapp_handler.rx.session') as mock_session:
            mock_db = Mock()
            mock_db.exec.return_value.first.return_value = None
            mock_session.return_value.__enter__.return_value = mock_db
            
            is_dup = await is_duplicate_event(message_id)
            assert is_dup is False
        
        # Second processing - is a duplicate
        with patch('app.integrations.whatsapp_handler.rx.session') as mock_session:
            mock_db = Mock()
            mock_event = Mock()
            mock_db.exec.return_value.first.return_value = mock_event
            mock_session.return_value.__enter__.return_value = mock_db
            
            is_dup = await is_duplicate_event(message_id)
            assert is_dup is True


class TestRetryLogic:
    """Test retry policy with exponential backoff"""
    
    @pytest.mark.asyncio
    async def test_retry_with_backoff(self):
        """Should retry failed events with exponential backoff"""
        message_id = "wamid.retry_test"
        event_type = "message"
        payload = json.dumps({"test": "data"})
        
        # Mock the processing to fail multiple times then succeed
        call_count = 0
        
        async def mock_process_side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Simulated failure")
            return True
        
        with patch('app.integrations.whatsapp_handler.record_processed_event') as mock_record:
            with patch('asyncio.sleep') as mock_sleep:
                result = await process_webhook_event(
                    message_id, event_type, payload, retry_count=0
                )
        
        # Should have succeeded after retries
        assert call_count > 1
    
    @pytest.mark.asyncio
    async def test_max_retries_reached(self):
        """Should log to dead letter after max retries"""
        message_id = "wamid.max_retry_test"
        event_type = "message"
        payload = json.dumps({"test": "data"})
        
        with patch('app.integrations.whatsapp_handler.log_to_dead_letter') as mock_dead_letter:
            with patch('app.integrations.whatsapp_handler.increment_metric'):
                with patch('asyncio.sleep'):
                    # Start with retry count at max
                    result = await process_webhook_event(
                        message_id, event_type, payload, retry_count=MAX_RETRIES
                    )
        
        assert result is False
        mock_dead_letter.assert_called_once()


class TestDeadLetterLogging:
    """Test dead-letter logging for failed events"""
    
    @pytest.mark.asyncio
    async def test_log_to_dead_letter(self):
        """Should log failed events to dead letter table"""
        message_id = "wamid.failed_test"
        event_type = "message"
        payload = json.dumps({"test": "data"})
        error_msg = "Test error"
        retry_count = 3
        
        with patch('app.integrations.whatsapp_handler.rx.session') as mock_session:
            mock_db = Mock()
            mock_session.return_value.__enter__.return_value = mock_db
            
            await log_to_dead_letter(
                message_id, event_type, payload, error_msg, retry_count
            )
            
            mock_db.add.assert_called_once()
            mock_db.commit.assert_called_once()


class TestMonitoringCounters:
    """Test monitoring counter increments"""
    
    @pytest.mark.asyncio
    async def test_increment_inbound_events(self):
        """Should increment inbound events counter"""
        with patch('app.integrations.whatsapp_handler.rx.session') as mock_session:
            mock_db = Mock()
            mock_metric = Mock()
            mock_metric.inbound_events = 0
            mock_db.exec.return_value.first.return_value = mock_metric
            mock_session.return_value.__enter__.return_value = mock_db
            
            await increment_metric("inbound_events")
            
            assert mock_metric.inbound_events == 1
            mock_db.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_increment_failures(self):
        """Should increment failures counter"""
        with patch('app.integrations.whatsapp_handler.rx.session') as mock_session:
            mock_db = Mock()
            mock_metric = Mock()
            mock_metric.failures = 0
            mock_db.exec.return_value.first.return_value = mock_metric
            mock_session.return_value.__enter__.return_value = mock_db
            
            await increment_metric("failures")
            
            assert mock_metric.failures == 1
    
    @pytest.mark.asyncio
    async def test_increment_circuit_breaker_trips(self):
        """Should increment circuit breaker trips counter"""
        with patch('app.integrations.whatsapp_handler.rx.session') as mock_session:
            mock_db = Mock()
            mock_metric = Mock()
            mock_metric.circuit_breaker_trips = 0
            mock_db.exec.return_value.first.return_value = mock_metric
            mock_session.return_value.__enter__.return_value = mock_db
            
            await increment_metric("circuit_breaker_trips")
            
            assert mock_metric.circuit_breaker_trips == 1


class TestCircuitBreaker:
    """Test circuit breaker pattern"""
    
    def setup_method(self):
        """Reset circuit breaker state before each test"""
        circuit_breaker_state["is_open"] = False
        circuit_breaker_state["failure_count"] = 0
        circuit_breaker_state["last_failure_time"] = None
    
    def test_circuit_breaker_opens_on_threshold(self):
        """Should open circuit breaker after threshold failures"""
        for i in range(CIRCUIT_BREAKER_THRESHOLD):
            increment_circuit_breaker_failure()
        
        assert circuit_breaker_state["is_open"] is True
        assert circuit_breaker_state["failure_count"] == CIRCUIT_BREAKER_THRESHOLD
    
    def test_circuit_breaker_stays_closed_below_threshold(self):
        """Should keep circuit closed below failure threshold"""
        for i in range(CIRCUIT_BREAKER_THRESHOLD - 1):
            increment_circuit_breaker_failure()
        
        assert circuit_breaker_state["is_open"] is False
    
    def test_circuit_breaker_reset_on_success(self):
        """Should reset circuit breaker on successful processing"""
        # Add some failures
        for i in range(3):
            increment_circuit_breaker_failure()
        
        # Then succeed
        reset_circuit_breaker()
        
        assert circuit_breaker_state["is_open"] is False
        assert circuit_breaker_state["failure_count"] == 0
        assert circuit_breaker_state["last_failure_time"] is None
    
    def test_circuit_breaker_rejects_when_open(self):
        """Should reject requests when circuit breaker is open"""
        circuit_breaker_state["is_open"] = True
        circuit_breaker_state["last_failure_time"] = datetime.now()
        
        assert is_circuit_breaker_open() is True


class TestWebhookEndpoint:
    """Test the main webhook endpoint"""
    
    @pytest.mark.asyncio
    async def test_webhook_success(self, mock_request):
        """Should successfully process valid webhook"""
        with patch('app.integrations.whatsapp_handler.is_duplicate_event', return_value=False):
            with patch('app.integrations.whatsapp_handler.process_webhook_event', return_value=True):
                with patch('app.integrations.whatsapp_handler.increment_metric'):
                    with patch('app.integrations.whatsapp_handler.is_circuit_breaker_open', return_value=False):
                        response = await whatsapp_webhook(mock_request)
        
        assert response.status_code == 200
        response_data = json.loads(response.body)
        assert response_data["status"] == "success"
    
    @pytest.mark.asyncio
    async def test_webhook_duplicate(self, mock_request):
        """Should handle duplicate messages gracefully"""
        with patch('app.integrations.whatsapp_handler.is_duplicate_event', return_value=True):
            with patch('app.integrations.whatsapp_handler.increment_metric'):
                with patch('app.integrations.whatsapp_handler.is_circuit_breaker_open', return_value=False):
                    response = await whatsapp_webhook(mock_request)
        
        assert response.status_code == 200
        response_data = json.loads(response.body)
        assert response_data["status"] == "duplicate"
    
    @pytest.mark.asyncio
    async def test_webhook_circuit_breaker_open(self, mock_request):
        """Should reject requests when circuit breaker is open"""
        with patch('app.integrations.whatsapp_handler.is_circuit_breaker_open', return_value=True):
            with patch('app.integrations.whatsapp_handler.increment_metric'):
                response = await whatsapp_webhook(mock_request)
        
        assert response.status_code == 503
        response_data = json.loads(response.body)
        assert "unavailable" in response_data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_webhook_invalid_json(self):
        """Should reject invalid JSON payloads"""
        request = Mock(spec=Request)
        request.body = AsyncMock(return_value=b"invalid json{")
        request.headers = {}
        
        response = await whatsapp_webhook(request)
        
        assert response.status_code == 400
        response_data = json.loads(response.body)
        assert "Invalid JSON" in response_data["detail"]
    
    @pytest.mark.asyncio
    async def test_webhook_missing_message_id(self):
        """Should reject payloads without message ID"""
        request = Mock(spec=Request)
        payload = json.dumps({"type": "message", "entry": []})
        request.body = AsyncMock(return_value=payload.encode('utf-8'))
        request.headers = {}
        
        response = await whatsapp_webhook(request)
        
        assert response.status_code == 400
        response_data = json.loads(response.body)
        assert "Missing message ID" in response_data["detail"]
