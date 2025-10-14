import reflex as rx
import json
from pathlib import Path
from typing import TypedDict


class HelpContent(TypedDict):
    title: str
    overview: str
    when_to_use: str
    common_pitfalls: str


class CopilotState(rx.State):
    """Manages the state of the AI Support Copilot."""

    show_panel: bool = False
    current_tab: str = "Explain"
    help_registry: dict[str, HelpContent] = {}
    current_context_id: str | None = None

    @rx.event
    def on_load(self):
        """Load the help registry from the JSON file on app start."""
        if not self.help_registry:
            registry_path = Path("app/knowledge/help_registry.json")
            if registry_path.exists():
                with open(registry_path, "r") as f:
                    self.help_registry = json.load(f)

    @rx.event
    def toggle_panel(self, context_id: str | None = None):
        """Toggle the visibility of the copilot panel."""
        self.show_panel = not self.show_panel
        if self.show_panel:
            self.current_context_id = (
                context_id
                if context_id
                else self.router.page.path.strip("/") or "index"
            )
            self.current_tab = "Explain"
        else:
            self.current_context_id = None

    @rx.event
    def set_current_tab(self, tab_name: str):
        """Set the active tab in the copilot panel."""
        self.current_tab = tab_name

    @rx.var
    def active_help_content(self) -> HelpContent | None:
        """Get the help content for the current context."""
        if self.current_context_id and self.help_registry:
            return self.help_registry.get(self.current_context_id)
        return None