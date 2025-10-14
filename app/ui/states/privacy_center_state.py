import reflex as rx
import sqlmodel
import secrets
import logging
from datetime import datetime, timedelta
from app.ui.states.auth_state import AuthState
from app.core.models import DataSubjectRequest, DataRequestType, DataRequestStatus, User

logger = logging.getLogger(__name__)


class PrivacyCenterState(AuthState):
    request_type: str = "access"
    email: str = ""
    form_message: str = ""
    is_verifying: bool = False
    verification_code: str = ""
    dsr_id_in_verification: int | None = None
    dsr_list: list[DataSubjectRequest] = []

    @rx.var
    def user_email(self) -> str:
        return self.user.email if self.user else ""

    @rx.var
    def user_has_requests(self) -> bool:
        return len(self.dsr_list) > 0

    @rx.event
    def load_requests(self):
        if not self.is_logged_in or not self.user:
            return
        with rx.session() as session:
            self.dsr_list = session.exec(
                sqlmodel.select(DataSubjectRequest)
                .where(DataSubjectRequest.user_id == self.user.id)
                .order_by(sqlmodel.desc(DataSubjectRequest.created_at))
            ).all()

    @rx.event
    def handle_dsr_submit(self, form_data: dict):
        self.form_message = ""
        email_to_use = self.user.email if self.user else form_data.get("email")
        if not email_to_use:
            self.form_message = "Email is required."
            return
        self.email = email_to_use
        with rx.session() as session:
            existing_pending_request = session.exec(
                sqlmodel.select(DataSubjectRequest)
                .where(DataSubjectRequest.email == self.email)
                .where(
                    DataSubjectRequest.status.in_(
                        [
                            DataRequestStatus.RECEIVED,
                            DataRequestStatus.VERIFYING,
                            DataRequestStatus.IN_PROGRESS,
                        ]
                    )
                )
            ).first()
            if existing_pending_request:
                self.form_message = "You already have a pending request. Please wait for it to be completed."
                return
            dsr = DataSubjectRequest(
                email=self.email,
                request_type=DataRequestType(self.request_type),
                user_id=self.user.id if self.user else None,
                tenant_id=self.user.tenant_id if self.user else None,
            )
            if not self.is_logged_in:
                code = secrets.token_hex(3).upper()
                dsr.verification_code = code
                dsr.verification_expires_at = datetime.now() + timedelta(minutes=15)
                dsr.status = DataRequestStatus.VERIFYING
                session.add(dsr)
                session.commit()
                session.refresh(dsr)
                self.dsr_id_in_verification = dsr.id
                self.is_verifying = True
                self.form_message = "A verification code has been sent to your email."
                logger.info(f"DSR verification code for {self.email}: {code}")
            else:
                session.add(dsr)
                session.commit()
                self.form_message = "Your request has been received."
                self._log_audit(
                    action="privacy.request.created",
                    details=f"Type: {self.request_type}",
                )
                return PrivacyCenterState.load_requests

    @rx.event
    def handle_verification(self, form_data: dict):
        code = form_data.get("verification_code")
        if not code:
            self.form_message = "Verification code is required."
            return
        with rx.session() as session:
            dsr = session.get(DataSubjectRequest, self.dsr_id_in_verification)
            if (
                not dsr
                or dsr.verification_code != code
                or dsr.verification_expires_at < datetime.now()
            ):
                self.form_message = "Invalid or expired verification code."
                if dsr:
                    dsr.status = DataRequestStatus.REJECTED
                    session.add(dsr)
                    session.commit()
                self.is_verifying = False
                self.dsr_id_in_verification = None
                return
            dsr.status = DataRequestStatus.RECEIVED
            dsr.verification_code = None
            dsr.verification_expires_at = None
            session.add(dsr)
            session.commit()
        self.is_verifying = False
        self.dsr_id_in_verification = None
        self.form_message = "Verification successful. Your request has been received."
        logger.info(f"DSR for {self.email} verified and queued for processing.")

    @rx.event
    def cancel_verification(self):
        if self.dsr_id_in_verification:
            with rx.session() as session:
                dsr = session.get(DataSubjectRequest, self.dsr_id_in_verification)
                if dsr:
                    session.delete(dsr)
                    session.commit()
        self.is_verifying = False
        self.dsr_id_in_verification = None
        self.form_message = ""
        self.email = ""