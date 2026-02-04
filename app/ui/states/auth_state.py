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
from app.ui.utils import get_logger, notify_error, notify_success
import bcrypt
import secrets
from datetime import datetime
import sqlmodel

logger = get_logger(__name__)


class AuthState(rx.State):
    """
    Authentication state management.
    
    Handles user registration, login, logout, and session management
    with audit logging for all authentication events.
    """
    user: Optional[User] = None
    _user_id: Optional[int] = None
    error_message: str = ""
    session_id: str = rx.Cookie(
        "",
        name="session_id",
        max_age=int(settings.SESSION_TIMEOUT.total_seconds()),
        same_site="lax",
    )

    @rx.var
    def is_logged_in(self) -> bool:
        return self.user is not None

    @rx.event
    def logout(self):
        """Log out the current user and clear session."""
        logger.info(f"User logout: user_id={self._user_id}")
        self._log_audit("user.logout")
        self.user = None
        self._user_id = None
        self.session_id = ""
        return rx.redirect("/login")

    @rx.event
    def register(self, form_data: dict):
        """
        Register a new user with tenant creation.
        
        Args:
            form_data: Dictionary containing email, password, tenant_name, and username
        """
        try:
            email = form_data["email"].lower()
            password = form_data["password"]
            tenant_name = form_data["tenant_name"]
            username = form_data["username"]
            
            if not all([email, password, tenant_name, username]):
                self.error_message = "All fields are required."
                logger.warning("Registration attempt with missing fields")
                return notify_error("All fields are required.")
                
            with rx.session() as session:
                # Check for existing email
                if session.exec(sqlmodel.select(User).where(User.email == email)).first():
                    self.error_message = "Email already registered."
                    logger.warning(f"Registration attempt with existing email: {email}")
                    return notify_error("Email already registered.")
                    
                # Check for existing username
                if session.exec(
                    sqlmodel.select(User).where(User.username == username)
                ).first():
                    self.error_message = "Username already taken."
                    logger.warning(f"Registration attempt with existing username: {username}")
                    return notify_error("Username already taken.")
                    
                # Check for existing tenant name
                if session.exec(
                    sqlmodel.select(Tenant).where(Tenant.name == tenant_name)
                ).first():
                    self.error_message = "Tenant name already exists."
                    logger.warning(f"Registration attempt with existing tenant: {tenant_name}")
                    return notify_error("Tenant name already exists.")
                    
                # Create tenant
                password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
                new_tenant = Tenant(name=tenant_name)
                session.add(new_tenant)
                session.commit()
                session.refresh(new_tenant)
                
                # Create wallet and subscription
                new_wallet = Wallet(tenant_id=new_tenant.id, coins=500)
                new_subscription = Subscription(tenant_id=new_tenant.id, plan="Free")
                session.add(new_wallet)
                session.add(new_subscription)
                
                # Create user
                new_user = User(
                    username=username,
                    email=email,
                    password_hash=password_hash,
                    tenant_id=new_tenant.id,
                )
                session.add(new_user)
                session.commit()
                session.refresh(new_user)
                
                # Assign owner role
                owner_role = UserRole(user_id=new_user.id, role=RoleEnum.OWNER)
                session.add(owner_role)
                session.commit()
                
                logger.info(f"New user registered: {username} (email: {email})")
                self._log_audit(
                    "user.register", user_id=new_user.id, tenant_id=new_tenant.id
                )
                self.user = new_user
                self._user_id = new_user.id
                return AuthState.create_session(new_user.id)
                
        except KeyError as e:
            logger.error(f"Missing required field in registration: {str(e)}")
            self.error_message = "Invalid form data."
            return notify_error("Invalid form data.")
        except Exception as e:
            logger.exception(f"Registration error: {str(e)}")
            self.error_message = "Registration failed. Please try again."
            return notify_error("Registration failed. Please try again.")

    @rx.event
    def login(self, form_data: dict):
        """
        Authenticate user and create session.
        
        Args:
            form_data: Dictionary containing email and password
        """
        try:
            email = form_data["email"].lower()
            password = form_data["password"]
            
            with rx.session() as session:
                user = session.exec(
                    sqlmodel.select(User).where(User.email == email)
                ).first()
                
                if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                    logger.info(f"User login successful: {email}")
                    self._log_audit("user.login", user_id=user.id, tenant_id=user.tenant_id)
                    self.user = user
                    self._user_id = user.id
                    return AuthState.create_session(user.id)
                else:
                    logger.warning(f"Failed login attempt for email: {email}")
                    self.error_message = "Invalid email or password."
                    self._log_audit(
                        "user.login.failed",
                        details=f"Failed login attempt for email: {email}",
                    )
                    return notify_error("Invalid email or password.")
                    
        except KeyError as e:
            logger.error(f"Missing required field in login: {str(e)}")
            self.error_message = "Invalid form data."
            return notify_error("Invalid form data.")
        except Exception as e:
            logger.exception(f"Login error: {str(e)}")
            self.error_message = "Login failed. Please try again."
            return notify_error("Login failed. Please try again.")

    @rx.event
    def create_session(self, user_id: int):
        """
        Create a new session for authenticated user.
        
        Args:
            user_id: The ID of the user to create session for
        """
        try:
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + settings.SESSION_TIMEOUT
            
            with rx.session() as session:
                new_session = Session(
                    session_id=session_token, user_id=user_id, expires_at=expires_at
                )
                session.add(new_session)
                session.commit()
                
            logger.info(f"Session created for user_id: {user_id}")
            self.session_id = session_token
            return rx.redirect("/")
            
        except Exception as e:
            logger.exception(f"Error creating session for user_id {user_id}: {str(e)}")
            return notify_error("Failed to create session. Please try again.")

    def _log_audit(
        self,
        action: str,
        user_id: int | None = None,
        tenant_id: int | None = None,
        details: str | None = None,
    ):
        """
        Log audit trail for authentication events.
        
        Args:
            action: The action being performed
            user_id: Optional user ID (defaults to current user)
            tenant_id: Optional tenant ID (defaults to current user's tenant)
            details: Optional additional details
        """
        try:
            with rx.session() as session:
                if user_id is None and self._user_id:
                    user_id = self._user_id
                if tenant_id is None and self.user:
                    tenant_id = self.user.tenant_id
                audit_log = AuditLog(
                    user_id=user_id, tenant_id=tenant_id, action=action, details=details
                )
                session.add(audit_log)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to log audit action '{action}': {str(e)}")

    @rx.event
    def check_login(self):
        """Verify session validity and restore user state."""
        try:
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
                        self._user_id = user.id
                        logger.debug(f"Session validated for user_id: {user.id}")
                        return
                        
            logger.warning("Invalid or expired session")
            return AuthState.logout()
            
        except Exception as e:
            logger.exception(f"Error checking login: {str(e)}")
            return AuthState.logout()

    @rx.var
    def current_user_role(self) -> str:
        """Get the current user's role."""
        try:
            if not self._user_id:
                return "Not logged in"
                
            with rx.session() as session:
                role = session.exec(
                    sqlmodel.select(UserRole).where(UserRole.user_id == self._user_id)
                ).first()
                return role.role.value if role else "No role"
                
        except Exception as e:
            logger.error(f"Error fetching user role: {str(e)}")
            return "Error"