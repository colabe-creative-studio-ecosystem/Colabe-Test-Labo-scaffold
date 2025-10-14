import reflex as rx
from app.ui.states.run_state import RunState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.core.models import RunStep


def run_console_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            RunState.is_logged_in,
            rx.el.div(sidebar(), run_console_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=RunState.load_run_details,
    )


def run_console_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    f"Run: {RunState.run.id.to_string()}",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    f"Status: {RunState.run.status}", class_name=f"text-text-secondary"
                ),
            ),
            rx.el.button(
                "Re-run", on_click=lambda: RunState.start_run(RunState.run.id)
            ),
            class_name=header_style,
        ),
        rx.el.div(
            run_timeline(),
            run_details(),
            class_name="p-8 grid grid-cols-1 lg:grid-cols-3 gap-6",
        ),
        class_name=page_content_style,
    )


def run_timeline() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Timeline", class_name="text-xl font-semibold mb-4"),
        rx.el.div(
            rx.foreach(RunState.run_steps_with_duration, render_run_step),
            class_name="space-y-4",
        ),
        **card_style(accent_color="cyan"),
        class_name="lg:col-span-2",
    )


def get_step_icon(step_name: rx.Var[str]) -> rx.Component:
    return rx.match(
        step_name,
        ("discover", rx.icon("search", class_name="h-5 w-5")),
        ("static", rx.icon("file-scan", class_name="h-5 w-5")),
        ("unit", rx.icon("beaker", class_name="h-5 w-5")),
        ("security", rx.icon("shield", class_name="h-5 w-5")),
        ("sbom", rx.icon("package", class_name="h-5 w-5")),
        ("summarize", rx.icon("message-square-text", class_name="h-5 w-5")),
        rx.icon("chevron-right", class_name="h-5 w-5"),
    )


def get_status_color_class(status: rx.Var[str]) -> rx.Var[str]:
    return rx.match(
        status,
        ("completed", "text-success font-semibold w-24 text-right"),
        ("running", "text-accent-yellow animate-pulse font-semibold w-24 text-right"),
        ("failed", "text-danger font-semibold w-24 text-right"),
        ("skipped", "text-text-secondary font-semibold w-24 text-right"),
        ("pending", "text-text-secondary font-semibold w-24 text-right"),
        "text-text-secondary font-semibold w-24 text-right",
    )


def render_run_step(step: dict) -> rx.Component:
    return rx.el.div(
        get_step_icon(step["name"]),
        rx.el.p(step["name"].to_string().capitalize(), class_name="font-medium"),
        rx.el.div(class_name="flex-grow"),
        rx.el.p(step["duration"], class_name="text-sm text-text-secondary"),
        rx.el.p(
            step["status"].to_string().capitalize(),
            class_name=get_status_color_class(step["status"]),
        ),
        class_name="flex items-center gap-4",
    )


def run_details() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Details", class_name="text-xl font-semibold mb-4"),
        rx.el.div(
            detail_item("Status", RunState.run.status),
            detail_item(
                "Started",
                rx.cond(RunState.run.started_at, RunState.run.started_at, "N/A"),
            ),
            detail_item(
                "Completed",
                rx.cond(RunState.run.completed_at, RunState.run.completed_at, "N/A"),
            ),
            detail_item("Test Plan ID", RunState.run.test_plan_id.to_string()),
            class_name="space-y-2",
        ),
        **card_style(accent_color="magenta"),
    )


def detail_item(label: str, value: rx.Var) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-text-secondary"),
        rx.el.p(value, class_name="font-semibold"),
        class_name="flex justify-between",
    )