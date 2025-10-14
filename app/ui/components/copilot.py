import reflex as rx
from app.ui.states.copilot_state import CopilotState


def copilot_panel() -> rx.Component:
    """The AI Support Copilot side panel."""
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("sparkles", size=20, class_name="text-accent-cyan"),
                    rx.el.h2(
                        "Colabe Copilot",
                        class_name="text-lg font-bold text-text-primary",
                    ),
                    class_name="flex items-center gap-3",
                ),
                rx.el.button(
                    rx.icon("x", size=18),
                    on_click=lambda: CopilotState.toggle_panel(),
                    class_name="p-1 rounded-md hover:bg-white/10",
                ),
                class_name="flex items-center justify-between p-4 border-b border-white/10",
            ),
            rx.el.div(
                copilot_tab("Explain", "file-text"),
                copilot_tab("Steps", "list-checks"),
                copilot_tab("Recipes", "flask-conical"),
                copilot_tab("Search", "search"),
                copilot_tab("FAQ", "circle_plus"),
                class_name="flex items-center border-b border-white/10 p-2",
            ),
            rx.el.div(
                rx.match(
                    CopilotState.current_tab,
                    ("Explain", explain_tab_content()),
                    ("Steps", rx.el.p("Steps content coming soon.")),
                    rx.el.p("Select a tab."),
                ),
                class_name="flex-grow p-4 overflow-y-auto",
            ),
            class_name="flex flex-col h-full",
        ),
        class_name=rx.cond(
            CopilotState.show_panel,
            "fixed bottom-4 right-4 h-[70vh] w-96 max-w-[90vw] bg-bg-elevated/80 backdrop-blur-xl rounded-2xl border border-accent-cyan/30 shadow-2xl shadow-accent-cyan/10 z-50 transition-all duration-300 ease-in-out transform opacity-100 translate-x-0",
            "fixed bottom-4 right-4 h-[70vh] w-96 max-w-[90vw] bg-bg-elevated/80 backdrop-blur-xl rounded-2xl border border-accent-cyan/30 shadow-2xl shadow-accent-cyan/10 z-50 transition-all duration-300 ease-in-out transform opacity-0 translate-x-20 pointer-events-none",
        ),
    )


def copilot_tab(name: str, icon_name: str) -> rx.Component:
    is_active = CopilotState.current_tab == name
    return rx.el.button(
        rx.icon(icon_name, size=16),
        rx.el.span(name),
        on_click=lambda: CopilotState.set_current_tab(name),
        class_name=rx.cond(
            is_active,
            "flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-semibold bg-accent-cyan/10 text-accent-cyan rounded-md",
            "flex-1 flex items-center justify-center gap-2 px-3 py-2 text-sm font-medium text-text-secondary hover:text-text-primary",
        ),
    )


def explain_tab_content() -> rx.Component:
    return rx.cond(
        CopilotState.active_help_content,
        rx.el.div(
            rx.el.h3(
                CopilotState.active_help_content["title"],
                class_name="text-xl font-bold text-text-primary mb-2",
            ),
            help_section("Overview", CopilotState.active_help_content["overview"]),
            help_section(
                "When to Use", CopilotState.active_help_content["when_to_use"]
            ),
            help_section(
                "Common Pitfalls", CopilotState.active_help_content["common_pitfalls"]
            ),
            class_name="space-y-4",
        ),
        rx.el.div(
            rx.icon("search", class_name="text-text-secondary"),
            rx.el.p(
                "No entry found for this context. Try searching.",
                class_name="text-text-secondary",
            ),
            class_name="flex flex-col items-center justify-center h-full gap-4",
        ),
    )


def help_section(title: str, content: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.h4(title, class_name="font-semibold text-text-primary mb-1"),
        rx.el.p(content, class_name="text-sm text-text-secondary leading-relaxed"),
        class_name="border-l-2 border-accent-cyan/50 pl-3",
    )


def help_beacon() -> rx.Component:
    """The persistent help button."""
    return rx.el.button(
        rx.icon("circle_plus", size=20),
        rx.el.span("Help"),
        on_click=lambda: CopilotState.toggle_panel(),
        class_name=rx.cond(
            CopilotState.show_panel,
            "fixed bottom-4 right-4 flex items-center gap-2 px-4 py-2 bg-bg-elevated border border-accent-cyan/30 rounded-full shadow-lg text-text-primary hover:bg-accent-cyan/20 z-40 transition-transform hover:scale-105 hidden",
            "fixed bottom-4 right-4 flex items-center gap-2 px-4 py-2 bg-bg-elevated border border-accent-cyan/30 rounded-full shadow-lg text-text-primary hover:bg-accent-cyan/20 z-40 transition-transform hover:scale-105",
        ),
    )