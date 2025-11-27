import reflex as rx
from typing import Optional
from app.core.models import (
    User,
    Tenant,
    UserRole,
    RoleEnum,
    AuditLog,
    Session,
    Wallet,
    Subscription,
)
from app.core.settings import settings
import bcrypt
import secrets
from datetime import datetime, timedelta
import sqlmodel


class AuthState(rx.State):
    user: Optional[User] = None
    error_message: str = ""
    session_id: str = rx.Cookie(
        "",
        name="session_id",
        max_age=settings.SESSION_TIMEOUT.total_seconds(),
        same_site="lax",
    )

    @rx.var
    def is_logged_in(self) -> bool:
        return self.user is not None

    @rx.event
    def logout(self):
        self._log_audit("user.logout")
        self.user = None
        self.session_id = ""
        return rx.redirect("/login")

    @rx.event
    def register(self, form_data: dict):
        email = form_data["email"].lower()
        password = form_data["password"]
        tenant_name = form_data["tenant_name"]
        username = form_data["username"]
        if not all([email, password, tenant_name, username]):
            self.error_message = "All fields are required."
            return
        with rx.session() as session:
            if session.exec(sqlmodel.select(User).where(User.email == email)).first():
                self.error_message = "Email already registered."
                return
            if session.exec(
                sqlmodel.select(User).where(User.username == username)
            ).first():
                self.error_message = "Username already taken."
                return
            if session.exec(
                sqlmodel.select(Tenant).where(Tenant.name == tenant_name)
            ).first():
                self.error_message = "Tenant name already exists."
                return
            password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            new_tenant = Tenant(name=tenant_name)
            session.add(new_tenant)
            session.commit()
            session.refresh(new_tenant)
            new_wallet = Wallet(tenant_id=new_tenant.id, coins=500)
            new_subscription = Subscription(tenant_id=new_tenant.id, plan="Free")
            session.add(new_wallet)
            session.add(new_subscription)
            new_user = User(
                username=username,
                email=email,
                password_hash=password_hash,
                tenant_id=new_tenant.id,
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            owner_role = UserRole(user_id=new_user.id, role=RoleEnum.OWNER)
            session.add(owner_role)
            session.commit()
            self._log_audit(
                "user.register", user_id=new_user.id, tenant_id=new_tenant.id
            )
            self.user = new_user
            return self._create_session(new_user.id, session)

    @rx.event
    def login(self, form_data: dict):
        email = form_data["email"].lower()
        password = form_data["password"]
        with rx.session() as session:
            user = session.exec(
                sqlmodel.select(User).where(User.email == email)
            ).first()
            if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                self._log_audit("user.login", user_id=user.id, tenant_id=user.tenant_id)
                self.user = user
                return self._create_session(user.id, session)
            else:
                self.error_message = "Invalid email or password."
                self._log_audit(
                    "user.login.failed",
                    details=f"Failed login attempt for email: {email}",
                )
                return rx.toast("Invalid email or password", duration=3000)

    def _create_session(self, user_id: int, session: sqlmodel.Session):
        session_token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + settings.SESSION_TIMEOUT
        new_session = Session(
            session_id=session_token, user_id=user_id, expires_at=expires_at
        )
        session.add(new_session)
        session.commit()
        self.session_id = session_token
        return rx.redirect("/")

    def _log_audit(
        self,
        action: str,
        user_id: int | None = None,
        tenant_id: int | None = None,
        details: str | None = None,
    ):
        with rx.session() as session:
            if user_id is None and self.user:
                user_id = self.user.id
            if tenant_id is None and self.user:
                tenant_id = self.user.tenant_id
            audit_log = AuditLog(
                user_id=user_id, tenant_id=tenant_id, action=action, details=details
            )
            session.add(audit_log)
            session.commit()

    @rx.event
    def check_login(self):
        if not self.session_id:
            return rx.redirect("/login")
        with rx.session() as session:
            db_session = session.exec(
                sqlmodel.select(Session).where(Session.session_id == self.session_id)
            ).first()
            if db_session and db_session.expires_at > datetime.now():
                user = session.exec(
                    sqlmodel.select(User).where(User.id == db_session.user_id)
                ).first()
                if user:
                    self.user = user
                    return
        return self.logout()


    @rx.var
    def current_user_role(self) -> str:
        if not self.user:
            return "Not logged in"
        with rx.session() as session:
            role = session.exec(
                sqlmodel.select(UserRole).where(UserRole.user_id == self.user.id)
            ).first()
            return role.role.value if role else "No role"
