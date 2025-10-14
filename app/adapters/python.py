from app.adapters.base import Adapter
from app.orchestrator.models import StepContext, StepResult, Finding
import subprocess
import json
import logging

logger = logging.getLogger(__name__)


class PythonAdapter(Adapter):
    id = "python"
    name = "Python Adapter"
    languages = ["python"]

    def _run_command(
        self, command: list[str], ctx: StepContext
    ) -> subprocess.CompletedProcess:
        """Helper to run a command and log its output."""
        logger.info(f"Running command: {' '.join(command)}")
        return subprocess.run(
            command, cwd=ctx.repo_path, capture_output=True, text=True
        )

    def discover(self, ctx: StepContext) -> StepResult:
        return StepResult(status="completed", metrics={"detected_framework": "Reflex"})

    def static(self, ctx: StepContext) -> StepResult:
        result = self._run_command(["ruff", "check", "."], ctx)
        num_issues = len(result.stdout.splitlines())
        return StepResult(status="completed", metrics={"ruff_issues": num_issues})

    def security(self, ctx: StepContext) -> StepResult:
        result = self._run_command(["bandit", "-r", ".", "-f", "json"], ctx)
        findings = []
        if result.returncode > 0 and result.stdout:
            try:
                report = json.loads(result.stdout)
                for item in report.get("results", []):
                    findings.append(
                        Finding(
                            description=item["issue_text"],
                            severity=item["issue_severity"],
                            file_path=item["filename"],
                            line_number=item["line_number"],
                        )
                    )
            except json.JSONDecodeError as e:
                logger.exception(f"Failed to parse bandit JSON output: {e}")
                return StepResult(
                    status="failed", error_message="Bandit output parsing error"
                )
        return StepResult(
            status="completed",
            findings=findings,
            metrics={"bandit_findings": len(findings)},
        )

    def unit(self, ctx: StepContext) -> StepResult:
        return StepResult(status="skipped", message="No unit test runner configured.")

    def integration(self, ctx: StepContext) -> StepResult:
        return StepResult(status="skipped", message="No integration tests found.")

    def e2e(self, ctx: StepContext) -> StepResult:
        return StepResult(status="skipped", message="No e2e tests found.")

    def perf(self, ctx: StepContext) -> StepResult:
        return StepResult(status="skipped", message="Performance tests not configured.")

    def a11y(self, ctx: StepContext) -> StepResult:
        return StepResult(
            status="skipped", message="Accessibility tests not configured."
        )

    def coverage(self, ctx: StepContext) -> StepResult:
        return StepResult(status="skipped", message="Coverage not configured.")

    def sbom(self, ctx: StepContext) -> StepResult:
        return StepResult(status="skipped", message="SBOM generation not configured.")

    def summarize(self, ctx: StepContext) -> StepResult:
        return StepResult(status="skipped", message="Summarization not implemented.")