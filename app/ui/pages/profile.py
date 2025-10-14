import reflex as rx
from app.ui.states.auth_state import AuthState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def profile_page() -> rx.Component:
    return rx.el.div(sidebar(), profile_content(), class_name=page_style)


def profile_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.h1("User Profile", class_name="text-2xl font-bold title-gradient"),
            class_name=header_style,
        ),
        rx.el.div(
            rx.cond(
                AuthState.is_logged_in,
                rx.el.div(
                    user_info_card(),
                    roles_card(),
                    sessions_card(),
                    class_name="p-8 grid grid-cols-1 lg:grid-cols-2 gap-8",
                ),
                rx.el.p("Loading profile..."),
            ),
            class_name="flex-1",
        ),
        class_name=page_content_style,
    )


def user_info_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Your Information", class_name="text-xl font-semibold mb-4"),
        rx.el.div(
            rx.image(
                src=f"https://api.dicebear.com/9.x/initials/svg?seed={AuthState.user.username}",
                class_name="h-24 w-24 rounded-full",
            ),
            rx.el.div(
                rx.el.p(AuthState.user.username, class_name="text-2xl font-bold"),
                rx.el.p(AuthState.user.email, class_name="text-text-secondary"),
                rx.el.div(
                    rx.el.span("2FA Status:"),
                    rx.el.span(
                        rx.cond(AuthState.user.has_2fa, "Enabled", "Disabled"),
                        class_name=rx.cond(
                            AuthState.user.has_2fa, "text-success", "text-warning"
                        ),
                    ),
                    class_name="flex items-center gap-2 mt-2",
                ),
            ),
            class_name="flex items-center gap-6",
        ),
        **card_style("cyan"),
    )


def roles_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Your Roles", class_name="text-xl font-semibold mb-4"),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Tenant", class_name="p-2 text-left"),
                        rx.el.th("Role", class_name="p-2 text-left"),
                    )
                ),
                rx.el.tbody(rx.foreach(AuthState.memberships, render_role_row)),
            ),
            class_name="w-full",
        ),
        **card_style("magenta"),
    )


def render_role_row(membership: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(membership.tenant.name, class_name="p-2"),
        rx.el.td(
            rx.el.span(
                membership.role,
                class_name="px-2 py-1 text-xs font-semibold rounded-full bg-accent-gold/20 text-accent-gold",
            ),
            class_name="p-2",
        ),
        class_name="border-t border-white/10",
    )


def sessions_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Active Sessions", class_name="text-xl font-semibold mb-4"),
        rx.el.p(
            "For security, you can revoke sessions on other devices.",
            class_name="text-text-secondary mb-4",
        ),
        rx.el.button(
            "Revoke All Other Sessions",
            on_click=lambda: rx.toast("Functionality not yet implemented."),
            class_name="px-4 py-2 bg-danger text-white font-semibold rounded-lg hover:opacity-90",
        ),
        **card_style("gold"),
    )