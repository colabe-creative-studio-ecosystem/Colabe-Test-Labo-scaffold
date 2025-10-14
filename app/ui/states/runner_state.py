import reflex as rx
import sqlmodel
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import RunnerPool, Runner
import secrets


class RunnerState(AuthState):
    runner_pools: list[RunnerPool] = []
    runners: list[Runner] = []
    selected_pool_id: Optional[int] = None
    active_tab: str = "runners"
    enrollment_token: str = ""

    @rx.event
    def load_runner_data(self):
        if not self.is_logged_in or not self.user:
            return rx.redirect("/login")
        with rx.session() as session:
            self.runner_pools = session.exec(
                sqlmodel.select(RunnerPool)
                .where(RunnerPool.tenant_id == self.user.tenant_id)
                .options(sqlmodel.selectinload(RunnerPool.runners))
                .order_by(RunnerPool.name)
            ).all()
            self.runners = session.exec(
                sqlmodel.select(Runner)
                .join(RunnerPool)
                .where(RunnerPool.tenant_id == self.user.tenant_id)
            ).all()
            if self.runner_pools and self.selected_pool_id is None:
                self.selected_pool_id = self.runner_pools[0].id

    @rx.event
    def select_pool(self, pool_id: int):
        self.selected_pool_id = pool_id
        self.active_tab = "runners"
        self.enrollment_token = ""

    @rx.event
    def set_active_tab(self, tab_name: str):
        self.active_tab = tab_name

    @rx.event
    def generate_enrollment_token(self):
        if not self.selected_pool_id:
            return
        token = f"colabe-token-{secrets.token_urlsafe(32)}"
        self.enrollment_token = token
        with rx.session() as session:
            pool = session.get(RunnerPool, self.selected_pool_id)
            if pool:
                pool.enrollment_token = token
                session.add(pool)
                session.commit()

    @rx.var
    def selected_pool(self) -> RunnerPool | None:
        if self.selected_pool_id is None:
            return None
        return next(
            (p for p in self.runner_pools if p.id == self.selected_pool_id), None
        )

    @rx.var
    def runners_in_selected_pool(self) -> list[Runner]:
        if self.selected_pool_id is None:
            return []
        return [r for r in self.runners if r.pool_id == self.selected_pool_id]