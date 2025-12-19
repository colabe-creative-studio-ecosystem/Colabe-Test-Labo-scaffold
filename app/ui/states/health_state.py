import reflex as rx
import logging
import asyncio
from sqlalchemy import text
from app.orchestrator.tasks import enqueue_health_check


class HealthState(rx.State):
    health_status: str = "Checking..."
    db_status: str = "Unknown"
    redis_status: str = "Unknown"
    worker_status: str = "Unknown"
    job_id: str = ""

    @rx.event
    def check_health(self):
        try:
            with rx.session() as session:
                session.exec(text("SELECT 1"))
            self.db_status = "OK"
        except Exception as e:
            logging.exception(e)
            self.db_status = "Error"
        try:
            import redis
            from app.core.settings import settings

            r = redis.from_url(settings.REDIS_URL)
            r.ping()
            self.redis_status = "OK"
        except Exception as e:
            logging.exception(e)
            self.redis_status = "Error"
        job_id = enqueue_health_check()
        if job_id:
            self.job_id = job_id
            self.worker_status = "Job Enqueued"
        else:
            self.job_id = ""
            if self.redis_status == "Error":
                self.worker_status = "Redis Unavailable"
            else:
                self.worker_status = "Enqueue Failed"
        if self.db_status == "OK" and self.redis_status == "OK":
            self.health_status = "OK"
        else:
            self.health_status = "Degraded"
        if self.job_id:
            return HealthState.check_job_status

    @rx.event(background=True)
    async def check_job_status(self):
        import time
        from rq.job import Job
        from app.orchestrator.tasks import redis_conn

        if not self.job_id:
            return
        for _ in range(10):
            job = Job.fetch(self.job_id, connection=redis_conn)
            if job.is_finished:
                async with self:
                    self.worker_status = f"OK ({job.result})"
                return
            elif job.is_failed:
                async with self:
                    self.worker_status = "Job Failed"
                return
            await asyncio.sleep(1)
        async with self:
            self.worker_status = "Job Timed Out"