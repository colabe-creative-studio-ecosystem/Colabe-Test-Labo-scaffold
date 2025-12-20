import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.policy_state import PolicyState
from app.ui.states.auth_state import AuthState
from app.core.models import SeverityEnum, AutofixScopeEnum
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style

SEVERITY_OPTIONS = [s.value for s in SeverityEnum]
AUTOFIX_SCOPE_OPTIONS = [s.value for s in AutofixScopeEnum]


def policies_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    policies_page_content(),
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


def policies_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Project Policies",
                    class_name="text-2xl font-bold text-[#D8B76E] drop-shadow-[0_0_10px_rgba(216,183,110,0.3)]",
                ),
                rx.el.p(
                    "Manage gates, SLAs, and automation rules for your project.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.cond(
                PolicyState.project_policy,
                rx.el.div(
                    policy_form(),
                    merge_status_card(),
                    class_name="grid grid-cols-1 lg:grid-cols-3 gap-8",
                ),
                rx.el.p("Loading policies...", class_name="text-[#A9B3C1]"),
            ),
            class_name="p-8 flex-1",
        ),
        class_name=page_content_style,
    )


def policy_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Policy Configuration",
            class_name="text-xl font-semibold text-[#00E5FF] mb-6 drop-shadow-[0_0_5px_rgba(0,229,255,0.3)]",
        ),
        policy_item(
            "Blocking Severity",
            "Block merges if findings of this severity or higher are present.",
            rx.el.select(
                rx.foreach(SEVERITY_OPTIONS, lambda x: rx.el.option(x, value=x)),
                default_value=PolicyState.project_policy.blocking_severity,
                on_change=PolicyState.set_blocking_severity,
                class_name="mt-1 block w-full pl-3 pr-10 py-2 text-base bg-[#0A0F14] text-[#E8F0FF] border border-white/10 rounded-md focus:outline-none focus:border-[#00E5FF] focus:shadow-[0_0_10px_-2px_#00E5FF] transition-all sm:text-sm",
            ),
        ),
        policy_item(
            "Minimum Code Coverage",
            "Minimum test coverage required to pass.",
            rx.el.div(
                rx.el.input(
                    type="number",
                    default_value=PolicyState.project_policy.min_coverage_percent,
                    on_change=PolicyState.set_min_coverage,
                    class_name="mt-1 block w-full pl-3 pr-10 py-2 text-base bg-[#0A0F14] text-[#E8F0FF] border border-white/10 rounded-md focus:outline-none focus:border-[#00E5FF] focus:shadow-[0_0_10px_-2px_#00E5FF] transition-all sm:text-sm",
                ),
                rx.el.p("%", class_name="ml-2 text-[#00E5FF] font-bold"),
                class_name="flex items-center",
            ),
        ),
        policy_item(
            "Autofix Scope",
            "Define which categories of issues are eligible for autofix.",
            rx.el.select(
                rx.foreach(AUTOFIX_SCOPE_OPTIONS, lambda x: rx.el.option(x, value=x)),
                default_value=PolicyState.project_policy.autofix_scope,
                on_change=PolicyState.set_autofix_scope,
                class_name="mt-1 block w-full pl-3 pr-10 py-2 text-base bg-[#0A0F14] text-[#E8F0FF] border border-white/10 rounded-md focus:outline-none focus:border-[#00E5FF] focus:shadow-[0_0_10px_-2px_#00E5FF] transition-all sm:text-sm",
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
                        "text-[#A9B3C1]",
                        "font-semibold text-[#FF3CF7]",
                    ),
                ),
                rx.el.button(
                    rx.el.span(
                        class_name=rx.cond(
                            PolicyState.project_policy.auto_merge_enabled,
                            "translate-x-5 inline-block h-5 w-5 rounded-full bg-white transform ring-0 transition ease-in-out duration-200",
                            "translate-x-0 inline-block h-5 w-5 rounded-full bg-gray-400 transform ring-0 transition ease-in-out duration-200",
                        )
                    ),
                    class_name=rx.cond(
                        PolicyState.project_policy.auto_merge_enabled,
                        "bg-[#FF3CF7] relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#FF3CF7] shadow-[0_0_10px_#FF3CF7]",
                        "bg-gray-700 relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#FF3CF7]",
                    ),
                    on_click=PolicyState.update_policy(
                        "auto_merge_enabled",
                        rx.cond(
                            PolicyState.project_policy.auto_merge_enabled,
                            "false",
                            "true",
                        ),
                    ),
                ),
                rx.el.span(
                    "Enabled",
                    class_name=rx.cond(
                        PolicyState.project_policy.auto_merge_enabled,
                        "font-semibold text-[#FF3CF7]",
                        "text-[#A9B3C1]",
                    ),
                ),
                class_name="flex items-center space-x-3 mt-1",
            ),
        ),
        class_name="col-span-1 lg:col-span-2 bg-[#0E1520] p-6 rounded-xl border border-[#D8B76E]/20 shadow-[0_0_20px_-5px_rgba(216,183,110,0.1)] space-y-6",
    )


def policy_item(title: str, description: str, control: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h3(title, class_name="font-medium text-[#FF3CF7]"),
            rx.el.p(description, class_name="text-sm text-[#A9B3C1]"),
        ),
        control,
        class_name="grid grid-cols-1 md:grid-cols-2 gap-4 items-center p-4 rounded-lg hover:bg-white/5 transition-colors border border-transparent hover:border-white/5",
    )


def merge_status_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Demo PR Merge Status", class_name="text-lg font-semibold text-[#E8F0FF]"
        ),
        rx.el.div(
            rx.cond(
                PolicyState.is_mergeable,
                rx.icon(
                    "circle_check_big",
                    class_name="text-[#00D68F] h-16 w-16 mx-auto drop-shadow-[0_0_10px_#00D68F]",
                ),
                rx.icon(
                    "message_circle_reply",
                    class_name="text-[#FF3B3B] h-16 w-16 mx-auto drop-shadow-[0_0_10px_#FF3B3B]",
                ),
            ),
            rx.el.p(
                rx.cond(PolicyState.is_mergeable, "Mergeable", "Blocked"),
                class_name="mt-2 text-2xl font-bold",
            ),
            class_name=rx.cond(
                PolicyState.is_mergeable, "text-[#00D68F]", "text-[#FF3B3B]"
            )
            + " text-center",
        ),
        rx.el.div(
            rx.el.h4(
                "Conditions:", class_name="font-semibold text-sm mb-2 text-[#E8F0FF]"
            ),
            merge_check_item(
                "Severity Gate",
                PolicyState.project_policy.blocking_severity.to_string() + " or higher",
                is_passing=PolicyState.is_mergeable,
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
        class_name="bg-[#0E1520] p-6 rounded-xl border border-[#D8B76E]/20 shadow-[0_0_20px_-5px_rgba(216,183,110,0.1)]",
    )


def merge_check_item(
    name: str, condition: str, is_passing: rx.Var[bool]
) -> rx.Component:
    return rx.el.div(
        rx.cond(
            is_passing,
            rx.icon("check", class_name="text-green-500 h-5 w-5"),
            rx.icon("x", class_name="text-red-500 h-5 w-5"),
        ),
        rx.el.p(name, class_name="font-medium"),
        rx.el.p(condition, class_name="text-gray-500 ml-auto"),
        class_name="flex items-center space-x-2",
    )