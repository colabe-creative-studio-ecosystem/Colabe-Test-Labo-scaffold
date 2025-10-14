import reflex as rx
from app.core.settings import settings
import redis
from rq import Queue
from app.orchestrator.job_runner import run_test_plan


def health_check_task():
    return "Celery is alive!"


redis_conn = redis.from_url(settings.REDIS_URL)
task_queue = Queue("default", connection=redis_conn, default_timeout=3600)


def enqueue_health_check():
    job = task_queue.enqueue(health_check_task)
    return job.get_id()


def enqueue_test_run(run_id: int, tenant_id: int):
    """Enqueues a test plan run task."""
    job = task_queue.enqueue(run_test_plan, run_id, tenant_id)
    return job.get_id()