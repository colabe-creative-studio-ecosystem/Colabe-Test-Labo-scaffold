import reflex as rx
from app.ui.states.member_state import MemberState
from app.core.models import Membership, RoleEnum
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def members_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        members_content(),
        class_name=page_style,
        on_mount=MemberState.load_members,
    )


def members_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.h1(
                "Member Management", class_name="text-2xl font-bold title-gradient"
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.cond(
                MemberState.is_admin,
                rx.el.div(
                    invite_member_card(),
                    members_list_card(),
                    class_name="p-8 grid grid-cols-1 lg:grid-cols-2 gap-8",
                ),
                rx.el.div(
                    "You must be an Admin or Owner to manage members.",
                    class_name="p-8 text-warning",
                ),
            )
        ),
        class_name=page_content_style,
    )


def invite_member_card() -> rx.Component:
    return rx.el.form(
        rx.el.h2("Invite New Member", class_name="text-xl font-semibold mb-4"),
        rx.el.input(
            name="email",
            type="email",
            placeholder="new.member@example.com",
            class_name="w-full mt-1 p-2 rounded-lg bg-bg-base border border-white/20",
        ),
        rx.el.select(
            [role.value for role in RoleEnum if role != RoleEnum.OWNER],
            name="role",
            default_value=RoleEnum.VIEWER.value,
            class_name="w-full mt-4 p-2 rounded-lg bg-bg-base border border-white/20",
        ),
        rx.el.button(
            "Send Invite",
            type="submit",
            class_name="mt-6 w-full py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
        ),
        on_submit=MemberState.invite_member,
        reset_on_submit=True,
        **card_style("cyan"),
    )


def members_list_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Current Members", class_name="text-xl font-semibold mb-4"),
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("User", class_name="p-2 text-left"),
                    rx.el.th("Role", class_name="p-2 text-left"),
                    rx.el.th("Actions", class_name="p-2 text-left"),
                )
            ),
            rx.el.tbody(rx.foreach(MemberState.members, render_member_row)),
            class_name="w-full",
        ),
        **card_style("magenta"),
    )


def render_member_row(membership: Membership) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.image(
                    src=f"https://api.dicebear.com/9.x/initials/svg?seed={membership.user.username}",
                    class_name="h-8 w-8 rounded-full mr-3",
                ),
                rx.el.div(
                    rx.el.p(membership.user.username, class_name="font-semibold"),
                    rx.el.p(membership.user.email, class_name="text-text-secondary"),
                ),
                class_name="flex items-center",
            ),
            class_name="p-2",
        ),
        rx.el.td(
            rx.el.select(
                [role.value for role in RoleEnum if role != RoleEnum.OWNER],
                value=membership.role,
                on_change=lambda new_role: MemberState.change_member_role(
                    membership.id, new_role
                ),
                disabled=membership.role == RoleEnum.OWNER,
                class_name="bg-bg-base border border-white/20 rounded-lg p-1",
            ),
            class_name="p-2",
        ),
        rx.el.td(
            rx.el.button(
                "Remove",
                on_click=lambda: MemberState.remove_member(membership.id),
                disabled=membership.role == RoleEnum.OWNER,
                class_name="px-2 py-1 text-xs bg-danger text-white rounded disabled:opacity-50",
            ),
            class_name="p-2",
        ),
        class_name="border-t border-white/10",
    )