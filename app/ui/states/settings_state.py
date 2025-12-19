import reflex as rx
import sqlmodel
from app.ui.states.auth_state import AuthState
from app.core.models import User, Tenant
import logging

logger = logging.getLogger(__name__)


class SettingsState(rx.State):
    username: str = ""
    email: str = ""
    tenant_name: str = ""
    is_saving: bool = False

    @rx.event
    async def load_settings(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        self.username = auth_state.user.username
        self.email = auth_state.user.email
        with rx.session() as session:
            tenant = session.get(Tenant, auth_state.user.tenant_id)
            if tenant:
                self.tenant_name = tenant.name

    @rx.event
    async def save_profile(self, form_data: dict):
        self.is_saving = True
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        new_email = form_data.get("email")
        if not new_email:
            self.is_saving = False
            return rx.toast("Email is required.")
        try:
            with rx.session() as session:
                user = session.get(User, auth_state.user.id)
                if user:
                    existing_user = session.exec(
                        sqlmodel.select(User)
                        .where(User.email == new_email)
                        .where(User.id != user.id)
                    ).first()
                    if existing_user:
                        self.is_saving = False
                        return rx.toast("Email already in use.")
                    user.email = new_email
                    session.add(user)
                    session.commit()
                    session.refresh(user)
                    self.email = new_email
                    auth_state.user = user
            self.is_saving = False
            return rx.toast("Profile updated successfully.")
        except Exception as e:
            logger.exception(f"Error updating profile: {e}")
            self.is_saving = False
            return rx.toast("Failed to update profile.")

    @rx.event
    async def save_tenant(self, form_data: dict):
        self.is_saving = True
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        new_name = form_data.get("tenant_name")
        if not new_name:
            self.is_saving = False
            return rx.toast("Tenant name is required.")
        try:
            with rx.session() as session:
                tenant = session.get(Tenant, auth_state.user.tenant_id)
                if tenant:
                    existing_tenant = session.exec(
                        sqlmodel.select(Tenant)
                        .where(Tenant.name == new_name)
                        .where(Tenant.id != tenant.id)
                    ).first()
                    if existing_tenant:
                        self.is_saving = False
                        return rx.toast("Tenant name already exists.")
                    tenant.name = new_name
                    session.add(tenant)
                    session.commit()
                    session.refresh(tenant)
                    self.tenant_name = new_name
            self.is_saving = False
            return rx.toast("Tenant settings updated.")
        except Exception as e:
            logger.exception(f"Error updating tenant: {e}")
            self.is_saving = False
            return rx.toast("Failed to update tenant.")