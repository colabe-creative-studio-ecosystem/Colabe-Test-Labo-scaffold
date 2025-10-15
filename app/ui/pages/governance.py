import reflex as rx
from app.ui.states.governance_state import GovernanceState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def governance_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            GovernanceState.is_logged_in,
            rx.el.div(sidebar(), governance_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=GovernanceState.on_load_data,
    )


def governance_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Governance",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Manage Flags, Experiments, and Safeguards.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.foreach(
                        GovernanceState.tabs,
                        lambda tab: rx.el.button(
                            tab,
                            on_click=GovernanceState.set_active_tab(tab),
                            class_name=rx.cond(
                                GovernanceState.active_tab == tab,
                                "px-4 py-2 font-semibold text-accent-cyan border-b-2 border-accent-cyan",
                                "px-4 py-2 font-medium text-text-secondary hover:text-text-primary",
                            ),
                        ),
                    ),
                    class_name="flex space-x-4 border-b border-white/10",
                ),
                class_name="px-8",
            ),
            rx.el.div(
                rx.match(
                    GovernanceState.active_tab,
                    ("Flags", flags_tab()),
                    ("Rules", rules_tab()),
                    ("Changesets", changesets_tab()),
                    ("Experiments", experiments_tab()),
                    ("Safeguards", safeguards_tab()),
                    ("Approvals", approvals_tab()),
                    ("History", history_tab()),
                    rx.el.p("Select a tab"),
                ),
                class_name="p-8",
            ),
            class_name="flex-1",
        ),
        class_name=page_content_style,
    )


def placeholder_tab_content(title: str) -> rx.Component:
    return rx.el.div(
        rx.el.h2(title, class_name="text-xl font-semibold text-text-primary mb-4"),
        rx.el.div(
            rx.el.p(
                "This feature is under construction. Check back soon for updates.",
                class_name="text-text-secondary",
            ),
            class_name="text-center py-16",
            **card_style("magenta"),
        ),
    )


def flags_tab() -> rx.Component:
    return placeholder_tab_content("Flags")


def rules_tab() -> rx.Component:
    return placeholder_tab_content("Rules")


def changesets_tab() -> rx.Component:
    return placeholder_tab_content("Changesets")


def experiments_tab() -> rx.Component:
    return placeholder_tab_content("Experiments")


def safeguards_tab() -> rx.Component:
    return placeholder_tab_content("Safeguards")


def approvals_tab() -> rx.Component:
    return placeholder_tab_content("Approvals")


def history_tab() -> rx.Component:
    return placeholder_tab_content("History")