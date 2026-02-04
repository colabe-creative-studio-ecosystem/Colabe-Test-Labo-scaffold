import reflex as rx
from app.core.settings import settings
import redis
from rq import Queue
import logging

logger = logging.getLogger(__name__)


def health_check_task():
    return "Celery is alive!"


def send_outbound_message_task(
    message_id: int,
    recipient_email: str,
    message_content: str,
    message_type: str,
):
    """
    Task to send an outbound message.
    
    This is a placeholder implementation. In production, you would:
    - Integrate with an email service (SendGrid, AWS SES, etc.)
    - Handle actual message sending
    - Return success/failure status
    """
    from app.orchestrator.message_dispatcher import MessageDispatcher
    from sqlmodel import Session, create_engine
    
    logger.info(
        f"Sending message {message_id} to {recipient_email} "
        f"(type: {message_type})"
    )
    
    try:
        # Simulate message sending
        # In production, replace with actual email service integration
        # Example:
        # response = sendgrid_client.send(to=recipient_email, content=message_content)
        
        # For now, just log success
        logger.info(f"Message {message_id} sent successfully (simulated)")
        
        # Update message status in database
        engine = create_engine(settings.DATABASE_URL)
        with Session(engine) as session:
            dispatcher = MessageDispatcher(session)
            dispatcher.record_message_success(message_id)
        
        return {"status": "success", "message_id": message_id}
        
    except Exception as e:
        logger.exception(f"Failed to send message {message_id}: {e}")
        
        # Record failure
        engine = create_engine(settings.DATABASE_URL)
        with Session(engine) as session:
            dispatcher = MessageDispatcher(session)
            dispatcher.record_message_failure(message_id, str(e))
        
        return {"status": "failure", "message_id": message_id, "error": str(e)}


try:
    redis_conn = redis.from_url(settings.REDIS_URL)
    task_queue = Queue("default", connection=redis_conn)
except Exception as e:
    logger.exception(f"Redis/Queue initialization failed: {e}")
    redis_conn = None
    task_queue = None


def enqueue_health_check():
    if not task_queue:
        logger.warning("Task queue is not available.")
        return None
    try:
        job = task_queue.enqueue(health_check_task)
        return job.get_id()
    except (redis.exceptions.ConnectionError, redis.exceptions.RedisError) as e:
        logger.exception(f"Redis connection failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"Failed to enqueue health check: {e}")
        return None


def enqueue_outbound_message(
    message_id: int,
    recipient_email: str,
    message_content: str,
    message_type: str,
) -> str | None:
    """
    Enqueue an outbound message for sending.
    
    Returns:
        Job ID if enqueued successfully, None otherwise
    """
    if not task_queue:
        logger.warning("Task queue is not available.")
        return None
    
    try:
        job = task_queue.enqueue(
            send_outbound_message_task,
            message_id,
            recipient_email,
            message_content,
            message_type,
        )
        return job.get_id()
    except (redis.exceptions.ConnectionError, redis.exceptions.RedisError) as e:
        logger.exception(f"Redis connection failed: {e}")
        return None
    except Exception as e:
        logger.exception(f"Failed to enqueue outbound message: {e}")
        return None