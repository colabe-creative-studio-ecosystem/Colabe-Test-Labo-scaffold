import reflex as rx
from app.core.settings import settings
import redis
from rq import Queue


def health_check_task():
    return "Celery is alive!"


redis_conn = redis.from_url(settings.REDIS_URL)
task_queue = Queue("default", connection=redis_conn)


def enqueue_health_check():
    job = task_queue.enqueue(health_check_task)
    return job.get_id()