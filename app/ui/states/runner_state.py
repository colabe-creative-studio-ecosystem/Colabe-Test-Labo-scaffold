import reflex as rx
import sqlmodel
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import RunnerPool, Runner


class RunnerState(AuthState):
    runner_pools: list[RunnerPool] = []
    runners: list[Runner] = []

    @rx.event
    def load_runner_data(self):
        if not self.is_logged_in or not self.user:
            return rx.redirect("/login")
        with rx.session() as session:
            self.runner_pools = session.exec(
                sqlmodel.select(RunnerPool)
                .where(RunnerPool.tenant_id == self.user.tenant_id)
                .options(sqlmodel.selectinload(RunnerPool.runners))
            ).all()
            self.runners = session.exec(
                sqlmodel.select(Runner)
                .join(RunnerPool)
                .where(RunnerPool.tenant_id == self.user.tenant_id)
            ).all()