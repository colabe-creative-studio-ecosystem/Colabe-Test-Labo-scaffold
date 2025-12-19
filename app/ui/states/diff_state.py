import reflex as rx
import sqlmodel
from app.core.models import AutofixPatch, AutofixRun, SecurityFinding, Project
from app.ui.states.auth_state import AuthState


class DiffFindingDisplay(rx.Base):
    description: str
    file_path: str


class DiffRunDisplay(rx.Base):
    finding: DiffFindingDisplay | None = None


class PatchDisplay(rx.Base):
    id: int
    diff: str
    created_at: str
    run: DiffRunDisplay | None = None


class DiffState(rx.State):
    patches: list[PatchDisplay] = []

    @rx.event
    async def load_data(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        with rx.session() as session:
            patches = session.exec(
                sqlmodel.select(AutofixPatch)
                .join(AutofixRun)
                .join(SecurityFinding)
                .join(Project)
                .where(Project.tenant_id == auth_state.user.tenant_id)
                .order_by(sqlmodel.desc(AutofixPatch.created_at))
                .options(
                    sqlmodel.selectinload(AutofixPatch.run).selectinload(
                        AutofixRun.finding
                    )
                )
            ).all()
            self.patches = [
                PatchDisplay(
                    id=p.id,
                    diff=p.diff,
                    created_at=p.created_at.isoformat(),
                    run=DiffRunDisplay(
                        finding=DiffFindingDisplay(
                            description=p.run.finding.description,
                            file_path=p.run.finding.file_path,
                        )
                        if p.run.finding
                        else None
                    )
                    if p.run
                    else None,
                )
                for p in patches
            ]