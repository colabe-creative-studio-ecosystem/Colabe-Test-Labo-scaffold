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


class TenantStatusEnum(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSING = "closing"
    CLOSED = "closed"


class DomainStatusEnum(str, Enum):
    PENDING = "pending"
    VERIFYING = "verifying"
    ISSUED = "issued"
    FAILED = "failed"


class Tenant(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    users: list["User"] = Relationship(back_populates="tenant")
    status: TenantStatusEnum = Field(default=TenantStatusEnum.ACTIVE)
    region: str = Field(default="eu-central-1")
    plan: str = Field(default="Free")
    feature_flags: str = Field(default="{}")
    theme: Optional[str] = Field(default=None)
    trial_ends_at: Optional[datetime.datetime] = None
    custom_domain: Optional[str] = Field(default=None, unique=True)
    custom_domain_status: Optional[DomainStatusEnum] = Field(default=None)
    custom_domain_txt_record: Optional[str] = Field(default=None)


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


class EventOutbox(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    event_id: str = Field(unique=True, index=True)
    topic: str
    payload: str
    status: str = Field(default="pending", index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    retry_count: int = Field(default=0)


class ConsumerIdempotency(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    idempotency_key: str = Field(unique=True, index=True)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)