import reflex as rx
import datetime
from typing import Optional
from sqlmodel import Field, Relationship, JSON, Column
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
    runner_pools: list["RunnerPool"] = Relationship(back_populates="tenant")


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


class GptModel(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    model_id: str = Field(unique=True)
    provider: str
    context_window: int
    supports_json: bool = Field(default=False)
    latency_p50: int
    cost_tokens_in: float
    cost_tokens_out: float
    max_output_tokens: int
    residency_region: str
    labels: str


class GptRunSummary(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    run_crn: str = Field(unique=True)
    project_crn: str
    status: str
    headline: str
    summary_data: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class GptPrReview(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    pr_crn: str = Field(unique=True)
    sha: str
    review_data: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class GptDocDraft(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    draft_type: str
    draft_data: dict = Field(default={}, sa_column=Column(JSON))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class RunnerPool(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tenant_id: int = Field(foreign_key="tenant.id")
    pool_type: str = Field(default="private")
    labels: dict = Field(default={}, sa_column=Column(JSON))
    region: str
    min_runners: int = Field(default=0)
    max_runners: int = Field(default=5)
    max_concurrency: int = Field(default=5)
    idle_ttl_seconds: int = Field(default=300)
    enrollment_token: Optional[str] = Field(default=None)
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    tenant: "Tenant" = Relationship(back_populates="runner_pools")
    runners: list["Runner"] = Relationship(back_populates="pool")


class Runner(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    runner_crn: str = Field(unique=True)
    pool_id: int = Field(foreign_key="runnerpool.id")
    hostname: str
    os: str
    arch: str
    ip_address: str
    region: str
    status: str = Field(default="offline")
    last_heartbeat: Optional[datetime.datetime] = None
    agent_version: str
    capabilities: dict = Field(default={}, sa_column=Column(JSON))
    registered_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    pool: "RunnerPool" = Relationship(back_populates="runners")


class TicketStatus(str, Enum):
    NEW = "new"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    WAITING_ON_CUSTOMER = "waiting_on_customer"
    PENDING_EXTERNAL = "pending_external"
    RESOLVED = "resolved"
    CLOSED = "closed"


class TicketSeverity(str, Enum):
    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"
    SEV4 = "SEV4"


class TicketPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class TicketChannel(str, Enum):
    WEB = "web"
    EMAIL = "email"
    API = "api"
    SLACK = "slack"
    TEAMS = "teams"
    AUTOTICKET = "autoticket"


class TicketAuthorType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class RunbookVisibility(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"


class BusinessHours(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    tenant_id: int = Field(foreign_key="tenant.id")
    tz: str
    weekdays: list[int] = Field(sa_column=Column(JSON))
    holidays: list[str] = Field(sa_column=Column(JSON))


class SLAPolicy(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    plan: str
    severity: TicketSeverity
    first_response_target_min: int
    next_response_target_min: int
    resolution_target_min: int
    business_hours_id: Optional[int] = Field(
        default=None, foreign_key="businesshours.id"
    )
    pause_on_customer_wait: bool = Field(default=True)
    business_hours: Optional["BusinessHours"] = Relationship()


class Ticket(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    org_id: Optional[int] = Field(default=None)
    subject: str
    channel: TicketChannel
    priority: TicketPriority
    severity: TicketSeverity
    status: TicketStatus = Field(default=TicketStatus.NEW)
    assignee_user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    group: Optional[str] = None
    sla_policy_id: Optional[int] = Field(default=None, foreign_key="slapolicy.id")
    opened_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    first_response_at: Optional[datetime.datetime] = None
    resolved_at: Optional[datetime.datetime] = None
    last_customer_reply_at: Optional[datetime.datetime] = None
    language: str = Field(default="en")
    related_crns: list[str] = Field(default=[], sa_column=Column(JSON))
    tenant: "Tenant" = Relationship()
    assignee: Optional["User"] = Relationship()
    sla_policy: Optional["SLAPolicy"] = Relationship()
    messages: list["TicketMessage"] = Relationship(back_populates="ticket")


class TicketMessage(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    author_type: TicketAuthorType
    author_id: Optional[int] = Field(default=None, foreign_key="user.id")
    lang: str = Field(default="en")
    body_markdown: str
    attachments: list[str] = Field(default=[], sa_column=Column(JSON))
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    ticket: "Ticket" = Relationship(back_populates="messages")
    author: Optional["User"] = Relationship()


class Runbook(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    severity_scope: list[TicketSeverity] = Field(sa_column=Column(JSON))
    steps_mdx: str
    linked_crns: list[str] = Field(default=[], sa_column=Column(JSON))
    visibility: RunbookVisibility = Field(default=RunbookVisibility.INTERNAL)


class SupportIntegration(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    type: str
    config_json: dict = Field(default={}, sa_column=Column(JSON))
    enabled: bool = Field(default=False)
    tenant_id: int = Field(foreign_key="tenant.id")


class SupportAudit(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tenant_id: int = Field(foreign_key="tenant.id")
    actor_crn: str
    action: str
    before_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    after_json: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.now)


class CSATResponse(rx.Model, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    ticket_id: int = Field(foreign_key="ticket.id")
    rating: int
    comment: Optional[str] = None
    lang: str = Field(default="en")
    ts: datetime.datetime = Field(default_factory=datetime.datetime.now)
    hashed_email: str
    ticket: "Ticket" = Relationship()