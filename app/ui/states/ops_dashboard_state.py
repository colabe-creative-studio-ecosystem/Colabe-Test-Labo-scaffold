import reflex as rx
import datetime
import random
from typing import TypedDict
from app.ui.states.auth_state import AuthState


class BuildInfo(TypedDict):
    sha: str
    signatures_verified: str


class HelmInfo(TypedDict):
    release_version: str
    values_hash: str


class HpaStatus(TypedDict):
    name: str
    state: str


class PodHealth(TypedDict):
    running: int
    pending: int
    failed: int


class WafCounters(TypedDict):
    rate_limited_ips: int


class OpsDashboardState(AuthState):
    build_info: BuildInfo = {"sha": "loading...", "signatures_verified": "loading..."}
    helm_info: HelmInfo = {"release_version": "loading...", "values_hash": "loading..."}
    hpa_status: list[HpaStatus] = []
    pod_health: PodHealth = {"running": 0, "pending": 0, "failed": 0}
    error_budget_burn: float = 0.0
    last_backup_check: str = "loading..."
    last_dr_drill: str = "loading..."
    synthetics_last_pass: str = "loading..."
    waf_counters: WafCounters = {"rate_limited_ips": 0}
    residency_check: str = "loading..."

    @rx.event
    def load_ops_data(self):
        """Loads mock operational data."""
        self.build_info = {"sha": "a1b2c3d4", "signatures_verified": "Verified"}
        self.helm_info = {"release_version": "v1.2.3", "values_hash": "f4g5h6i7"}
        self.hpa_status = [
            {"name": "web", "state": "Scaling (CPU > 65%)"},
            {"name": "worker", "state": "Stable (Queue < 100)"},
        ]
        self.pod_health = {
            "running": random.randint(8, 12),
            "pending": random.randint(0, 1),
            "failed": 0,
        }
        self.error_budget_burn = round(random.uniform(0.5, 2.5), 2)
        now = datetime.datetime.now()
        self.last_backup_check = (now - datetime.timedelta(hours=6)).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
        self.last_dr_drill = (now - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        self.synthetics_last_pass = (now - datetime.timedelta(minutes=2)).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
        self.waf_counters = {"rate_limited_ips": random.randint(5, 50)}
        self.residency_check = "Passing"