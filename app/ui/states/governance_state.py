import reflex as rx
from app.ui.states.auth_state import AuthState


class GovernanceState(AuthState):
    """State for the governance page."""

    tabs: list[str] = [
        "Flags",
        "Rules",
        "Changesets",
        "Experiments",
        "Safeguards",
        "Approvals",
        "History",
    ]
    active_tab: str = "Flags"

    @rx.event
    def on_load_data(self):
        """Load initial data for the governance page."""
        pass