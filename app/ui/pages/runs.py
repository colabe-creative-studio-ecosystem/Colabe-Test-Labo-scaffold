import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.run_state import RunState
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style
from app.core.models import Run


def runs_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    runs_content(), footer(), class_name="flex-1 flex flex-col min-w-0"
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=RunState.load_data,
    )


def runs_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Live Runs",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Monitor test execution progress and history.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Status",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Test Plan",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Project",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Started At",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Actions",
                                class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                            ),
                        )
                    ),
                    rx.el.tbody(
                        rx.foreach(RunState.runs, render_run_row),
                        class_name="divide-y divide-white/10",
                    ),
                    class_name="min-w-full divide-y divide-white/10",
                ),
                class_name="overflow-hidden rounded-xl border border-white/10 bg-[#0E1520]",
            ),
            class_name="p-8 flex-1",
        ),
        class_name=page_content_style,
    )


from app.ui.states.run_state import RunDisplay


def render_run_row(run: RunDisplay) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.span(
                run.status,
                class_name=rx.cond(
                    run.status == "running",
                    "px-2 py-1 text-xs font-semibold rounded-full bg-[#00E5FF]/20 text-[#00E5FF]",
                    rx.cond(
                        run.status == "completed",
                        "px-2 py-1 text-xs font-semibold rounded-full bg-green-500/20 text-green-200",
                        "px-2 py-1 text-xs font-semibold rounded-full bg-gray-500/20 text-gray-200",
                    ),
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.cond(run.test_plan, run.test_plan.name, "Deleted Plan"),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]",
        ),
        rx.el.td(
            rx.cond(
                run.test_plan,
                rx.cond(run.test_plan.project, run.test_plan.project.name, "-"),
                "-",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]",
        ),
        rx.el.td(
            rx.cond(run.started_at, run.started_at, "Not started"),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("trash-2", size=16),
                on_click=RunState.delete_run(run.id),
                class_name="text-gray-500 hover:text-[#FF3B3B] transition-colors",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm",
        ),
    )