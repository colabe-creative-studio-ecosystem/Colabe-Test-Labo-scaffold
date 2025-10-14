import reflex as rx
from typing import TypedDict, Literal


class Finding(TypedDict):
    """Represents a finding from a tool (lint, security, etc.)."""

    description: str
    severity: str
    file_path: str
    line_number: int


class StepResult(TypedDict, total=False):
    """The result of a single step in the DAG."""

    status: Literal["completed", "failed", "skipped"]
    metrics: dict | None
    findings: list[Finding] | None
    artifacts: list[str] | None
    coverage_delta: float | None
    cost_estimate: int | None
    message: str | None
    error_message: str | None


class StepContext(TypedDict):
    """Context passed to each adapter step."""

    tenant_id: int
    project_id: int
    run_id: int
    repo_path: str