import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.policy_state import PolicyState
from app.core.models import SeverityEnum, AutofixScopeEnum
from app.ui.pages.index import sidebar, user_dropdown


def policies_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            PolicyState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    policies_page_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name="flex min-h-screen bg-gray-50 font-['Inter']",
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen",
            ),
        ),
        on_mount=PolicyState.load_policy,
    )


def policies_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Project Policies", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Manage gates, SLAs, and automation rules for your project.",
                    class_name="text-gray-500",
                ),
            ),
            user_dropdown(),
            class_name="flex items-center justify-between p-4 border-b bg-white",
        ),
        rx.el.div(
            rx.cond(
                PolicyState.project_policy,
                rx.el.div(
                    policy_form(),
                    merge_status_card(),
                    class_name="grid grid-cols-1 lg:grid-cols-3 gap-8",
                ),
                rx.el.p("Loading policies..."),
            ),
            class_name="p-8",
        ),
        class_name="flex-1 flex flex-col",
    )


def policy_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Policy Configuration", class_name="text-xl font-semibold text-gray-800"
        ),
        policy_item(
            "Blocking Severity",
            "Block merges if findings of this severity or higher are present.",
            rx.el.select(
                [s.value for s in SeverityEnum],
                default_value=PolicyState.project_policy.blocking_severity,
                on_change=lambda value: PolicyState.update_policy(
                    "blocking_severity", value
                ),
                class_name="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md",
            ),
        ),
        policy_item(
            "Minimum Code Coverage",
            "Minimum test coverage required to pass.",
            rx.el.div(
                rx.el.input(
                    type="number",
                    default_value=PolicyState.project_policy.min_coverage_percent,
                    on_change=lambda value: PolicyState.update_policy(
                        "min_coverage_percent", value
                    ),
                    class_name="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md",
                ),
                rx.el.p("%", class_name="ml-2 text-gray-500"),
                class_name="flex items-center",
            ),
        ),
        policy_item(
            "Autofix Scope",
            "Define which categories of issues are eligible for autofix.",
            rx.el.select(
                [s.value for s in AutofixScopeEnum],
                default_value=PolicyState.project_policy.autofix_scope,
                on_change=lambda value: PolicyState.update_policy(
                    "autofix_scope", value
                ),
                class_name="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md",
            ),
        ),
        policy_item(
            "Auto-merge",
            "Automatically merge pull requests if all checks pass.",
            rx.el.div(
                rx.el.span(
                    "Disabled",
                    class_name=rx.cond(
                        PolicyState.project_policy.auto_merge_enabled,
                        "text-gray-500",
                        "font-semibold text-gray-900",
                    ),
                ),
                rx.el.button(
                    rx.el.span(
                        class_name=rx.cond(
                            PolicyState.project_policy.auto_merge_enabled,
                            "translate-x-5",
                            "translate-x-0",
                        )
                        + " inline-block h-5 w-5 rounded-full bg-white transform ring-0 transition ease-in-out duration-200"
                    ),
                    class_name=rx.cond(
                        PolicyState.project_policy.auto_merge_enabled,
                        "bg-blue-600",
                        "bg-gray-200",
                    )
                    + " relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500",
                    on_click=lambda: PolicyState.update_policy(
                        "auto_merge_enabled",
                        (~PolicyState.project_policy.auto_merge_enabled).to_string(),
                    ),
                ),
                rx.el.span(
                    "Enabled",
                    class_name=rx.cond(
                        PolicyState.project_policy.auto_merge_enabled,
                        "font-semibold text-gray-900",
                        "text-gray-500",
                    ),
                ),
                class_name="flex items-center space-x-3 mt-1",
            ),
        ),
        class_name="col-span-1 lg:col-span-2 bg-white p-6 rounded-xl border border-gray-200 shadow-sm space-y-6",
    )


def policy_item(title: str, description: str, control: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(title, class_name="font-medium text-gray-900"),
            rx.el.p(description, class_name="text-sm text-gray-500"),
        ),
        control,
        class_name="grid grid-cols-1 md:grid-cols-2 gap-4 items-center",
    )


def merge_status_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Demo PR Merge Status", class_name="text-lg font-semibold text-gray-800"
        ),
        rx.el.div(
            rx.icon(
                tag=rx.cond(PolicyState.is_mergeable, "check_circle", "x_circle"),
                class_name=rx.cond(
                    PolicyState.is_mergeable, "text-green-500", "text-red-500"
                )
                + " h-16 w-16 mx-auto",
            ),
            rx.el.p(
                rx.cond(PolicyState.is_mergeable, "Mergeable", "Blocked"),
                class_name="mt-2 text-2xl font-bold",
            ),
            class_name=rx.cond(
                PolicyState.is_mergeable, "text-green-600", "text-red-600"
            )
            + " text-center",
        ),
        rx.el.div(
            rx.el.h4("Conditions:", class_name="font-semibold text-sm mb-2"),
            merge_check_item(
                "Severity Gate",
                PolicyState.project_policy.blocking_severity.to_string() + " or higher",
                is_passing=~PolicyState.is_mergeable,
            ),
            merge_check_item(
                "Coverage Gate",
                "> "
                + PolicyState.project_policy.min_coverage_percent.to_string()
                + "%",
                is_passing=PolicyState.is_mergeable,
            ),
            class_name="mt-4 space-y-2 text-sm",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def merge_check_item(
    name: str, condition: str, is_passing: rx.Var[bool]
) -> rx.Component:
    return rx.el.div(
        rx.icon(
            tag=rx.cond(is_passing, "check", "x"),
            class_name=rx.cond(is_passing, "text-green-500", "text-red-500")
            + " h-5 w-5",
        ),
        rx.el.p(name, class_name="font-medium"),
        rx.el.p(condition, class_name="text-gray-500 ml-auto"),
        class_name="flex items-center space-x-2",
    )