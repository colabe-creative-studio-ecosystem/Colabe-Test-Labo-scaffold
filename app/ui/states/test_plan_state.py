import reflex as rx
import sqlmodel
from app.core.models import TestPlan, Project
from app.ui.states.auth_state import AuthState


class TestPlanProjectDisplay(rx.Base):
    name: str


class TestPlanDisplay(rx.Base):
    id: int
    name: str
    created_at: str
    project: TestPlanProjectDisplay | None = None


class TestPlanState(rx.State):
    test_plans: list[TestPlanDisplay] = []
    new_plan_name: str = ""
    selected_project_id: str = ""
    projects: list[Project] = []

    @rx.event
    async def load_data(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
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
                .options(sqlmodel.selectinload(TestPlan.project))
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

    @rx.event
    def set_new_plan_name(self, name: str):
        self.new_plan_name = name

    @rx.event
    def set_selected_project_id(self, project_id: str):
        self.selected_project_id = project_id

    @rx.event
    async def create_test_plan(self):
        if not self.new_plan_name or not self.selected_project_id:
            return rx.toast(
                "Please provide a name and select a project.", duration=3000
            )
        with rx.session() as session:
            plan = TestPlan(
                name=self.new_plan_name, project_id=int(self.selected_project_id)
            )
            session.add(plan)
            session.commit()
        self.new_plan_name = ""
        await self.load_data()
        return rx.toast("Test Plan created.", duration=3000)

    @rx.event
    async def delete_test_plan(self, plan_id: int):
        with rx.session() as session:
            plan = session.get(TestPlan, plan_id)
            if plan:
                session.delete(plan)
                session.commit()
        await self.load_data()
        return rx.toast("Test Plan deleted.", duration=3000)