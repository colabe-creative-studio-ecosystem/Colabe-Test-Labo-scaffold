"""
Tests for the message dispatcher guardrails.
"""
import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel, select
from app.orchestrator.message_dispatcher import (
    MessageDispatcher,
    MessageDispatcherConfig,
    GuardrailViolation,
)
from app.core.models import (
    Tenant,
    User,
    OutboundMessage,
    ConversationRateLimit,
    ContactCooldown,
    WorkspaceQuietHours,
    CircuitBreakerState,
)


@pytest.fixture
def db_session():
    """Create an in-memory database for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        # Create test tenant
        tenant = Tenant(name="test_tenant")
        session.add(tenant)
        session.commit()
        session.refresh(tenant)
        
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="test_hash",
            tenant_id=tenant.id,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        
        yield session


def test_can_send_message_no_restrictions(db_session):
    """Test that messages can be sent when no restrictions are in place."""
    dispatcher = MessageDispatcher(db_session)
    tenant = db_session.exec(select(Tenant)).first()
    tenant_id = tenant.id
    
    can_send, reason, fix = dispatcher.can_send_message(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
        conversation_id="conv-123",
    )
    
    assert can_send is True
    assert reason is None
    assert fix is None


def test_conversation_rate_limit(db_session):
    """Test that conversation rate limiting works."""
    config = MessageDispatcherConfig()
    config.MAX_MESSAGES_PER_CONVERSATION_WINDOW = 2
    config.CONVERSATION_WINDOW_SECONDS = 60
    config.DEFAULT_CONTACT_COOLDOWN_SECONDS = 0  # Disable cooldown for this test
    
    dispatcher = MessageDispatcher(db_session, config)
    tenant = db_session.exec(select(Tenant)).first()
    tenant_id = tenant.id
    conversation_id = "conv-123"
    
    # First message - should pass
    can_send, _, _ = dispatcher.can_send_message(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
        conversation_id=conversation_id,
    )
    assert can_send is True
    
    # Record the message
    msg = dispatcher.record_message_attempt(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
        message_type="test",
        conversation_id=conversation_id,
        status="sent",
    )
    
    # Second message - should pass
    can_send, _, _ = dispatcher.can_send_message(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
        conversation_id=conversation_id,
    )
    assert can_send is True
    
    # Record the second message
    msg2 = dispatcher.record_message_attempt(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
        message_type="test",
        conversation_id=conversation_id,
        status="sent",
    )
    
    # Third message - should fail due to rate limit
    can_send, reason, fix = dispatcher.can_send_message(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
        conversation_id=conversation_id,
    )
    assert can_send is False
    assert "rate limit exceeded" in reason.lower()
    assert fix is not None


def test_contact_cooldown(db_session):
    """Test that contact cooldown works."""
    config = MessageDispatcherConfig()
    config.DEFAULT_CONTACT_COOLDOWN_SECONDS = 10
    
    dispatcher = MessageDispatcher(db_session, config)
    tenant = db_session.exec(select(Tenant)).first()
    tenant_id = tenant.id
    recipient = "test@example.com"
    
    # Create cooldown manually
    cooldown = ContactCooldown(
        contact_email=recipient,
        tenant_id=tenant_id,
        last_message_sent_at=datetime.now(),
        cooldown_until=datetime.now() + timedelta(seconds=100),
    )
    db_session.add(cooldown)
    db_session.commit()
    
    # Try to send - should fail
    can_send, reason, fix = dispatcher.can_send_message(
        tenant_id=tenant_id,
        recipient_email=recipient,
    )
    assert can_send is False
    assert "cooldown" in reason.lower()
    assert fix is not None


def test_circuit_breaker_opens_after_failures(db_session):
    """Test that circuit breaker opens after threshold failures."""
    config = MessageDispatcherConfig()
    config.CIRCUIT_BREAKER_FAILURE_THRESHOLD = 3
    
    dispatcher = MessageDispatcher(db_session, config)
    tenant = db_session.exec(select(Tenant)).first()
    tenant_id = tenant.id
    
    # Record failures
    for i in range(3):
        msg = dispatcher.record_message_attempt(
            tenant_id=tenant_id,
            recipient_email=f"test{i}@example.com",
            message_type="test",
            status="pending",
        )
        dispatcher.record_message_failure(msg.id, "Test failure")
    
    # Circuit should now be open
    can_send, reason, fix = dispatcher.can_send_message(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
    )
    assert can_send is False
    assert "circuit breaker" in reason.lower()
    assert "open" in reason.lower()


def test_quiet_hours_blocking(db_session):
    """Test that quiet hours block messages."""
    dispatcher = MessageDispatcher(db_session)
    tenant = db_session.exec(select(Tenant)).first()
    tenant_id = tenant.id
    
    # Set up quiet hours for current time
    current_hour = datetime.now().hour
    quiet_hours = WorkspaceQuietHours(
        tenant_id=tenant_id,
        enabled=True,
        start_hour=current_hour,
        end_hour=(current_hour + 1) % 24,
        timezone="UTC",
    )
    db_session.add(quiet_hours)
    db_session.commit()
    
    # Try to send - should fail
    can_send, reason, fix = dispatcher.can_send_message(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
    )
    assert can_send is False
    assert "quiet hours" in reason.lower()
    assert fix is not None


def test_message_success_resets_circuit_breaker(db_session):
    """Test that successful message in half_open state closes circuit."""
    dispatcher = MessageDispatcher(db_session)
    tenant = db_session.exec(select(Tenant)).first()
    tenant_id = tenant.id
    
    # Create circuit breaker in half_open state
    circuit = CircuitBreakerState(
        tenant_id=tenant_id,
        state="half_open",
        failure_count=5,
        window_start=datetime.now(),
    )
    db_session.add(circuit)
    db_session.commit()
    
    # Record a successful message
    msg = dispatcher.record_message_attempt(
        tenant_id=tenant_id,
        recipient_email="test@example.com",
        message_type="test",
        status="pending",
    )
    dispatcher.record_message_success(msg.id)
    
    # Check that circuit is now closed
    db_session.refresh(circuit)
    assert circuit.state == "closed"
    assert circuit.failure_count == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
