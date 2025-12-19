import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.test_plan_state import TestPlanState
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.core.models import TestPlan
from app.ui.states.test_plan_state import TestPlanDisplay


def test_plans_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    test_plans_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def test_plans_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Test Plans",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Create and manage your test execution plans.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            create_plan_section(),
            rx.cond(
                TestPlanState.test_plans.length() > 0,
                rx.el.div(
                    rx.foreach(TestPlanState.test_plans, plan_card),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                ),
                rx.el.div(
                    rx.icon(
                        "file-check",
                        size=48,
                        class_name="text-[#A9B3C1] opacity-50 mb-4",
                    ),
                    rx.el.p(
                        "No test plans found. Create one to get started.",
                        class_name="text-[#A9B3C1]",
                    ),
                    class_name="flex flex-col items-center justify-center py-20 bg-[#0E1520]/50 rounded-xl border border-dashed border-white/10",
                ),
            ),
            class_name="p-8 flex-1",
        ),
        class_name=page_content_style,
    )


def create_plan_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "New Test Plan", class_name="text-lg font-semibold text-[#E8F0FF] mb-4"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.label(
                    "Project",
                    class_name="block text-sm font-medium text-[#A9B3C1] mb-1",
                ),
                rx.el.select(
                    rx.foreach(
                        TestPlanState.projects,
                        lambda p: rx.el.option(p.name, value=p.id.to_string()),
                    ),
                    on_change=TestPlanState.set_selected_project_id,
                    value=TestPlanState.selected_project_id,
                    class_name="w-full bg-[#0A0F14] border border-white/10 text-[#E8F0FF] rounded-lg px-3 py-2 focus:outline-none focus:border-[#00E5FF]",
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Plan Name",
                    class_name="block text-sm font-medium text-[#A9B3C1] mb-1",
                ),
                rx.el.input(
                    placeholder="e.g., Nightly Regression",
                    on_change=TestPlanState.set_new_plan_name,
                    class_name="w-full bg-[#0A0F14] border border-white/10 text-[#E8F0FF] rounded-lg px-3 py-2 focus:outline-none focus:border-[#00E5FF]",
                    default_value=TestPlanState.new_plan_name,
                ),
                class_name="flex-1",
            ),
            rx.el.div(
                rx.el.label(
                    "Action",
                    class_name="block text-sm font-medium text-transparent mb-1",
                ),
                rx.el.button(
                    "Create Plan",
                    on_click=TestPlanState.create_test_plan,
                    class_name="w-full bg-[#00E5FF] text-[#0A0F14] font-bold py-2 px-4 rounded-lg hover:opacity-90 transition-opacity",
                ),
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4 items-end",
        ),
        class_name="mb-8 p-6 bg-[#0E1520] rounded-xl border border-white/5 shadow-lg",
    )


def plan_card(plan: TestPlanDisplay) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("file-check", size=24, class_name="text-[#00E5FF]"),
                class_name="p-3 rounded-lg bg-[#0A0F14] border border-white/5",
            ),
            rx.el.button(
                rx.icon("trash-2", size=18),
                on_click=TestPlanState.delete_test_plan(plan.id),
                class_name="text-gray-500 hover:text-[#FF3B3B] transition-colors p-2",
            ),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.h3(
            plan.name, class_name="text-xl font-bold text-[#E8F0FF] mb-1 truncate"
        ),
        rx.el.p(
            rx.cond(plan.project, plan.project.name, "Unknown Project"),
            class_name="text-sm text-[#A9B3C1] mb-4",
        ),
        rx.el.div(
            rx.el.p(
                "Created", class_name="text-xs text-[#A9B3C1] uppercase tracking-wider"
            ),
            rx.el.p(plan.created_at, class_name="text-sm text-[#E8F0FF] font-medium"),
            class_name="pt-4 border-t border-white/5",
        ),
        **card_style("cyan"),
    )