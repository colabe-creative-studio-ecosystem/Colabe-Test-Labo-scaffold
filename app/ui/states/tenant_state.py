import reflex as rx
import reflex as rx
import sqlmodel
import json
import uuid
import datetime
import logging
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import (
    Tenant,
    User,
    UserRole,
    RoleEnum,
    Wallet,
    Subscription,
    ProjectPolicy,
    TenantStatusEnum,
)
from app.core.settings import settings


class TenantState(AuthState):
    tenants: list[Tenant] = []

    @rx.event
    def load_tenants(self):
        if not self.is_admin:
            return rx.redirect("/")
        with rx.session() as session:
            self.tenants = session.exec(sqlmodel.select(Tenant)).all()

    @rx.event
    def provision_tenant(self, form_data: dict):
        if not self.is_admin:
            return rx.toast("Permission denied.")
        tenant_name = form_data.get("tenant_name")
        owner_email = form_data.get("owner_email")
        plan = form_data.get("plan", "Free")
        region = form_data.get("region", settings.TENANT_DEFAULT_REGION)
        trial_days = int(form_data.get("trial_days", settings.TRIAL_DAYS_DEFAULT))
        if not tenant_name or not owner_email:
            return rx.toast("Tenant Name and Owner Email are required.")
        with rx.session() as session:
            if session.exec(
                sqlmodel.select(Tenant).where(Tenant.name == tenant_name)
            ).first():
                return rx.toast(f"Tenant '{tenant_name}' already exists.")
            new_tenant = Tenant(name=tenant_name, plan=plan, region=region)
            if trial_days > 0:
                new_tenant.trial_ends_at = datetime.datetime.now(
                    datetime.timezone.utc
                ) + datetime.timedelta(days=trial_days)
            session.add(new_tenant)
            session.commit()
            session.refresh(new_tenant)
            wallet = Wallet(
                tenant_id=new_tenant.id, coins=1000 if plan != "Free" else 100
            )
            sub = Subscription(tenant_id=new_tenant.id, plan=plan, status="active")
            session.add(wallet)
            session.add(sub)
            owner_user = session.exec(
                sqlmodel.select(User).where(User.email == owner_email)
            ).first()
            if not owner_user:
                import bcrypt
                import secrets

                temp_password = secrets.token_urlsafe(16)
                password_hash = bcrypt.hashpw(
                    temp_password.encode(), bcrypt.gensalt()
                ).decode()
                owner_user = User(
                    username=owner_email.split("@")[0],
                    email=owner_email,
                    password_hash=password_hash,
                    tenant_id=new_tenant.id,
                )
                session.add(owner_user)
                session.commit()
                session.refresh(owner_user)
                owner_role = UserRole(user_id=owner_user.id, role=RoleEnum.OWNER)
                session.add(owner_role)
            self._log_audit(
                action="tenant.provision",
                tenant_id=new_tenant.id,
                details=f"Provisioned tenant '{tenant_name}' with plan '{plan}'.",
            )
            session.commit()
        self.load_tenants()
        return rx.toast(f"Tenant '{tenant_name}' provisioned successfully.")

    @rx.event
    def update_tenant_status(self, tenant_id: int, status: str):
        if not self.is_admin:
            return rx.toast("Permission denied.")
        try:
            new_status = TenantStatusEnum(status)
        except ValueError as e:
            logging.exception(f"Invalid status: {status}, error: {e}")
            return rx.toast(f"Invalid status: {status}")
        with rx.session() as session:
            tenant = session.get(Tenant, tenant_id)
            if tenant:
                old_status = tenant.status.value
                tenant.status = new_status
                session.add(tenant)
                self._log_audit(
                    action=f"tenant.{status}",
                    tenant_id=tenant_id,
                    details=f"Tenant status changed from '{old_status}' to '{status}'.",
                )
                session.commit()
                self.load_tenants()
                return rx.toast(f"Tenant status updated to {status}.")