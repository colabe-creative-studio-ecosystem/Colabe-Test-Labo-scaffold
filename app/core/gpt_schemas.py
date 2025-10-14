from typing import TypedDict, Optional


class RunSummaryTopFinding(TypedDict):
    type: str
    severity: str
    file: str
    summary: str
    citations: list[str]


class RunSummarySuggestedAction(TypedDict):
    action: str
    params: dict
    reason: str


class RunSummaryV1(TypedDict):
    run_crn: str
    project_crn: str
    status: str
    headline: str
    gates: dict[str, str]
    top_findings: list[RunSummaryTopFinding]
    coverage: dict[str, float]
    perf: dict[str, float]
    a11y: dict[str, int]
    suggested_actions: list[RunSummarySuggestedAction]
    coins_estimate: dict[str, int]


class PrReviewFileComment(TypedDict):
    path: str
    line: int
    severity: str
    comment: str
    suggestion_patch: Optional[str]
    citations: list[str]


class PrReviewBlockingIssue(TypedDict):
    title: str
    why: str
    citations: list[str]


class PrReviewV1(TypedDict):
    pr_crn: str
    sha: str
    risk_score: int
    summary: str
    checks: dict[str, bool]
    file_comments: list[PrReviewFileComment]
    blocking_issues: list[PrReviewBlockingIssue]
    ready_for_merge: bool