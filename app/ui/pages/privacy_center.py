import reflex as rx
from app.ui.states.privacy_center_state import PrivacyCenterState
from app.ui.pages.legal import legal_page_layout
from app.ui.styles import card_style


def privacy_center_page() -> rx.Component:
    return legal_page_layout(
        rx.el.main(
            rx.el.header(
                rx.el.div(
                    rx.el.h1(
                        "Privacy Center",
                        class_name="text-3xl font-bold text-text-primary title-gradient",
                    ),
                    rx.el.p(
                        "Manage your data subject rights.",
                        class_name="text-text-secondary",
                    ),
                ),
                class_name="p-8 border-b border-white/10",
            ),
            rx.el.div(
                rx.cond(
                    PrivacyCenterState.is_verifying, verification_form(), dsr_form()
                ),
                rx.cond(PrivacyCenterState.is_logged_in, requests_history()),
                class_name="p-8 grid grid-cols-1 lg:grid-cols-2 gap-8 items-start",
            ),
            class_name="flex-1",
        )
    )


def dsr_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Submit a New Request",
            class_name="text-xl font-semibold text-text-primary mb-4",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "Request Type", class_name="text-sm font-medium text-text-secondary"
                ),
                rx.el.select(
                    ["access", "delete"],
                    default_value=PrivacyCenterState.request_type,
                    on_change=PrivacyCenterState.set_request_type,
                    class_name="w-full mt-1 p-2 rounded-lg bg-bg-base border border-white/10",
                ),
                class_name="space-y-1",
            ),
            rx.cond(
                ~PrivacyCenterState.is_logged_in,
                rx.el.div(
                    rx.el.label(
                        "Email Address",
                        class_name="text-sm font-medium text-text-secondary",
                    ),
                    rx.el.input(
                        name="email",
                        placeholder="your@email.com",
                        type="email",
                        class_name="w-full mt-1 p-2 rounded-lg bg-bg-base border border-white/10",
                    ),
                    class_name="space-y-1",
                ),
            ),
            rx.el.button(
                "Submit Request",
                type="submit",
                class_name="w-full py-2 px-4 mt-4 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
            ),
            rx.cond(
                PrivacyCenterState.form_message,
                rx.el.p(
                    PrivacyCenterState.form_message,
                    class_name="mt-4 text-sm text-accent-gold",
                ),
            ),
            on_submit=PrivacyCenterState.handle_dsr_submit,
            class_name="space-y-4",
        ),
        **card_style("cyan"),
    )


def verification_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Verify Your Email",
            class_name="text-xl font-semibold text-text-primary mb-4",
        ),
        rx.el.p(
            f"A verification code was sent to {PrivacyCenterState.email}. Please enter it below.",
            class_name="text-sm text-text-secondary",
        ),
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "Verification Code",
                    class_name="text-sm font-medium text-text-secondary",
                ),
                rx.el.input(
                    name="verification_code",
                    placeholder="ABCDEF",
                    class_name="w-full mt-1 p-2 rounded-lg bg-bg-base border border-white/10 tracking-widest text-center",
                ),
                class_name="space-y-1",
            ),
            rx.el.div(
                rx.el.button(
                    "Verify",
                    type="submit",
                    class_name="w-full py-2 px-4 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
                ),
                rx.el.button(
                    "Cancel",
                    on_click=PrivacyCenterState.cancel_verification,
                    type="button",
                    class_name="w-full py-2 px-4 bg-danger/50 text-text-primary font-semibold rounded-lg hover:bg-danger",
                ),
                class_name="flex gap-4 mt-4",
            ),
            rx.cond(
                PrivacyCenterState.form_message,
                rx.el.p(
                    PrivacyCenterState.form_message,
                    class_name="mt-4 text-sm text-accent-gold",
                ),
            ),
            on_submit=PrivacyCenterState.handle_verification,
            class_name="space-y-4",
        ),
        **card_style("gold"),
    )


def requests_history() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Your Request History",
            class_name="text-xl font-semibold text-text-primary mb-4",
        ),
        rx.cond(
            PrivacyCenterState.user_has_requests,
            rx.el.ul(
                rx.foreach(PrivacyCenterState.dsr_list, render_dsr_item),
                class_name="space-y-4",
            ),
            rx.el.p("You have no past requests.", class_name="text-text-secondary"),
        ),
        **card_style("magenta"),
    )


def render_dsr_item(dsr: rx.Var) -> rx.Component:
    return rx.el.li(
        rx.el.div(
            rx.el.span(
                dsr.request_type.capitalize(), class_name="font-semibold capitalize"
            ),
            rx.el.span(
                dsr.status,
                class_name=rx.cond(
                    dsr.status == "completed", "text-success", "text-warning"
                )
                + " text-xs font-bold uppercase px-2 py-1 rounded-full bg-bg-base",
            ),
            class_name="flex justify-between items-center",
        ),
        rx.el.p(
            f"Submitted on {dsr.created_at.to_string()}",
            class_name="text-sm text-text-secondary",
        ),
        class_name="p-4 rounded-lg bg-bg-base",
    )