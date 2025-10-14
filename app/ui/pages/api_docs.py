import reflex as rx
from app.ui.states.auth_state import AuthState


def api_docs_page() -> rx.Component:
    """A page that redirects to the new API docs page."""
    return rx.el.div(
        rx.el.p("Redirecting to API documentation..."),
        on_mount=rx.redirect("/api-center/rest"),
    )