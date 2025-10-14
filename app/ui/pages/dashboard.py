import reflex as rx
from app.ui.pages.index import sidebar, user_dropdown
from app.ui.states.auth_state import AuthState
from app.ui.states.dashboard_state import DashboardState
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.ui.components.help_copilot import help_copilot_shell


def dashboard_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                dashboard_content(),
                help_copilot_shell(),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=DashboardState.load_dashboard_data,
    )


def dashboard_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Dashboard",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    f"Welcome back, {AuthState.user.username}!",
                    class_name="text-text-secondary",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.icon("circle_play", class_name="mr-2"),
                    "Run Quick Sweep",
                    on_click=lambda: AuthState.cta_clicked("quick_sweep_dashboard"),
                    class_name="px-6 py-3 bg-accent-cyan text-bg-base rounded-lg font-semibold hover:opacity-90 transition-opacity flex items-center",
                ),
                rx.el.button(
                    rx.icon("circle_plus", class_name="mr-2"),
                    "New Project",
                    on_click=lambda: AuthState.cta_clicked("new_project_dashboard"),
                    class_name="px-6 py-3 bg-bg-elevated border border-white/20 text-text-primary rounded-lg font-semibold hover:bg-white/5 transition-colors flex items-center",
                ),
                class_name="flex items-center space-x-4",
            ),
            rx.el.div(
                recent_runs_card(),
                policy_gates_card(),
                autofix_queue_card(),
                usage_spend_card(),
                class_name="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6",
            ),
            rx.el.div(
                rx.el.h3(
                    "Live Event Stream",
                    class_name="text-lg font-semibold text-text-primary",
                ),
                rx.el.div(
                    rx.foreach(
                        DashboardState.live_events,
                        lambda event: rx.el.div(
                            rx.el.code(
                                f"[{event['timestamp']}]",
                                class_name="text-accent-cyan/80",
                            ),
                            rx.el.span(
                                event["message"], class_name="ml-4 text-text-secondary"
                            ),
                            class_name="font-mono text-sm",
                        ),
                    ),
                    class_name="mt-4 p-4 bg-bg-base rounded-lg h-48 overflow-y-auto space-y-2",
                ),
                class_name="mt-6 p-6",
                **card_style("magenta"),
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )


def status_chip(status: str) -> rx.Component:
    return rx.el.span(
        status,
        class_name=rx.cond(
            status == "PASSED",
            "bg-success/20 text-success",
            rx.cond(
                status == "FAILED",
                "bg-danger/20 text-danger",
                "bg-warning/20 text-warning",
            ),
        )
        + " px-2 py-1 text-xs font-semibold rounded-full",
    )


def recent_runs_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Recent Runs", class_name="text-lg font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            rx.foreach(
                DashboardState.recent_runs,
                lambda run: rx.el.div(
                    rx.el.p(run["name"], class_name="font-medium"),
                    rx.el.div(
                        status_chip(run["status"]),
                        rx.el.p(
                            f"{run['duration_s']}s",
                            class_name="text-sm text-text-secondary",
                        ),
                        class_name="flex items-center space-x-4",
                    ),
                    class_name="flex justify-between items-center",
                ),
            ),
            class_name="space-y-3",
        ),
        **card_style("cyan"),
    )


def policy_ring(name: str, value: int, color: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(f"{value}%", class_name="text-lg font-bold z-10"),
            rx.el.div(
                class_name="absolute inset-0 rounded-full bg-bg-elevated",
                style={
                    "background": f"conic-gradient(var(--accent-{color}) {value * 3.6}deg, transparent 0deg)"
                },
            ),
            rx.el.div(class_name="absolute inset-2 rounded-full bg-bg-elevated"),
            class_name="relative w-24 h-24 rounded-full flex items-center justify-center",
        ),
        rx.el.p(name, class_name="mt-2 text-sm font-medium text-text-secondary"),
        class_name="flex flex-col items-center",
    )


def policy_gates_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Policy Gates", class_name="text-lg font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            policy_ring("Security", DashboardState.policy_gates["security"], "magenta"),
            policy_ring("Perf", DashboardState.policy_gates["performance"], "yellow"),
            policy_ring("A11y", DashboardState.policy_gates["accessibility"], "cyan"),
            policy_ring("Coverage", DashboardState.policy_gates["coverage"], "gold"),
            class_name="flex justify-around",
        ),
        **card_style("magenta"),
    )


def autofix_queue_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Autofix Queue", class_name="text-lg font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    DashboardState.autofix_stats["proposed"],
                    class_name="text-3xl font-bold",
                ),
                rx.el.p("Proposed", class_name="text-sm text-text-secondary"),
                class_name="text-center",
            ),
            rx.el.div(
                rx.el.p(
                    DashboardState.autofix_stats["applied"],
                    class_name="text-3xl font-bold",
                ),
                rx.el.p("Applied", class_name="text-sm text-text-secondary"),
                class_name="text-center",
            ),
            rx.el.div(
                rx.el.p(
                    f"{DashboardState.autofix_stats['merge_rate']}%",
                    class_name="text-3xl font-bold",
                ),
                rx.el.p("Merge Rate", class_name="text-sm text-text-secondary"),
                class_name="text-center",
            ),
            class_name="flex justify-around",
        ),
        **card_style("gold"),
    )


def usage_spend_card() -> rx.Component:
    return rx.el.div(
        rx.el.h3(
            "Usage & Spend", class_name="text-lg font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    DashboardState.usage_spend["coins_burned_30d"],
                    class_name="text-2xl font-bold",
                ),
                rx.el.p("Coins Burned (30d)", class_name="text-sm text-text-secondary"),
                class_name="text-center",
            ),
            rx.el.div(
                rx.el.h4(
                    "Top Adapters", class_name="font-semibold mb-2 text-text-primary"
                ),
                rx.foreach(
                    DashboardState.usage_spend["top_adapters"],
                    lambda adapter: rx.el.div(
                        rx.el.p(adapter[0], class_name="text-sm"),
                        rx.el.p(
                            f"{adapter[1]} coins", class_name="text-sm font-semibold"
                        ),
                        class_name="flex justify-between",
                    ),
                ),
                class_name="space-y-1",
            ),
            class_name="space-y-4",
        ),
        **card_style("yellow"),
    )