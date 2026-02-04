import reflex as rx
import sqlmodel
from sqlalchemy.orm import selectinload
from datetime import datetime
from app.core.models import Run, TestPlan, Project
from app.ui.states.auth_state import AuthState
from app.ui.utils import get_logger, notify_error, notify_success

logger = get_logger(__name__)


class RunProjectDisplay(rx.Base):
    """Display model for project information in runs."""
    name: str


class RunPlanDisplay(rx.Base):
    """Display model for test plan information in runs."""
    name: str
    project: RunProjectDisplay | None = None


class RunDisplay(rx.Base):
    """Display model for test run information."""
    id: int
    status: str
    started_at: str | None = None
    test_plan: RunPlanDisplay | None = None


class RunState(rx.State):
    """
    Test run management state.
    
    Handles viewing, triggering, and managing test execution runs.
    """
    runs: list[RunDisplay] = []

    @rx.event
    async def load_data(self):
        """Load all runs for the current tenant."""
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                logger.warning("Attempted to load runs without authentication")
                return
                
            with rx.session() as session:
                runs = session.exec(
                    sqlmodel.select(Run)
                    .join(TestPlan)
                    .join(Project)
                    .where(Project.tenant_id == auth_state.user.tenant_id)
                    .order_by(sqlmodel.desc(Run.created_at))
                    .options(selectinload(Run.test_plan).selectinload(TestPlan.project))
                ).all()
                
                self.runs = [
                    RunDisplay(
                        id=r.id,
                        status=r.status,
                        started_at=r.started_at.isoformat() if r.started_at else None,
                        test_plan=RunPlanDisplay(
                            name=r.test_plan.name,
                            project=RunProjectDisplay(name=r.test_plan.project.name)
                            if r.test_plan.project
                            else None,
                        )
                        if r.test_plan
                        else None,
                    )
                    for r in runs
                ]
                logger.info(f"Loaded {len(self.runs)} runs")
                
        except Exception as e:
            logger.exception(f"Error loading runs: {str(e)}")
            return notify_error("Failed to load runs.")

    @rx.event
    async def trigger_run(self, plan_id: int):
        """
        Trigger a new test run for a test plan.
        
        Args:
            plan_id: ID of the test plan to run
        """
        try:
            with rx.session() as session:
                run = Run(test_plan_id=plan_id, status="running", started_at=datetime.now())
                session.add(run)
                session.commit()
                logger.info(f"Triggered new run for test plan {plan_id}")
                
            await self.load_data()
            return notify_success("Run triggered successfully.")
            
        except Exception as e:
            logger.exception(f"Error triggering run for plan {plan_id}: {str(e)}")
            return notify_error("Failed to trigger run.")

    @rx.event
    async def delete_run(self, run_id: int):
        """
        Delete a test run.
        
        Args:
            run_id: ID of the run to delete
        """
        try:
            with rx.session() as session:
                run = session.get(Run, run_id)
                if run:
                    session.delete(run)
                    session.commit()
                    logger.info(f"Deleted run {run_id}")
                else:
                    logger.warning(f"Attempted to delete non-existent run {run_id}")
                    
            await self.load_data()
            return notify_success("Run deleted.")
            
        except Exception as e:
            logger.exception(f"Error deleting run {run_id}: {str(e)}")
            return notify_error("Failed to delete run.")