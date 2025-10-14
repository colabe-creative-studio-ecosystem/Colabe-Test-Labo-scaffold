import reflex as rx
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import Project, ProjectPolicy, SeverityEnum
import sqlmodel


class PolicyState(AuthState):
    project_policy: Optional[ProjectPolicy] = None
    current_project_id: int = 1
    mock_pr_findings: list[dict] = [
        {"severity": "HIGH", "description": "SQL Injection vulnerability"},
        {"severity": "LOW", "description": "Cross-site scripting"},
    ]
    mock_pr_coverage: float = 85.0

    @rx.event
    def load_policy(self):
        if not self.is_logged_in:
            return
        with rx.session() as session:
            policy = session.exec(
                sqlmodel.select(ProjectPolicy).where(
                    ProjectPolicy.project_id == self.current_project_id
                )
            ).first()
            if not policy:
                project = session.get(Project, self.current_project_id)
                if not project:
                    project = Project(id=1, name="Default Project", tenant_id=1)
                    session.add(project)
                    session.commit()
                    session.refresh(project)
                policy = ProjectPolicy(project_id=self.current_project_id)
                session.add(policy)
                session.commit()
                session.refresh(policy)
            self.project_policy = policy

    @rx.event
    def update_policy(self, field: str, value: str):
        if self.project_policy:
            with rx.session() as session:
                policy_to_update = session.get(ProjectPolicy, self.project_policy.id)
                if policy_to_update:
                    if field in [
                        "min_coverage_percent",
                        "performance_budget",
                        "accessibility_budget",
                        "sla_critical",
                        "sla_high",
                        "sla_medium",
                        "sla_low",
                    ]:
                        setattr(policy_to_update, field, int(value))
                    elif field == "auto_merge_enabled":
                        setattr(policy_to_update, field, value == "true")
                    else:
                        setattr(policy_to_update, field, value)
                    session.add(policy_to_update)
                    session.commit()
                    session.refresh(policy_to_update)
                    self.project_policy = policy_to_update

    @rx.var
    def severity_gate_passed(self) -> bool:
        if not self.project_policy:
            return False
        severity_map = {
            SeverityEnum.CRITICAL.value: 4,
            SeverityEnum.HIGH.value: 3,
            SeverityEnum.MEDIUM.value: 2,
            SeverityEnum.LOW.value: 1,
        }
        blocking_severity_level = severity_map.get(
            self.project_policy.blocking_severity.value, 3
        )
        for finding in self.mock_pr_findings:
            finding_severity_level = severity_map.get(finding["severity"], 0)
            if finding_severity_level >= blocking_severity_level:
                return False
        return True

    @rx.var
    def coverage_gate_passed(self) -> bool:
        if not self.project_policy:
            return False
        return self.mock_pr_coverage >= self.project_policy.min_coverage_percent

    @rx.var
    def is_mergeable(self) -> bool:
        return self.severity_gate_passed and self.coverage_gate_passed