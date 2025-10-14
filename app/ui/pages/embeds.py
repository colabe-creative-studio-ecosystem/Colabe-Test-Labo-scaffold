import reflex as rx
import jwt
import logging
from app.core.settings import settings
from app.ui.states.auth_state import AuthState


class EmbedPageState(AuthState):
    is_valid_token: bool = False
    error_message: str = "Loading widget..."
    loaded_widget_type: str = ""
    resource_id: str = ""

    @rx.var
    def token(self) -> str:
        return self.router.page.params.get("token", "")

    @rx.event
    def verify_token(self):
        token = self.token
        if not token:
            self.error_message = "Error: Missing token."
            self.is_valid_token = False
            return
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            self.is_valid_token = True
            self.loaded_widget_type = self.router.page.params.get(
                "widget_type", "unknown"
            )
            self.resource_id = payload.get("resource", "unknown").split(":")[-1]
        except jwt.ExpiredSignatureError as e:
            logging.exception(e)
            self.error_message = "Error: Token has expired."
            self.is_valid_token = False
        except jwt.InvalidTokenError as e:
            logging.exception(e)
            self.error_message = "Error: Invalid token."
            self.is_valid_token = False


def embed_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            EmbedPageState.is_valid_token,
            render_widget(),
            rx.el.div(
                rx.icon("flag_triangle_right", class_name="text-danger"),
                rx.el.h1("Access Denied", class_name="text-xl font-bold"),
                rx.el.p(EmbedPageState.error_message, class_name="text-text-secondary"),
                class_name="flex flex-col items-center justify-center gap-4 p-8",
            ),
        ),
        class_name="min-h-screen colabe-bg text-text-primary flex items-center justify-center font-['Inter']",
        on_mount=EmbedPageState.verify_token,
    )


def render_widget() -> rx.Component:
    return rx.match(
        EmbedPageState.loaded_widget_type,
        ("runs", runs_widget()),
        ("coverage", coverage_widget()),
        rx.el.p(f"Unknown widget type: {EmbedPageState.loaded_widget_type}"),
    )


def runs_widget() -> rx.Component:
    return rx.el.div(
        rx.el.h2(f"Run Details: {EmbedPageState.resource_id}", class_name="font-bold"),
        rx.el.p("This is a read-only embedded view of the run."),
        class_name="p-4 border border-accent-cyan/50 rounded-lg bg-bg-elevated",
    )


def coverage_widget() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            f"Coverage for Project: {EmbedPageState.resource_id}",
            class_name="font-bold",
        ),
        rx.el.p("This is a read-only embedded view of project coverage."),
        class_name="p-4 border border-accent-magenta/50 rounded-lg bg-bg-elevated",
    )