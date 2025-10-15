import reflex as rx
import sqlmodel
from typing import Optional
import json
import logging
from app.ui.states.auth_state import AuthState
from app.core.models import (
    FFFlag,
    FFChangeset,
    FFExperiment,
    FFSafeguard,
    FFChangesetStatusEnum,
    FFRiskEnum,
    FFEnvEnum,
    User,
)


class GovernanceState(AuthState):
    """State for the Governance dashboard."""

    active_tab: str = "Flags"
    tabs: list[str] = [
        "Flags",
        "Rules",
        "Changesets",
        "Experiments",
        "Safeguards",
        "Approvals",
        "History",
    ]
    flags: list[FFFlag] = []
    changesets: list[FFChangeset] = []
    experiments: list[FFExperiment] = []
    safeguards: list[FFSafeguard] = []
    selected_changeset_diff: dict | list | None = None
    is_diff_modal_open: bool = False

    @rx.event
    def on_load(self):
        """Load all necessary data for the governance page."""
        return [
            GovernanceState.load_flags,
            GovernanceState.load_changesets,
            GovernanceState.load_experiments,
            GovernanceState.load_safeguards,
        ]

    @rx.event
    def set_active_tab(self, tab: str):
        """Set the active tab."""
        self.active_tab = tab

    @rx.event
    def load_flags(self):
        """Load feature flags from the database."""
        with rx.session() as session:
            self.flags = session.exec(sqlmodel.select(FFFlag)).all()

    @rx.event
    def load_changesets(self):
        """Load changesets from the database."""
        with rx.session() as session:
            self.changesets = session.exec(
                sqlmodel.select(FFChangeset).options(
                    sqlmodel.selectinload(FFChangeset.author)
                )
            ).all()

    @rx.event
    def load_experiments(self):
        """Load experiments from the database."""
        with rx.session() as session:
            self.experiments = session.exec(sqlmodel.select(FFExperiment)).all()

    @rx.event
    def load_safeguards(self):
        """Load safeguards from the database."""
        with rx.session() as session:
            self.safeguards = session.exec(sqlmodel.select(FFSafeguard)).all()

    @rx.event
    def show_diff_modal(self, changeset: FFChangeset):
        """Show the diff modal for a changeset."""
        try:
            self.selected_changeset_diff = json.loads(changeset.diff_json)
        except json.JSONDecodeError as e:
            logging.exception(f"Error decoding changeset diff JSON: {e}")
            self.selected_changeset_diff = {"error": "Invalid JSON in diff"}
        self.is_diff_modal_open = True

    @rx.event
    def close_diff_modal(self):
        """Close the diff modal."""
        self.is_diff_modal_open = False
        self.selected_changeset_diff = None

    @rx.var
    def formatted_diff(self) -> str:
        """Return the selected changeset diff as a formatted JSON string."""
        if self.selected_changeset_diff:
            return json.dumps(self.selected_changeset_diff, indent=2)
        return ""