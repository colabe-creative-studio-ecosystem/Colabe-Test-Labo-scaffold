import reflex as rx
import sqlmodel
from app.ui.states.auth_state import AuthState
from app.core.models import Membership, User, RoleEnum
import logging

logger = logging.getLogger(__name__)


class MemberState(AuthState):
    members: list[Membership] = []

    @rx.event
    def load_members(self):
        if not self.is_logged_in or not self.current_tenant:
            return rx.redirect("/login")
        with rx.session() as session:
            self.members = session.exec(
                sqlmodel.select(Membership)
                .where(Membership.tenant_id == self.current_tenant.id)
                .options(sqlmodel.selectinload(Membership.user))
            ).all()

    @rx.event
    def invite_member(self, form_data: dict):
        if not self.is_admin:
            return rx.toast("Only Admins or Owners can invite members.")
        email = form_data.get("email")
        role = form_data.get("role")
        if not email or not role:
            return rx.toast("Email and role are required.")
        with rx.session() as session:
            user = session.exec(
                sqlmodel.select(User).where(User.email == email)
            ).first()
            if not user:
                user = User(
                    username=email.split("@")[0], email=email, password_hash=None
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            existing = session.exec(
                sqlmodel.select(Membership).where(
                    Membership.user_id == user.id,
                    Membership.tenant_id == self.current_tenant.id,
                )
            ).first()
            if existing:
                return rx.toast(f"User {email} is already a member.")
            new_membership = Membership(
                user_id=user.id, tenant_id=self.current_tenant.id, role=RoleEnum(role)
            )
            session.add(new_membership)
            self._log_audit(
                action="tenant.member.added",
                resource_crn=f"crn:colabe:{self.current_tenant.region}:{self.current_tenant.id}:user/{user.id}",
                after={"email": email, "role": role},
            )
            session.commit()
        self.load_members()
        return rx.toast(f"Invitation sent to {email}.")

    @rx.event
    def change_member_role(self, membership_id: int, new_role_str: str):
        if not self.is_admin:
            return rx.toast("Only Admins or Owners can change roles.")
        with rx.session() as session:
            membership = session.get(Membership, membership_id)
            if not membership or membership.tenant_id != self.current_tenant.id:
                return rx.toast("Membership not found.")
            if membership.role == RoleEnum.OWNER:
                return rx.toast("Cannot change the role of an Owner.")
            try:
                new_role = RoleEnum(new_role_str)
            except ValueError as e:
                logging.exception(f"Invalid role selected: {e}")
                return rx.toast("Invalid role selected.")
            old_role = membership.role.value
            membership.role = new_role
            session.add(membership)
            self._log_audit(
                action="tenant.member.role_changed",
                resource_crn=f"crn:colabe:{self.current_tenant.region}:{self.current_tenant.id}:user/{membership.user_id}",
                before={"role": old_role},
                after={"role": new_role.value},
            )
            session.commit()
        self.load_members()
        return rx.toast("Member role updated successfully.")

    @rx.event
    def remove_member(self, membership_id: int):
        if not self.is_admin:
            return rx.toast("Only Admins or Owners can remove members.")
        with rx.session() as session:
            membership = session.get(Membership, membership_id)
            if not membership or membership.tenant_id != self.current_tenant.id:
                return rx.toast("Membership not found.")
            if membership.role == RoleEnum.OWNER:
                return rx.toast("Cannot remove the Owner.")
            removed_email = membership.user.email
            session.delete(membership)
            self._log_audit(
                action="tenant.member.removed",
                resource_crn=f"crn:colabe:{self.current_tenant.region}:{self.current_tenant.id}:user/{membership.user_id}",
                before={"email": removed_email, "role": membership.role.value},
            )
            session.commit()
        self.load_members()
        return rx.toast(f"Member {removed_email} removed.")