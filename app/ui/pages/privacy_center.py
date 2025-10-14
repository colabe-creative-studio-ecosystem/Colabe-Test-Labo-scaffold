import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.pages.index import landing_header, footer
from app.ui.styles import card_style


def privacy_center_page() -> rx.Component:
    return rx.el.div(
        landing_header(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    "Privacy Center",
                    class_name="text-4xl md:text-5xl font-bold tracking-tighter title-gradient",
                ),
                rx.el.p(
                    "Manage your personal data and exercise your privacy rights.",
                    class_name="mt-4 text-lg md:text-xl text-text-secondary max-w-2xl text-center",
                ),
                class_name="py-16 text-center",
            ),
            rx.el.div(
                rx.cond(
                    LegalState.dsr_status == "completed",
                    dsr_completed_view(),
                    dsr_form_view(),
                ),
                class_name="max-w-2xl mx-auto p-8",
                **card_style("cyan"),
            ),
            class_name="container mx-auto",
        ),
        footer(),
        class_name="colabe-bg min-h-screen text-text-primary font-['Inter']",
        on_mount=LegalState.on_load_legal,
    )


def dsr_form_view() -> rx.Component:
    return rx.el.form(
        rx.el.h2("Data Subject Request", class_name="text-2xl font-bold mb-6"),
        rx.cond(
            LegalState.is_logged_in,
            authenticated_dsr_form(),
            unauthenticated_dsr_form(),
        ),
        on_submit=LegalState.submit_dsr_request,
    )


def authenticated_dsr_form() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "You are logged in as ",
            rx.el.strong(LegalState.dsr_email),
            ".",
            class_name="mb-4",
        ),
        dsr_request_type_selector(),
        rx.el.button(
            "Submit Request",
            type="submit",
            class_name="w-full mt-6 px-6 py-3 bg-accent-cyan text-bg-base rounded-lg font-semibold hover:opacity-90 transition-opacity",
        ),
    )


def unauthenticated_dsr_form() -> rx.Component:
    return rx.el.div(
        rx.cond(
            ~LegalState.dsr_code_sent,
            rx.el.div(
                rx.el.label("Email Address", class_name="font-semibold"),
                rx.el.input(
                    name="email",
                    placeholder="your@email.com",
                    type="email",
                    required=True,
                    class_name="w-full mt-2 bg-bg-base border border-white/20 rounded-lg p-3",
                ),
                rx.el.button(
                    "Send Verification Code",
                    type="submit",
                    class_name="w-full mt-6 px-6 py-3 bg-accent-cyan text-bg-base rounded-lg font-semibold hover:opacity-90 transition-opacity",
                ),
            ),
            rx.el.div(
                rx.el.p(f"A verification code was sent to {LegalState.dsr_email}."),
                rx.el.label("Verification Code", class_name="font-semibold mt-4"),
                rx.el.input(
                    name="code",
                    placeholder="123456",
                    required=True,
                    class_name="w-full mt-2 bg-bg-base border border-white/20 rounded-lg p-3",
                ),
                dsr_request_type_selector(),
                rx.el.button(
                    "Verify and Submit",
                    on_click=LegalState.verify_dsr_code,
                    class_name="w-full mt-6 px-6 py-3 bg-accent-cyan text-bg-base rounded-lg font-semibold hover:opacity-90 transition-opacity",
                ),
            ),
        ),
        rx.cond(
            LegalState.dsr_error_message != "",
            rx.el.p(LegalState.dsr_error_message, class_name="text-danger mt-4"),
        ),
    )


def dsr_request_type_selector() -> rx.Component:
    return rx.el.div(
        rx.el.label("Request Type", class_name="font-semibold"),
        rx.el.select(
            ["Access/Export", "Delete"],
            name="request_type",
            default_value="export",
            on_change=LegalState.set_dsr_request_type,
            class_name="w-full mt-2 bg-bg-base border border-white/20 rounded-lg p-3",
        ),
        rx.el.p(
            "Deletion is irreversible and will be processed according to our retention policy.",
            class_name="text-sm text-text-secondary mt-2",
        ),
        class_name="mt-6",
    )


def dsr_completed_view() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Request Status", class_name="text-2xl font-bold mb-6 text-center"),
        rx.el.div(
            status_timeline_item("Received", "check", LegalState.dsr_status),
            status_timeline_item("In Progress", "loader", LegalState.dsr_status),
            status_timeline_item("Completed", "check_check", LegalState.dsr_status),
            class_name="flex justify-between items-center my-8",
        ),
        rx.cond(
            LegalState.dsr_status == "completed",
            rx.el.div(
                rx.el.p("Your request has been completed."),
                rx.cond(
                    LegalState.dsr_request_type == "export",
                    rx.el.a(
                        "Download Your Data",
                        href="/placeholder_export.zip",
                        class_name="mt-4 inline-block text-accent-cyan hover:underline",
                    ),
                ),
                class_name="text-center",
            ),
            rx.el.div(
                rx.el.p(
                    "Your request is being processed. This may take up to 30 days. You will receive an email confirmation once it's complete."
                ),
                class_name="text-center text-text-secondary",
            ),
        ),
    )


def get_status_class(name: str, current_status: rx.Var[str]) -> rx.Var[str]:
    base_class = "w-12 h-12 rounded-full flex items-center justify-center "
    name_lower = name.lower().replace(" ", "_")
    status_order = rx.Var.create(["received", "in_progress", "completed"])
    is_valid_status_name = status_order.contains(name_lower)
    status_indices = {"received": 0, "in_progress": 1, "completed": 2}
    i = rx.Var.create(status_indices.get(name_lower, -1))
    return rx.cond(
        is_valid_status_name,
        rx.match(
            current_status,
            (
                "received",
                rx.cond(
                    i < 0,
                    base_class + "bg-accent-cyan text-bg-base",
                    base_class
                    + "bg-bg-base border border-white/20 text-text-secondary",
                ),
            ),
            (
                "in_progress",
                rx.cond(
                    i < 1,
                    base_class + "bg-accent-cyan text-bg-base",
                    rx.cond(
                        i == 1,
                        base_class + "bg-accent-yellow text-bg-base animate-pulse",
                        base_class
                        + "bg-bg-base border border-white/20 text-text-secondary",
                    ),
                ),
            ),
            (
                "completed",
                rx.cond(
                    i < 2,
                    base_class + "bg-accent-cyan text-bg-base",
                    rx.cond(
                        i == 2,
                        base_class + "bg-accent-cyan text-bg-base",
                        base_class
                        + "bg-bg-base border border-white/20 text-text-secondary",
                    ),
                ),
            ),
            base_class + "bg-bg-base border border-white/20 text-text-secondary",
        ),
        base_class + "bg-bg-base border border-white/20 text-text-secondary",
    )


def status_timeline_item(
    name: str, icon: str, current_status: rx.Var[str]
) -> rx.Component:
    return rx.el.div(
        rx.el.div(rx.icon(icon), class_name=get_status_class(name, current_status)),
        rx.el.p(name, class_name="mt-2 text-sm font-semibold"),
        class_name="flex flex-col items-center text-center",
    )