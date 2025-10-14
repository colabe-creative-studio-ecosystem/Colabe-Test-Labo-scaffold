import reflex as rx
from app.ui.states.auth_state import AuthState
from app.core.models import Run, RunStep, TestPlan
import sqlmodel
from app.orchestrator.tasks import enqueue_test_run
import logging


class RunState(AuthState):
    run: Run = Run(id=-1, test_plan_id=-1, status="pending")
    run_steps: list[RunStep] = []
    run_steps_with_duration: list[dict] = []

    @rx.event
    def load_run_details(self):
        if not self.is_logged_in:
            return rx.redirect("/login")
        run_id_str = self.router.page.params.get("run_id")
        if not run_id_str:
            return rx.redirect("/app")
        try:
            run_id = int(run_id_str)
        except ValueError as e:
            logging.exception(e)
            return rx.redirect("/app")
        with rx.session() as session:
            run = session.exec(
                sqlmodel.select(Run)
                .where(Run.id == run_id)
                .options(sqlmodel.selectinload(Run.steps))
            ).first()
            if run:
                self.run = run
                dag_order = {
                    step: i
                    for i, step in enumerate(
                        [
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
                    )
                }
                sorted_steps = sorted(
                    run.steps, key=lambda s: dag_order.get(s.name, 99)
                )
                self.run_steps = sorted_steps
                steps_data = []
                for step in sorted_steps:
                    duration_str = ""
                    if step.completed_at and step.started_at:
                        duration = (step.completed_at - step.started_at).total_seconds()
                        duration_str = f"{duration:.2f}s"
                    steps_data.append(
                        {
                            "id": step.id,
                            "name": step.name,
                            "status": step.status,
                            "duration": duration_str,
                        }
                    )
                self.run_steps_with_duration = steps_data
            else:
                return rx.redirect("/app")
        if self.run.status in ["pending", "running"]:
            return RunState.load_run_details

    @rx.event
    def start_run(self, test_plan_id: int):
        with rx.session() as session:
            tp = session.get(TestPlan, test_plan_id)
            if not tp:
                tp = TestPlan(
                    id=test_plan_id, name=f"Demo Plan {test_plan_id}", project_id=1
                )
                session.add(tp)
                session.commit()
            new_run = Run(test_plan_id=test_plan_id, status="pending")
            session.add(new_run)
            session.commit()
            session.refresh(new_run)
            enqueue_test_run(new_run.id, self.user.tenant_id)
            return rx.redirect(f"/runs/{new_run.id}")