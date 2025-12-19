import reflex as rx
import sqlmodel
import logging
from app.ui.states.auth_state import AuthState
from app.core.models import SecurityFinding, AutofixRun, AutofixPatch
from app.autofix.patch_generator import PatchGenerator

logger = logging.getLogger(__name__)


class AutofixState(rx.State):
    autofix_runs: list[AutofixRun] = []

    @rx.event(background=True)
    async def trigger_autofix(self, finding_id: int):
        async with self:
            auth_state = await self.get_state(AuthState)
            if not auth_state.is_logged_in or not auth_state.user:
                return
            with rx.session() as session:
                finding = session.exec(
                    sqlmodel.select(SecurityFinding).where(
                        SecurityFinding.id == finding_id
                    )
                ).first()
                if not finding:
                    logger.error(f"Security finding with id {finding_id} not found.")
                    return
                autofix_run = AutofixRun(finding_id=finding_id, status="running")
                session.add(autofix_run)
                session.commit()
                session.refresh(autofix_run)
        try:
            patch_generator = PatchGenerator()
            patched_code = patch_generator.generate_patch(finding)
            async with self:
                with rx.session() as session:
                    autofix_run = session.get(AutofixRun, autofix_run.id)
                    if patched_code:
                        original_code = patch_generator._get_file_content(
                            finding.file_path
                        )
                        import difflib

                        diff = "".join(
                            difflib.unified_diff(
                                original_code.splitlines(keepends=True),
                                patched_code.splitlines(keepends=True),
                                fromfile=f"a/{finding.file_path}",
                                tofile=f"b/{finding.file_path}",
                            )
                        )
                        autofix_patch = AutofixPatch(
                            autofix_run_id=autofix_run.id, diff=diff
                        )
                        session.add(autofix_patch)
                        autofix_run.status = "completed"
                        logger.info(f"Autofix patch generated for finding {finding_id}")
                    else:
                        autofix_run.status = "failed"
                        logger.error(
                            f"Failed to generate autofix patch for finding {finding_id}"
                        )
                    session.add(autofix_run)
                    session.commit()
        except Exception as e:
            logger.exception(
                f"Error during autofix process for finding {finding_id}: {e}"
            )
            async with self:
                with rx.session() as session:
                    autofix_run = session.get(AutofixRun, autofix_run.id)
                    if autofix_run:
                        autofix_run.status = "failed"
                        session.add(autofix_run)
                        session.commit()