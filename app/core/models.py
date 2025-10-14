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
    wallet: Optional["Wallet"] = Relationship(back_populates="tenant")
    subscription: Optional["Subscription"] = Relationship(back_populates="tenant")
    billing_settings: Optional["BillingSettings"] = Relationship(
        back_populates="tenant"
    )


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


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"


class Run(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    test_plan_id: int = Field(foreign_key="testplan.id")
    status: RunStatus = Field(default=RunStatus.PENDING)
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    idempotency_key: Optional[str] = Field(default=None, index=True)
    steps: list["RunStep"] = Relationship(back_populates="run")
    coverage_data: list["Coverage"] = Relationship(back_populates="run")
    quality_score: Optional["QualityScore"] = Relationship(back_populates="run")
    cost_estimate: Optional["RunCostEstimate"] = Relationship(back_populates="run")


class Finding(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id")
    run: "Run" = Relationship()
    description: str
    severity: str
    file_path: str
    line_number: int
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class RunStepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RunStep(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id")
    run: "Run" = Relationship(back_populates="steps")
    name: str
    status: RunStepStatus = Field(default=RunStepStatus.PENDING)
    started_at: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    log_artifact_id: Optional[int] = Field(foreign_key="artifact.id")


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
    coins_balance: int = Field(default=0)
    credits_balance: int = Field(default=0)
    holds_balance: int = Field(default=0)
    tenant: "Tenant" = Relationship(back_populates="wallet")


class LedgerEntryType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"
    HOLD = "hold"
    FINALIZE = "finalize"
    REFUND = "refund"


class WalletLedger(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    wallet_id: int = Field(foreign_key="wallet.id")
    entry_type: LedgerEntryType
    amount: int
    idempotency_key: str = Field(unique=True)
    request_hash: str
    related_id: Optional[str] = None
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)
    wallet: "Wallet" = Relationship()


class Subscription(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", unique=True)
    plan_id: str = Field(default="free")
    status: str = Field(default="active")
    renews_at: Optional[datetime.datetime] = None
    concurrency_limit: int = Field(default=1)
    artifact_storage_gb: int = Field(default=1)
    retention_days: int = Field(default=7)
    autofix_attempts_limit: int = Field(default=0)
    tenant: "Tenant" = Relationship(back_populates="subscription")


class PricingSnapshot(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    snapshot_data: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class UsageEvent(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    meter_id: str
    quantity: float
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


class InvoicesIndex(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    invoice_ref: str = Field(unique=True)
    amount: float
    currency: str = Field(default="EUR")
    status: str
    due_date: Optional[datetime.date] = None
    paid_at: Optional[datetime.datetime] = None
    pdf_url: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class BillingSettings(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id", unique=True)
    auto_top_up_enabled: bool = Field(default=False)
    auto_top_up_threshold: int = Field(default=1000)
    auto_top_up_amount: int = Field(default=5000)
    low_balance_alert_threshold: int = Field(default=200)
    billing_email: Optional[str] = None
    vat_id: Optional[str] = None
    tax_address: Optional[str] = None
    tenant: "Tenant" = Relationship(back_populates="billing_settings")


class RunCostEstimate(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_id: int = Field(foreign_key="run.id", unique=True)
    estimated_cost: int
    actual_cost: Optional[int] = None
    hold_id: Optional[str] = None
    status: str = Field(default="estimated")
    run: "Run" = Relationship(back_populates="cost_estimate")


class APIKey(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    user_id: int = Field(foreign_key="user.id")
    prefix: str = Field(unique=True, index=True)
    hashed_key: str
    scopes: str
    last_used_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    revoked: bool = Field(default=False)
    name: str = ""
    tenant: "Tenant" = Relationship()
    user: "User" = Relationship()