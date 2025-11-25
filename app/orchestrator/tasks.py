"""Background task helpers for the orchestration layer."""

import redis
from rq import Queue
from rq.exceptions import NoSuchJobError
from rq.job import Job

from app.core.settings import settings


def health_check_task():
    """Simple worker heartbeat task used by the health check page."""

    return "Worker is responsive"


redis_conn = redis.from_url(settings.REDIS_URL)
task_queue = Queue("default", connection=redis_conn)


def enqueue_health_check():
    """Queue a health check job and return its id."""

    job = task_queue.enqueue(health_check_task)
    return job.get_id()


def fetch_job(job_id: str) -> Job | None:
    """Safely fetch a job by id.

    Args:
        job_id: The RQ job identifier.

    Returns:
        The corresponding ``Job`` or ``None`` if it no longer exists.
    """

    try:
        return Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        return None