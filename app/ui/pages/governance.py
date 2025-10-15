import reflex as rx
from app.ui.states.governance_state import GovernanceState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, sidebar_style


def governance_page() -> rx.Component:
    """The main UI for the Governance & Feature Flags page."""
    return rx.el.div(
        rx.cond(
            GovernanceState.is_logged_in,
            rx.el.div(sidebar(), governance_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-text-primary"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=GovernanceState.on_load,
    )


def governance_content() -> rx.Component:
    """The main content area of the governance page."""
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Governance & Feature Flags",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Manage remote configuration, experiments, and safeguards.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            tabs_navigation(),
            rx.el.div(
                rx.match(
                    GovernanceState.active_tab,
                    ("Flags", flags_tab()),
                    ("Changesets", changesets_tab()),
                    ("Experiments", experiments_tab()),
                    ("Safeguards", safeguards_tab()),
                    rx.el.p(f"Content for {GovernanceState.active_tab} coming soon."),
                ),
                class_name="mt-6",
            ),
            class_name="p-8",
        ),
        diff_modal(),
        class_name=page_content_style,
    )


def tabs_navigation() -> rx.Component:
    """Navigation tabs for the governance page."""
    return rx.el.div(
        rx.foreach(
            GovernanceState.tabs,
            lambda tab: rx.el.button(
                tab,
                on_click=lambda: GovernanceState.set_active_tab(tab),
                class_name=rx.cond(
                    GovernanceState.active_tab == tab,
                    "px-4 py-2 text-sm font-semibold text-accent-cyan border-b-2 border-accent-cyan",
                    "px-4 py-2 text-sm font-medium text-text-secondary hover:text-text-primary",
                ),
            ),
        ),
        class_name="flex space-x-4 border-b border-white/10",
    )


def table_wrapper(content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.div(content, class_name="overflow-x-auto"),
        class_name="bg-bg-elevated p-4 rounded-lg border border-white/10",
    )


def flags_tab() -> rx.Component:
    """Content for the 'Flags' tab."""
    return table_wrapper(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Key"),
                    rx.el.th("Description"),
                    rx.el.th("Type"),
                    rx.el.th("Risk"),
                    rx.el.th("Default Value"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    GovernanceState.flags,
                    lambda flag: rx.el.tr(
                        rx.el.td(flag.key),
                        rx.el.td(flag.description),
                        rx.el.td(flag.type),
                        rx.el.td(
                            rx.el.span(
                                flag.risk, class_name=risk_badge_style(flag.risk)
                            )
                        ),
                        rx.el.td(rx.el.code(flag.default_value)),
                    ),
                )
            ),
            class_name="w-full text-sm text-left text-text-secondary",
        )
    )


def changesets_tab() -> rx.Component:
    """Content for the 'Changesets' tab."""
    return table_wrapper(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("ID"),
                    rx.el.th("Author"),
                    rx.el.th("Status"),
                    rx.el.th("Risk"),
                    rx.el.th("Environment"),
                    rx.el.th("Created At"),
                    rx.el.th("Actions"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    GovernanceState.changesets,
                    lambda cs: rx.el.tr(
                        rx.el.td(cs.id),
                        rx.el.td(cs.author.username),
                        rx.el.td(
                            rx.el.span(
                                cs.status, class_name=status_badge_style(cs.status)
                            )
                        ),
                        rx.el.td(
                            rx.el.span(cs.risk, class_name=risk_badge_style(cs.risk))
                        ),
                        rx.el.td(cs.env),
                        rx.el.td(cs.created_at.to_string()),
                        rx.el.td(
                            rx.el.button(
                                "View Diff",
                                on_click=lambda: GovernanceState.show_diff_modal(cs),
                                class_name="text-accent-cyan text-xs font-semibold hover:underline",
                            )
                        ),
                    ),
                )
            ),
            class_name="w-full text-sm text-left text-text-secondary",
        )
    )


def experiments_tab() -> rx.Component:
    """Content for the 'Experiments' tab."""
    return table_wrapper(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Key"),
                    rx.el.th("Env"),
                    rx.el.th("Status"),
                    rx.el.th("A/B/Holdout %"),
                    rx.el.th("Primary Metric"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    GovernanceState.experiments,
                    lambda exp: rx.el.tr(
                        rx.el.td(exp.key),
                        rx.el.td(exp.env),
                        rx.el.td(exp.status),
                        rx.el.td(
                            f"{exp.variant_a_pct}/{exp.variant_b_pct}/{exp.holdout_pct}"
                        ),
                        rx.el.td(exp.primary_metric),
                    ),
                )
            ),
            class_name="w-full text-sm text-left text-text-secondary",
        )
    )


def safeguards_tab() -> rx.Component:
    """Content for the 'Safeguards' tab."""
    return table_wrapper(
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Name"),
                    rx.el.th("Env"),
                    rx.el.th("Condition"),
                    rx.el.th("Action"),
                    rx.el.th("Cooldown (min)"),
                    rx.el.th("Enabled"),
                )
            ),
            rx.el.tbody(
                rx.foreach(
                    GovernanceState.safeguards,
                    lambda sg: rx.el.tr(
                        rx.el.td(sg.name),
                        rx.el.td(sg.env),
                        rx.el.td(sg.condition),
                        rx.el.td(sg.action),
                        rx.el.td(sg.cooldown_min),
                        rx.el.td(
                            rx.icon(
                                tag=rx.cond(sg.enabled, "check_circle", "x_circle"),
                                class_name=rx.cond(
                                    sg.enabled, "text-success", "text-danger"
                                ),
                            )
                        ),
                    ),
                )
            ),
            class_name="w-full text-sm text-left text-text-secondary",
        )
    )


def diff_modal() -> rx.Component:
    """Modal to display changeset diffs."""
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.trigger(),
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title("Changeset Diff"),
            rx.radix.primitives.dialog.description(
                "Showing the JSON diff for the selected changeset."
            ),
            rx.el.pre(
                rx.el.code(GovernanceState.formatted_diff, class_name="text-xs"),
                class_name="mt-4 p-4 bg-bg-base rounded-md max-h-[60vh] overflow-auto",
            ),
            rx.el.div(
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        "Close",
                        class_name="mt-4 px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
                    )
                ),
                class_name="flex justify-end",
            ),
            style={
                "background-color": "#0E1520",
                "color": "#E8F0FF",
                "border": "1px solid #333",
            },
        ),
        open=GovernanceState.is_diff_modal_open,
        on_open_change=GovernanceState.close_diff_modal,
    )


def risk_badge_style(risk: rx.Var[str]) -> rx.Var[str]:
    return rx.match(
        risk,
        (
            "high",
            "px-2 py-1 text-xs font-semibold rounded-full bg-danger/20 text-danger",
        ),
        (
            "medium",
            "px-2 py-1 text-xs font-semibold rounded-full bg-warning/20 text-warning",
        ),
        (
            "low",
            "px-2 py-1 text-xs font-semibold rounded-full bg-green-500/20 text-green-400",
        ),
        "px-2 py-1 text-xs font-semibold rounded-full bg-gray-500/20 text-gray-400",
    )


def status_badge_style(status: rx.Var[str]) -> rx.Var[str]:
    return rx.match(
        status,
        (
            "approved",
            "px-2 py-1 text-xs font-semibold rounded-full bg-success/20 text-success",
        ),
        (
            "applied",
            "px-2 py-1 text-xs font-semibold rounded-full bg-blue-500/20 text-blue-400",
        ),
        (
            "pending_approval",
            "px-2 py-1 text-xs font-semibold rounded-full bg-warning/20 text-warning",
        ),
        (
            "rejected",
            "px-2 py-1 text-xs font-semibold rounded-full bg-danger/20 text-danger",
        ),
        (
            "rolled_back",
            "px-2 py-1 text-xs font-semibold rounded-full bg-orange-500/20 text-orange-400",
        ),
        "px-2 py-1 text-xs font-semibold rounded-full bg-gray-500/20 text-gray-400",
    )