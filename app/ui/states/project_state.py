import reflex as rx
import sqlmodel
import logging
from app.core.models import Project, ProjectPolicy
from app.ui.states.auth_state import AuthState

logger = logging.getLogger(__name__)


class ProjectState(rx.State):
    projects: list[Project] = []
    new_project_name: str = ""
    is_create_modal_open: bool = False

    @rx.event
    async def load_projects(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        with rx.session() as session:
            self.projects = session.exec(
                sqlmodel.select(Project)
                .where(Project.tenant_id == auth_state.user.tenant_id)
                .order_by(sqlmodel.desc(Project.created_at))
            ).all()

    @rx.event
    def set_new_project_name(self, name: str):
        self.new_project_name = name

    @rx.event
    def toggle_create_modal(self):
        self.is_create_modal_open = not self.is_create_modal_open
        if not self.is_create_modal_open:
            self.new_project_name = ""

    @rx.event
    async def create_project(self):
        if not self.new_project_name.strip():
            return rx.toast("Project name is required.", duration=3000)
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        try:
            with rx.session() as session:
                new_project = Project(
                    name=self.new_project_name, tenant_id=auth_state.user.tenant_id
                )
                session.add(new_project)
                session.commit()
                session.refresh(new_project)
                default_policy = ProjectPolicy(project_id=new_project.id)
                session.add(default_policy)
                session.commit()
            await self.load_projects()
            self.toggle_create_modal()
            return rx.toast("Project created successfully!", duration=3000)
        except Exception as e:
            logger.exception(f"Error creating project: {e}")
            return rx.toast(f"Error creating project: {str(e)}", duration=3000)

    @rx.event
    async def delete_project(self, project_id: int):
        try:
            with rx.session() as session:
                project = session.get(Project, project_id)
                if project:
                    session.delete(project)
                    session.commit()
            await self.load_projects()
            return rx.toast("Project deleted.", duration=3000)
        except Exception as e:
            logger.exception(f"Error deleting project {project_id}: {e}")
            return rx.toast(
                "Cannot delete project. It may have related resources (scans, findings, etc.) attached.",
                duration=5000,
            )