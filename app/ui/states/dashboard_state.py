import reflex as rx
from typing import TypedDict
import datetime
import random
from app.ui.states.auth_state import AuthState


class Run(TypedDict):
    name: str
    status: str
    duration_s: int


class Event(TypedDict):
    timestamp: str
    message: str


class UsageSpend(TypedDict):
    coins_burned_30d: int
    top_adapters: list[tuple[str, int]]


class DashboardState(AuthState):
    recent_runs: list[Run] = []
    policy_gates: dict[str, int] = {
        "security": 0,
        "performance": 0,
        "accessibility": 0,
        "coverage": 0,
    }
    autofix_stats: dict[str, int] = {"proposed": 0, "applied": 0, "merge_rate": 0}
    usage_spend: UsageSpend = {"coins_burned_30d": 0, "top_adapters": []}
    live_events: list[Event] = []

    @rx.event
    def load_dashboard_data(self):
        self.recent_runs = [
            {"name": "feat/new-login-flow", "status": "PASSED", "duration_s": 124},
            {"name": "fix/header-bug", "status": "FAILED", "duration_s": 98},
            {"name": "chore/update-deps", "status": "PASSED", "duration_s": 210},
            {"name": "main @ 1a2b3c4", "status": "PASSED", "duration_s": 180},
            {"name": "feat/new-feature", "status": "RUNNING", "duration_s": 65},
        ]
        self.policy_gates = {
            "security": 92,
            "performance": 88,
            "accessibility": 95,
            "coverage": 78,
        }
        self.autofix_stats = {"proposed": 12, "applied": 8, "merge_rate": 67}
        self.usage_spend = {
            "coins_burned_30d": 12540,
            "top_adapters": [
                ("Playwright", 4500),
                ("Bandit", 2100),
                ("Lighthouse", 3200),
            ],
        }
        self.live_events = [
            {
                "timestamp": (
                    datetime.datetime.now() - datetime.timedelta(seconds=5)
                ).strftime("%H:%M:%S"),
                "message": "Run 125 PASSED on main",
            },
            {
                "timestamp": (
                    datetime.datetime.now() - datetime.timedelta(seconds=15)
                ).strftime("%H:%M:%S"),
                "message": "Triggered run 126 on feat/new-dashboard",
            },
            {
                "timestamp": (
                    datetime.datetime.now() - datetime.timedelta(seconds=32)
                ).strftime("%H:%M:%S"),
                "message": "Autofix PR #42 merged",
            },
            {
                "timestamp": (
                    datetime.datetime.now() - datetime.timedelta(seconds=45)
                ).strftime("%H:%M:%S"),
                "message": "Policy gate failed: Coverage on PR #45",
            },
            {
                "timestamp": (
                    datetime.datetime.now() - datetime.timedelta(seconds=58)
                ).strftime("%H:%M:%S"),
                "message": "User demo@colabe.ai logged in",
            },
        ]