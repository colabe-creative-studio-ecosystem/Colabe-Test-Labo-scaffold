import reflex as rx
import sqlmodel
from sqlalchemy.orm import selectinload
from app.core.models import TestPlan, Project
from app.ui.states.auth_state import AuthState
from app.ui.utils import get_logger, notify_error, notify_success, notify_warning

logger = get_logger(__name__)


class TestPlanProjectDisplay(rx.Base):
    """Display model for project information in test plans."""
    name: str


class TestPlanDisplay(rx.Base):
    """Display model for test plan information."""
    id: int
    name: str
    created_at: str
    project: TestPlanProjectDisplay | None = None


class TestPlanState(rx.State):
    """
    Test plan management state.
    
    Handles creation, viewing, and deletion of test plans.
    """
    test_plans: list[TestPlanDisplay] = []
    new_plan_name: str = ""
    selected_project_id: str = ""
    projects: list[Project] = []

    @rx.event
    async def load_data(self):
        """Load test plans and projects for the current tenant."""
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                logger.warning("Attempted to load test plans without authentication")
                return
                
            with rx.session() as session:
                self.projects = session.exec(
                    sqlmodel.select(Project).where(
                        Project.tenant_id == auth_state.user.tenant_id
                    )
                ).all()
                
                test_plans = session.exec(
                    sqlmodel.select(TestPlan)
                    .join(Project)
                    .where(Project.tenant_id == auth_state.user.tenant_id)
                    .order_by(sqlmodel.desc(TestPlan.created_at))
                    .options(selectinload(TestPlan.project))
                ).all()
                
                self.test_plans = [
                    TestPlanDisplay(
                        id=p.id,
                        name=p.name,
                        created_at=p.created_at.isoformat(),
                        project=TestPlanProjectDisplay(name=p.project.name)
                        if p.project
                        else None,
                    )
                    for p in test_plans
                ]
                
                if self.projects and (not self.selected_project_id):
                    self.selected_project_id = str(self.projects[0].id)
                    
                logger.info(f"Loaded {len(self.test_plans)} test plans and {len(self.projects)} projects")
                
        except Exception as e:
            logger.exception(f"Error loading test plans: {str(e)}")
            return notify_error("Failed to load test plans.")

    @rx.event
    def set_new_plan_name(self, name: str):
        self.new_plan_name = name

    @rx.event
    def set_selected_project_id(self, project_id: str):
        self.selected_project_id = project_id

    @rx.event
    async def create_test_plan(self):
        """Create a new test plan."""
        try:
            if not self.new_plan_name or not self.selected_project_id:
                logger.warning("Attempted to create test plan with missing data")
                return notify_warning("Please provide a name and select a project.")
                
            with rx.session() as session:
                plan = TestPlan(
                    name=self.new_plan_name, project_id=int(self.selected_project_id)
                )
                session.add(plan)
                session.commit()
                logger.info(f"Created test plan: {self.new_plan_name}")
                
            self.new_plan_name = ""
            await self.load_data()
            return notify_success("Test Plan created.")
            
        except ValueError as e:
            logger.error(f"Invalid project ID: {self.selected_project_id}")
            return notify_error("Invalid project selected.")
        except Exception as e:
            logger.exception(f"Error creating test plan: {str(e)}")
            return notify_error("Failed to create test plan.")

    @rx.event
    async def delete_test_plan(self, plan_id: int):
        """
        Delete a test plan.
        
        Args:
            plan_id: ID of the test plan to delete
        """
        try:
            with rx.session() as session:
                plan = session.get(TestPlan, plan_id)
                if plan:
                    session.delete(plan)
                    session.commit()
                    logger.info(f"Deleted test plan {plan_id}")
                else:
                    logger.warning(f"Attempted to delete non-existent test plan {plan_id}")
                    
            await self.load_data()
            return notify_success("Test Plan deleted.")
            
        except Exception as e:
            logger.exception(f"Error deleting test plan {plan_id}: {str(e)}")
            return notify_error("Failed to delete test plan.")