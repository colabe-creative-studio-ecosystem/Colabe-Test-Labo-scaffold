import reflex as rx
import sqlmodel
from datetime import datetime
from app.core.models import Run, TestPlan, Project
from app.ui.states.auth_state import AuthState


class RunProjectDisplay(rx.Base):
    name: str


class RunPlanDisplay(rx.Base):
    name: str
    project: RunProjectDisplay | None = None


class RunDisplay(rx.Base):
    id: int
    status: str
    started_at: str | None = None
    test_plan: RunPlanDisplay | None = None


class RunState(rx.State):
    runs: list[RunDisplay] = []

    @rx.event
    async def load_data(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        with rx.session() as session:
            runs = session.exec(
                sqlmodel.select(Run)
                .join(TestPlan)
                .join(Project)
                .where(Project.tenant_id == auth_state.user.tenant_id)
                .order_by(sqlmodel.desc(Run.created_at))
                .options(
                    sqlmodel.selectinload(Run.test_plan).selectinload(TestPlan.project)
                )
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

    @rx.event
    async def trigger_run(self, plan_id: int):
        with rx.session() as session:
            run = Run(test_plan_id=plan_id, status="running", started_at=datetime.now())
            session.add(run)
            session.commit()
        await self.load_data()
        return rx.toast("Run triggered successfully.", duration=3000)

    @rx.event
    async def delete_run(self, run_id: int):
        with rx.session() as session:
            run = session.get(Run, run_id)
            if run:
                session.delete(run)
                session.commit()
        await self.load_data()
        return rx.toast("Run deleted.", duration=3000)