import reflex as rx
from app.ui.states.help_state import HelpState


def help_copilot_shell() -> rx.Component:
    """The main shell including the beacon and the side panel."""
    return rx.el.div(
        help_beacon(),
        rx.cond(HelpState.show_panel, help_side_panel()),
        rx.el.script("""
            document.addEventListener('keydown', (event) => {
                if (event.shiftKey && event.key === '?') {
                    event.preventDefault();
                    document.getElementById('help-beacon-button').click();
                }
                if (event.key === 'Escape' && document.getElementById('help-side-panel')) {
                    event.preventDefault();
                    document.getElementById('help-close-button').click();
                }
            });
            """),
    )


def help_beacon() -> rx.Component:
    """The persistent help button fixed at the bottom-right."""
    return rx.el.button(
        rx.icon("circle_plus", size=20, class_name="mr-2"),
        "Help",
        id="help-beacon-button",
        on_click=HelpState.toggle_panel,
        class_name="fixed bottom-6 right-6 z-50 flex items-center px-4 py-2 bg-bg-elevated text-text-primary font-semibold rounded-lg shadow-lg border border-accent-cyan/30 hover:bg-accent-cyan/20 transition-all duration-300 hover:shadow-accent-cyan/20",
    )


def help_side_panel() -> rx.Component:
    """The side panel that opens to show help content."""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("bot", size=24, class_name="text-accent-cyan"),
                        rx.el.h2(
                            HelpState.t.get("copilot_title", "AI Support Copilot"),
                            class_name="text-xl font-bold title-gradient",
                        ),
                        class_name="flex items-center gap-3",
                    ),
                    rx.el.button(
                        rx.icon("x", size=20),
                        id="help-close-button",
                        on_click=HelpState.toggle_panel,
                        class_name="p-2 rounded-full hover:bg-white/10 transition-colors",
                    ),
                    class_name="flex items-center justify-between p-4 border-b border-white/10",
                ),
                rx.el.div(
                    rx.foreach(
                        ["Explain", "Steps", "Recipes", "Search", "FAQ"],
                        lambda tab: help_tab(tab),
                    ),
                    class_name="flex border-b border-white/10 px-4",
                ),
                rx.el.div(
                    rx.match(
                        HelpState.active_tab,
                        ("Explain", explain_tab_content()),
                        ("Steps", steps_tab_content()),
                        ("Recipes", recipes_tab_content()),
                        rx.el.div(
                            f"Content for {HelpState.active_tab} coming soon.",
                            class_name="p-6 text-text-secondary",
                        ),
                    ),
                    class_name="flex-grow overflow-y-auto p-6 space-y-6",
                ),
                class_name="flex flex-col h-full",
            ),
            class_name="relative w-full max-w-lg h-full bg-bg-elevated border-l-2 border-accent-cyan/80 shadow-2xl shadow-accent-cyan/20 flex flex-col",
            style={
                "box-shadow": "-10px 0 30px -10px hsla(var(--accent-cyan-hsl), 0.5)"
            },
        ),
        id="help-side-panel",
        class_name="fixed top-0 right-0 h-full z-50 backdrop-blur-sm bg-black/30",
        style={
            "animation": "slideInFromRight 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94) forwards"
        },
    )


def help_tab(name: str) -> rx.Component:
    """A single tab button."""
    is_active = HelpState.active_tab == name
    return rx.el.button(
        name,
        on_click=lambda: HelpState.set_active_tab(name),
        class_name=rx.cond(
            is_active,
            "px-4 py-3 font-semibold text-accent-cyan border-b-2 border-accent-cyan",
            "px-4 py-3 font-medium text-text-secondary hover:text-text-primary",
        ),
        role="tab",
        aria_selected=is_active.to_string(),
    )


def explain_tab_content() -> rx.Component:
    """Content for the 'Explain' tab."""
    return rx.cond(
        HelpState.current_help_entry,
        rx.el.div(
            rx.el.h3(
                HelpState.current_help_entry["title"],
                class_name="text-2xl font-bold text-text-primary",
            ),
            help_section("Purpose", [rx.el.p(HelpState.current_help_entry["purpose"])]),
            help_section(
                "When to use", [rx.el.p(HelpState.current_help_entry["when_to_use"])]
            ),
            help_section(
                "Common Pitfalls",
                rx.foreach(
                    HelpState.current_help_entry["pitfalls"],
                    lambda item: rx.el.li(item),
                ),
                is_list=True,
            ),
            help_section(
                "Advanced Tips",
                rx.foreach(
                    HelpState.current_help_entry["advanced_tips"],
                    lambda item: rx.el.li(item),
                ),
                is_list=True,
            ),
        ),
        rx.el.div(
            rx.icon("search", class_name="text-text-secondary", size=32),
            rx.el.p(
                HelpState.t.get(
                    "no_entry_found", "No entry found for this context. Try Search."
                ),
                class_name="text-text-secondary mt-2",
            ),
            class_name="flex flex-col items-center justify-center h-full text-center",
        ),
    )


def steps_tab_content() -> rx.Component:
    """Content for the 'Steps' tab, for checklists or guided tours."""
    return rx.cond(
        HelpState.current_help_entry,
        rx.el.div(
            help_section(
                "Numbered Steps",
                rx.el.ol(
                    rx.foreach(
                        HelpState.current_help_entry["steps"],
                        lambda item: rx.el.li(item, class_name="mb-2"),
                    ),
                    class_name="list-decimal list-inside space-y-2",
                ),
            ),
            help_section(
                "Verification", [rx.el.p(HelpState.current_help_entry["verification"])]
            ),
            help_section(
                "Rollback", [rx.el.p(HelpState.current_help_entry["rollback"])]
            ),
        ),
        rx.el.div(
            "No specific steps available for this context.",
            class_name="text-text-secondary",
        ),
    )


def recipes_tab_content() -> rx.Component:
    """Content for the 'Recipes' tab, showing safe actions."""
    return rx.el.div(
        rx.el.h4(
            "Quick Actions", class_name="text-lg font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            recipe_button(
                "Start Demo Quick Sweep",
                "Runs a quick sweep on the demo project.",
                "circle-play",
            ),
            recipe_button(
                "Prefill High-Severity Policy",
                "Sets merge-blocking severity to HIGH in Policies.",
                "gavel",
            ),
            class_name="space-y-3",
        ),
    )


def help_section(
    title: str, content: rx.Component | list[rx.Component], is_list: bool = False
) -> rx.Component:
    container = rx.el.ul if is_list else rx.el.div
    return rx.el.div(
        rx.el.h4(title, class_name="text-md font-semibold text-accent-gold mb-2"),
        container(
            content,
            class_name="text-text-secondary space-y-2"
            + (" list-disc list-inside" if is_list else ""),
        ),
        class_name="border-t border-white/10 pt-4",
    )


def recipe_button(title: str, description: str, icon: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, size=20, class_name="text-accent-cyan"),
        rx.el.div(
            rx.el.p(title, class_name="font-semibold text-text-primary text-left"),
            rx.el.p(description, class_name="text-sm text-text-secondary text-left"),
            class_name="flex-grow",
        ),
        rx.icon("chevron-right", size=16, class_name="text-text-secondary"),
        class_name="w-full flex items-center gap-4 p-4 rounded-lg bg-bg-base hover:bg-white/5 border border-white/10 transition-colors",
    )