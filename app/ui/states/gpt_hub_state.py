import reflex as rx
import sqlmodel
from app.ui.states.auth_state import AuthState
from app.core.models import GptRunSummary, GptPrReview, GptDocDraft
from app.core.gpt_schemas import RunSummaryV1, PrReviewV1
from typing import Optional


class GptHubState(AuthState):
    latest_summaries: list[RunSummaryV1] = []
    prs_awaiting_review: list[PrReviewV1] = []
    doc_drafts: list[dict] = []
    token_usage: int = 0

    @rx.event
    def load_overview(self):
        if not self.user:
            return rx.redirect("/login")
        self.latest_summaries = [
            {
                "run_crn": "crn:1:run:123",
                "project_crn": "crn:1:proj:1",
                "status": "blocked",
                "headline": "Build failed due to critical security issue.",
                "gates": {"security": "block", "perf": "pass"},
                "top_findings": [
                    {
                        "type": "sec",
                        "severity": "critical",
                        "file": "app/main.py",
                        "summary": "SQL Injection vulnerability found.",
                        "citations": ["crn:1:finding:555"],
                    }
                ],
                "coverage": {"before_pct": 85.0, "after_pct": 84.5, "delta_pct": -0.5},
                "perf": {"lcp_ms": 1200, "cls": 0.1, "tbt_ms": 300},
                "a11y": {"violations_total": 5, "critical": 1},
                "suggested_actions": [],
                "coins_estimate": {"tokens_in": 1500, "tokens_out": 300, "coins": 18},
            }
        ]
        self.prs_awaiting_review = [
            {
                "pr_crn": "crn:1:pr:456",
                "sha": "a1b2c3d4",
                "risk_score": 85,
                "summary": "This PR introduces a new user authentication flow but has potential performance regressions.",
                "checks": {"tests_updated": True, "secrets_ok": True},
                "file_comments": [
                    {
                        "path": "app/auth.py",
                        "line": 42,
                        "severity": "warn",
                        "comment": "Consider adding more robust error handling here.",
                        "citations": [],
                    }
                ],
                "blocking_issues": [],
                "ready_for_merge": False,
            }
        ]
        self.doc_drafts = [
            {
                "type": "KB Patch",
                "title": "Update installation guide for v2.0",
                "status": "Draft",
            }
        ]
        self.token_usage = 125600