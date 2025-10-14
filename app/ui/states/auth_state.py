import reflex as rx
from typing import Optional
from app.core.models import (
    User,
    Tenant,
    Membership,
    RoleEnum,
    AuditEvent,
    Session,
    Wallet,
    Subscription,
    Organization,
)
from app.core.settings import settings
from app.integrations.triggerbus import TriggerBus
import bcrypt
import secrets
import json
from datetime import datetime, timedelta
import sqlmodel
import logging

logger = logging.getLogger(__name__)


class AuthState(rx.State):
    user: Optional[User] = None
    current_tenant: Optional[Tenant] = None
    memberships: list[Membership] = []
    error_message: str = ""
    session_id: str = rx.Cookie(
        "",
        name=settings.SESSION_COOKIE_NAME,
        max_age=settings.SESSION_TTL_HOURS * 3600,
        same_site="lax",
        secure=True,
    )
    csrf_token: str = rx.Cookie("", name="csrf_token")
    _feature_flags_cache: dict[str, str | bool | int] = {}
    _cache_expiry: Optional[datetime] = None

    @rx.var
    def is_logged_in(self) -> bool:
        return self.user is not None

    @rx.var
    def current_role(self) -> RoleEnum | None:
        if self.user and self.current_tenant:
            for m in self.memberships:
                if m.tenant_id == self.current_tenant.id:
                    return m.role
        return None

    @rx.var
    def is_owner(self) -> bool:
        return self.current_role == RoleEnum.OWNER

    @rx.var
    def is_admin(self) -> bool:
        return self.current_role in [RoleEnum.OWNER, RoleEnum.ADMIN]

    @rx.event
    def logout(self):
        self._log_audit("auth.logout")
        TriggerBus.publish(
            "auth.logout",
            {"user_id": self.user.id},
            self.current_tenant.id,
            idempotency_key=f"logout-{self.user.id}-{datetime.now().timestamp()}",
        )
        self.user = None
        self.current_tenant = None
        self.memberships = []
        self.session_id = ""
        self.csrf_token = ""
        return rx.redirect("/login")

    @rx.event
    def sso_login(self):
        with rx.session() as session:
            user = session.exec(
                sqlmodel.select(User).where(User.email == "owner@colabe.ai")
            ).first()
            if user:
                self.user = user
                return self._post_login_setup(user.id, session)
            else:
                self.error_message = "SSO user not found. Please seed the database."
                return rx.toast(self.error_message)

    @rx.event
    def register(self, form_data: dict):
        email = form_data.get("email", "").lower()
        password = form_data.get("password", "")
        org_name = form_data.get("org_name", "")
        username = form_data.get("username", "")
        if not all([email, password, org_name, username]):
            self.error_message = "All fields are required."
            return rx.toast(self.error_message)
        with rx.session() as session:
            if session.exec(sqlmodel.select(User).where(User.email == email)).first():
                self.error_message = "Email already registered."
                return rx.toast(self.error_message)
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_org = Organization(name=org_name)
            session.add(new_org)
            session.commit()
            session.refresh(new_org)
            new_tenant = Tenant(name=f"{org_name} Default", organization_id=new_org.id)
            session.add(new_tenant)
            session.commit()
            session.refresh(new_tenant)
            new_user = User(username=username, email=email, password_hash=password_hash)
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            membership = Membership(
                user_id=new_user.id, tenant_id=new_tenant.id, role=RoleEnum.OWNER
            )
            session.add(membership)
            self._log_audit(
                "user.register",
                actor_user_id=new_user.id,
                tenant_id=new_tenant.id,
                details=f"User {email} registered and created organization {org_name}",
            )
            session.commit()
            self.user = new_user
            return self._post_login_setup(new_user.id, session)

    @rx.event
    def login(self, form_data: dict):
        email = form_data["email"].lower()
        password = form_data["password"]
        with rx.session() as session:
            user = session.exec(
                sqlmodel.select(User).where(User.email == email)
            ).first()
            if (
                user
                and user.password_hash
                and bcrypt.checkpw(password.encode(), user.password_hash.encode())
            ):
                self.user = user
                return self._post_login_setup(user.id, session)
            else:
                self.error_message = "Invalid email or password."
                self._log_audit(
                    "auth.login.failed", details=f"Failed login attempt for {email}"
                )
                return rx.toast(self.error_message)

    def _post_login_setup(self, user_id: int, session: sqlmodel.Session):
        self._load_user_context(user_id, session)
        if not self.memberships:
            self.error_message = "User has no tenant memberships."
            return rx.toast(self.error_message)
        self.current_tenant = self.memberships[0].tenant
        self._log_audit("auth.login")
        TriggerBus.publish(
            "auth.login",
            {"user_id": user_id},
            self.current_tenant.id,
            idempotency_key=f"login-{user_id}-{datetime.now().timestamp()}",
        )
        return self._create_session(user_id, session)

    def _create_session(self, user_id: int, session: sqlmodel.Session):
        session_token = secrets.token_urlsafe(32)
        csrf_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(hours=settings.SESSION_TTL_HOURS)
        new_session = Session(
            session_id=session_token, user_id=user_id, expires_at=expires_at
        )
        session.add(new_session)
        session.commit()
        self.session_id = session_token
        self.csrf_token = csrf_token
        return rx.redirect("/")

    def _log_audit(
        self,
        action: str,
        actor_user_id: int | None = None,
        tenant_id: int | None = None,
        resource_crn: str | None = None,
        before: dict | None = None,
        after: dict | None = None,
        details: str | None = None,
    ):
        with rx.session() as session:
            uid = actor_user_id or (self.user.id if self.user else None)
            tid = tenant_id or (self.current_tenant.id if self.current_tenant else None)
            if uid is None or tid is None:
                logger.warning(
                    f"Could not log audit action '{action}' due to missing user/tenant ID."
                )
                return
            event = AuditEvent(
                actor_user_id=uid,
                tenant_id=tid,
                action=action,
                resource_crn=resource_crn,
                before_json=json.dumps(before) if before else None,
                after_json=json.dumps(after) if after else None,
                ip_address=self.router.headers.get("x-forwarded-for"),
                user_agent=self.router.headers.get("user-agent"),
            )
            session.add(event)
            session.commit()

    def _load_user_context(self, user_id: int, session: sqlmodel.Session):
        self.memberships = session.exec(
            sqlmodel.select(Membership)
            .where(Membership.user_id == user_id)
            .options(sqlmodel.selectinload(Membership.tenant))
        ).all()

    @rx.event
    def check_login(self):
        if not self.session_id:
            return rx.redirect("/login")
        with rx.session() as session:
            db_session = session.exec(
                sqlmodel.select(Session)
                .where(Session.session_id == self.session_id)
                .options(sqlmodel.selectinload(Session.user))
            ).first()
            if db_session and db_session.expires_at > datetime.now():
                db_session.expires_at = datetime.now() + timedelta(
                    hours=settings.SESSION_TTL_HOURS
                )
                session.add(db_session)
                session.commit()
                self.user = db_session.user
                self._load_user_context(self.user.id, session)
                if self.memberships:
                    if not self.current_tenant or self.current_tenant.id not in [
                        m.tenant_id for m in self.memberships
                    ]:
                        self.current_tenant = self.memberships[0].tenant
                    return
            return AuthState.logout()

    @rx.event
    def switch_tenant(self, tenant_id: int):
        if not self.is_logged_in:
            return rx.redirect("/login")
        valid_tenant = False
        for m in self.memberships:
            if m.tenant_id == tenant_id:
                self.current_tenant = m.tenant
                valid_tenant = True
                break
        if valid_tenant:
            self._log_audit(
                "tenant.switch", resource_crn=f"crn:colabe:global:{tenant_id}:tenant"
            )
            return rx.redirect(self.router.page.path)
        else:
            return rx.toast("Access to this tenant is not permitted.")