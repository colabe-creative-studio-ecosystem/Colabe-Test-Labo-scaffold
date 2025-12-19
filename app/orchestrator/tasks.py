import reflex as rx
from app.core.settings import settings
import redis
from rq import Queue
import logging

logger = logging.getLogger(__name__)


def health_check_task():
    return "Celery is alive!"


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