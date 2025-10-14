import reflex as rx
import json
from pathlib import Path
from typing import TypedDict
from app.ui.states.auth_state import AuthState


class HelpEntry(TypedDict):
    id: str
    title: str
    purpose: str
    when_to_use: str
    preconditions: list[str]
    steps: list[str]
    verification: str
    rollback: str
    advanced_tips: list[str]
    pitfalls: list[str]
    related: list[str]


class HelpState(AuthState):
    show_panel: bool = False
    active_tab: str = "Explain"
    lang: str = "en"
    current_context_id: str | None = None
    _registry: dict[str, HelpEntry] = {}
    _i18n: dict = {}

    def _load_data(self):
        if not self._registry:
            registry_path = Path("knowledge/help_registry.json")
            if registry_path.exists():
                with open(registry_path, "r") as f:
                    self._registry = {item["id"]: item for item in json.load(f)}
        if not self._i18n:
            i18n_path = Path(f"knowledge/i18n/{self.lang}/copilot.json")
            if i18n_path.exists():
                with open(i18n_path, "r") as f:
                    self._i18n = json.load(f)

    @rx.var
    def current_help_entry(self) -> HelpEntry | None:
        self._load_data()
        if self.current_context_id:
            return self._registry.get(self.current_context_id)
        return None

    @rx.var
    def t(self) -> dict:
        self._load_data()
        return self._i18n

    @rx.event
    def toggle_panel(self):
        self.show_panel = not self.show_panel
        if not self.show_panel:
            self.current_context_id = None

    @rx.event
    def open_panel_with_context(self, context_id: str):
        self.current_context_id = context_id
        self.active_tab = "Explain"
        self.show_panel = True

    @rx.event
    def set_active_tab(self, tab: str):
        self.active_tab = tab

    @rx.event
    def set_lang(self, lang: str):
        self.lang = lang
        self._i18n = {}
        self._load_data()

    @rx.event
    def log_telemetry(self, event_name: str, payload: dict):
        print(f"[Telemetry] Event: {event_name}, Payload: {payload}")
        return rx.console_log(f"Telemetry: {event_name}")