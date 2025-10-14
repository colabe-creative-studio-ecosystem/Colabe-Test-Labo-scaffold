import reflex as rx
import logging
from app.orchestrator.models import StepContext, StepResult
from app.adapters.python import PythonAdapter
from app.adapters.base import Adapter
import time
from app.core.models import Run, RunStep, RunStatus, RunStepStatus, Tenant
import datetime

logger = logging.getLogger(__name__)
DAG_STEPS = [
    "discover",
    "static",
    "unit",
    "integration",
    "e2e",
    "perf",
    "a11y",
    "security",
    "coverage",
    "sbom",
    "summarize",
]


def get_adapter_for_project(project_id: int) -> Adapter | None:
    return PythonAdapter()


def run_test_plan(run_id: int, tenant_id: int):
    """The main background task for running a test plan DAG."""
    logger.info(f"Starting test plan run_id={run_id} for tenant_id={tenant_id}")
    with rx.session() as session:
        run = session.get(Run, run_id)
        if not run:
            logger.error(f"Run with id {run_id} not found.")
            return
        run.status = RunStatus.RUNNING
        run.started_at = datetime.datetime.now(datetime.UTC)
        for step_name in DAG_STEPS:
            run_step = RunStep(run_id=run.id, name=step_name)
            session.add(run_step)
        session.commit()
        session.refresh(run)
    adapter = get_adapter_for_project(run.test_plan_id)
    if not adapter:
        _fail_run(run_id, "No suitable adapter found for the project.")
        return
    ctx = StepContext(
        tenant_id=tenant_id, project_id=run.test_plan_id, run_id=run_id, repo_path="."
    )
    for step in run.steps:
        _update_step_status(step.id, RunStepStatus.RUNNING)
        try:
            adapter_method = getattr(adapter, step.name, None)
            if adapter_method:
                logger.info(f"Executing step '{step.name}' for run_id={run_id}")
                result: StepResult = adapter_method(ctx)
                if result.status == "failed":
                    logger.warning(
                        f"Step '{step.name}' failed for run_id={run_id}. Halting execution."
                    )
                    _update_step_status(step.id, RunStepStatus.FAILED)
                    _fail_run(run_id, f"Step '{step.name}' failed.")
                    return
                else:
                    _update_step_status(step.id, RunStepStatus.COMPLETED)
            else:
                logger.info(
                    f"Skipping undefined step '{step.name}' for run_id={run_id}"
                )
                _update_step_status(step.id, RunStepStatus.SKIPPED)
        except Exception as e:
            logger.exception(
                f"An unexpected error occurred during step '{step.name}' for run_id={run_id}: {e}"
            )
            _update_step_status(step.id, RunStepStatus.FAILED)
            _fail_run(run_id, f"Error in step '{step.name}'.")
            return
    _complete_run(run_id)


def _update_step_status(step_id: int, status: RunStepStatus):
    with rx.session() as session:
        step = session.get(RunStep, step_id)
        if step:
            step.status = status
            if status == RunStepStatus.RUNNING:
                step.started_at = datetime.datetime.now(datetime.UTC)
            elif status in [
                RunStepStatus.COMPLETED,
                RunStepStatus.FAILED,
                RunStepStatus.SKIPPED,
            ]:
                step.completed_at = datetime.datetime.now(datetime.UTC)
            session.add(step)
            session.commit()


def _fail_run(run_id: int, reason: str):
    logger.error(f"Failing run_id={run_id}. Reason: {reason}")
    with rx.session() as session:
        run = session.get(Run, run_id)
        if run:
            run.status = RunStatus.FAILED
            run.completed_at = datetime.datetime.now(datetime.UTC)
            session.add(run)
            session.commit()


def _complete_run(run_id: int):
    logger.info(f"Completing run_id={run_id} successfully.")
    with rx.session() as session:
        run = session.get(Run, run_id)
        if run:
            run.status = RunStatus.COMPLETED
            run.completed_at = datetime.datetime.now(datetime.UTC)
            session.add(run)
            session.commit()