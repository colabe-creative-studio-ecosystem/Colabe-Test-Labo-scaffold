import reflex as rx
import datetime
from typing import Optional
from sqlmodel import Field, Relationship
from enum import Enum


class RoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class Tenant(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    users: list["User"] = Relationship(back_populates="tenant")


class User(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True)
    email: str = Field(unique=True)
    password_hash: str
    tenant_id: int = Field(foreign_key="tenant.id")
    tenant: "Tenant" = Relationship(back_populates="users")
    roles: list["UserRole"] = Relationship(back_populates="user")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class Project(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tenant_id: int = Field(foreign_key="tenant.id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    user_roles: list["UserRole"] = Relationship(back_populates="project")
    policy: Optional["ProjectPolicy"] = Relationship(back_populates="project")


class UserRole(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    role: RoleEnum
    user: "User" = Relationship(back_populates="roles")
    project: Optional["Project"] = Relationship(back_populates="user_roles")


class Repository(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str
    project_id: int = Field(foreign_key="project.id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class TestPlan(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    project_id: int = Field(foreign_key="project.id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class Run(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_plan_id: int = Field(foreign_key="testplan.id")
    status: str
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    coverage_data: list["Coverage"] = Relationship(back_populates="run")
    quality_score: Optional["QualityScore"] = Relationship(back_populates="run")


class Finding(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id")
    run: "Run" = Relationship()
    description: str
    severity: str
    file_path: str
    line_number: int
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class SeverityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class AutofixScopeEnum(str, Enum):
    SECURITY = "security"
    QUALITY = "quality"
    ALL = "all"
    NONE = "none"


class ProjectPolicy(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id", unique=True)
    blocking_severity: SeverityEnum = Field(default=SeverityEnum.HIGH)
    min_coverage_percent: float = Field(default=80.0)
    performance_budget: int = Field(default=90)
    accessibility_budget: int = Field(default=95)
    required_adapters: str = Field(default="bandit,cyclonedx")
    autofix_scope: AutofixScopeEnum = Field(default=AutofixScopeEnum.SECURITY)
    auto_merge_enabled: bool = Field(default=False)
    sla_critical: int = Field(default=24)
    sla_high: int = Field(default=72)
    sla_medium: int = Field(default=168)
    sla_low: int = Field(default=720)
    project: "Project" = Relationship(back_populates="policy")


class SecurityFinding(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    scanner: str
    test_id: str
    description: str
    severity: str
    file_path: str
    line_number: int
    owasp_category: Optional[str] = None
    cwe: Optional[str] = None
    status: str = Field(default="new")
    waiver_expiry: Optional[datetime.datetime] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    project: "Project" = Relationship()


class SBOMComponent(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="project.id")
    name: str
    version: str
    purl: str = Field(unique=True)
    vulnerabilities: list["ComponentVulnerability"] = Relationship(
        back_populates="component"
    )
    project: "Project" = Relationship()


class ComponentVulnerability(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    component_id: int = Field(foreign_key="sbomcomponent.id")
    osv_id: str = Field(unique=True)
    summary: str
    severity: str
    cvss_score: Optional[float] = None
    details: str
    component: "SBOMComponent" = Relationship(back_populates="vulnerabilities")


class Coverage(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id")
    file_path: str
    covered_lines: int
    total_lines: int
    coverage_percentage: float
    run: "Run" = Relationship(back_populates="coverage_data")


class QualityScore(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id", unique=True)
    static_issues_score: float
    test_pass_rate: float
    coverage_delta: float
    performance_score: float
    accessibility_score: float
    security_score: float
    composite_score: float
    run: "Run" = Relationship(back_populates="quality_score")


class Artifact(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id")
    run: "Run" = Relationship()
    name: str
    storage_path: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class Policy(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str
    tenant_id: int = Field(foreign_key="tenant.id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class AuditLog(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")
    action: str
    details: Optional[str] = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    user: Optional["User"] = Relationship()


class AutofixRun(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    finding_id: int = Field(foreign_key="securityfinding.id")
    status: str = Field(default="pending")
    branch_name: Optional[str] = None
    pull_request_url: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    finding: "SecurityFinding" = Relationship()


class AutofixPatch(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    autofix_run_id: int = Field(foreign_key="autofixrun.id")
    diff: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    run: "AutofixRun" = Relationship()


class Session(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(unique=True)
    user_id: int = Field(foreign_key="user.id")
    user: "User" = Relationship()
    expires_at: datetime.datetime


class Wallet(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", unique=True)
    coins: int = Field(default=500)
    tenant: "Tenant" = Relationship()


class Subscription(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", unique=True)
    plan: str = Field(default="Free")
    status: str = Field(default="active")
    renews_at: Optional[datetime.datetime] = None
    tenant: "Tenant" = Relationship()


class CoinPack(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    amount: int
    price_eur: float
    volume_discount: float = Field(default=0.0)


class Invoice(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    amount: float
    currency: str = Field(default="EUR")
    status: str
    due_date: Optional[datetime.date] = None
    paid_at: Optional[datetime.datetime] = None
    download_url: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class FFTypeEnum(str, Enum):
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    JSON = "json"


class FFRiskEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FFEnvEnum(str, Enum):
    DEV = "dev"
    STAGE = "stage"
    PROD = "prod"


class FFRolloutTypeEnum(str, Enum):
    FIXED = "fixed"
    PERCENT = "percent"
    EXPR = "expr"


class FFChangesetStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    APPLIED = "applied"
    REJECTED = "rejected"
    ROLLED_BACK = "rolled_back"


class FFSafeguardActionEnum(str, Enum):
    ROLLBACK = "rollback"
    FREEZE = "freeze"
    ALERT = "alert"


class FFFlag(rx.Model, table=True, __tablename__="ff_flags"):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str = Field(unique=True)
    description: str
    type: FFTypeEnum
    risk: FFRiskEnum
    default_value: str
    allowed_scopes: str
    created_by_id: int = Field(foreign_key="user.id")
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    created_by: "User" = Relationship()
    rules: list["FFRule"] = Relationship(back_populates="flag")


class FFSegment(rx.Model, table=True, __tablename__="ff_segments"):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    definition_json: str


class FFRule(rx.Model, table=True, __tablename__="ff_rules"):
    id: Optional[int] = Field(default=None, primary_key=True)
    flag_id: int = Field(foreign_key="ff_flags.id")
    env: FFEnvEnum
    region: Optional[str] = None
    tenant_id: Optional[int] = Field(default=None, foreign_key="tenant.id")
    segment_id: Optional[int] = Field(default=None, foreign_key="ff_segments.id")
    rollout_type: FFRolloutTypeEnum
    value: str
    percent: int = Field(default=0)
    hash_salt: str
    start_at: Optional[datetime.datetime] = None
    end_at: Optional[datetime.datetime] = None
    precedence: int
    flag: "FFFlag" = Relationship(back_populates="rules")
    tenant: Optional["Tenant"] = Relationship()
    segment: Optional["FFSegment"] = Relationship()


class FFChangeset(rx.Model, table=True, __tablename__="ff_changesets"):
    id: Optional[int] = Field(default=None, primary_key=True)
    env: FFEnvEnum
    author_id: int = Field(foreign_key="user.id")
    status: FFChangesetStatusEnum
    diff_json: str
    risk: FFRiskEnum
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    approved_by_id: Optional[int] = Field(default=None, foreign_key="user.id")
    approved_at: Optional[datetime.datetime] = None
    applied_at: Optional[datetime.datetime] = None
    author: "User" = Relationship(
        sa_relationship_kwargs={"foreign_keys": "FFChangeset.author_id"}
    )
    approved_by: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "FFChangeset.approved_by_id"}
    )


class FFExperiment(rx.Model, table=True, __tablename__="ff_experiments"):
    id: Optional[int] = Field(default=None, primary_key=True)
    key: str
    env: FFEnvEnum
    variant_a_pct: int
    variant_b_pct: int
    holdout_pct: int
    primary_metric: str
    start_at: Optional[datetime.datetime] = None
    end_at: Optional[datetime.datetime] = None
    guardrails_json: str
    status: str
    assignments: list["FFAssignment"] = Relationship(back_populates="experiment")


class FFAssignment(rx.Model, table=True, __tablename__="ff_assignments"):
    id: Optional[int] = Field(default=None, primary_key=True)
    experiment_id: int = Field(foreign_key="ff_experiments.id")
    subject_key: str
    variant: str
    hash: str
    ts: datetime.datetime = Field(default_factory=datetime.datetime.now)
    experiment: "FFExperiment" = Relationship(back_populates="assignments")


class FFAudit(rx.Model, table=True, __tablename__="ff_audit"):
    id: Optional[int] = Field(default=None, primary_key=True)
    actor_crn: str
    action: str
    before_json: str
    after_json: str
    ts: datetime.datetime = Field(default_factory=datetime.datetime.now)


class FFSafeguard(rx.Model, table=True, __tablename__="ff_safeguards"):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    env: FFEnvEnum
    condition: str
    threshold_json: str
    action: FFSafeguardActionEnum
    cooldown_min: int
    enabled: bool = Field(default=True)