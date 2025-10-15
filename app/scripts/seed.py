import reflex as rx
import bcrypt
from sqlmodel import Session, select
from app.core.models import (
    Tenant,
    User,
    UserRole,
    RoleEnum,
    Project,
    ProjectPolicy,
    Wallet,
    Subscription,
    SecurityFinding,
)


def seed_data():
    """Seeds the database with initial demo data."""
    print("Starting database seeding...")
    with rx.session() as session:
        if session.exec(select(Tenant).where(Tenant.name == "Demo Tenant")).first():
            print("Demo data already exists. Skipping seeding.")
            return
        demo_tenant = Tenant(name="Demo Tenant")
        session.add(demo_tenant)
        session.commit()
        session.refresh(demo_tenant)
        print(f"Created Tenant: {demo_tenant.name}")
        wallet = Wallet(tenant_id=demo_tenant.id, coins=10000)
        subscription = Subscription(tenant_id=demo_tenant.id, plan="Pro")
        session.add(wallet)
        session.add(subscription)
        print(f"Created Wallet and Pro Subscription for {demo_tenant.name}")
        password = "password"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        demo_user = User(
            username="demo_user",
            email="demo@colabe.ai",
            password_hash=password_hash,
            tenant_id=demo_tenant.id,
        )
        session.add(demo_user)
        session.commit()
        session.refresh(demo_user)
        print(f"Created User: {demo_user.username}")
        owner_role = UserRole(user_id=demo_user.id, role=RoleEnum.OWNER)
        session.add(owner_role)
        print(f"Assigned {RoleEnum.OWNER.value} role to {demo_user.username}")
        sample_project = Project(name="Colabe Showcase", tenant_id=demo_tenant.id)
        session.add(sample_project)
        session.commit()
        session.refresh(sample_project)
        print(f"Created Project: {sample_project.name}")
        project_policy = ProjectPolicy(project_id=sample_project.id)
        session.add(project_policy)
        print(f"Created default policy for project {sample_project.name}")
        findings_data = [
            {
                "scanner": "bandit",
                "test_id": "B404",
                "description": "Use of subprocess module.",
                "severity": "LOW",
                "file_path": "app/orchestrator/tasks.py",
                "line_number": 10,
                "owasp_category": "A03:2021-Injection",
                "cwe": "78",
                "status": "new",
            },
            {
                "scanner": "bandit",
                "test_id": "B101",
                "description": "Use of assert.",
                "severity": "LOW",
                "file_path": "app/tests/test_basic.py",
                "line_number": 25,
                "owasp_category": "A04:2021-Insecure Design",
                "cwe": "657",
                "status": "new",
            },
            {
                "scanner": "cyclonedx",
                "test_id": "CVE-2023-1234",
                "description": "Vulnerability in requests library.",
                "severity": "HIGH",
                "file_path": "requirements.txt",
                "line_number": 1,
                "owasp_category": "A06:2021-Vulnerable and Outdated Components",
                "cwe": "1104",
                "status": "new",
            },
        ]
        for data in findings_data:
            finding = SecurityFinding(project_id=sample_project.id, **data)
            session.add(finding)
        print(f"Created {len(findings_data)} sample security findings.")
        from app.core.models import (
            Ticket,
            TicketMessage,
            TicketStatus,
            TicketSeverity,
            TicketPriority,
            TicketChannel,
            TicketAuthorType,
            Runbook,
            RunbookVisibility,
            SLAPolicy,
        )

        ticket1 = Ticket(
            tenant_id=demo_tenant.id,
            subject="Cannot connect to database",
            channel=TicketChannel.WEB,
            priority=TicketPriority.HIGH,
            severity=TicketSeverity.SEV2,
            status=TicketStatus.IN_PROGRESS,
            assignee_user_id=demo_user.id,
            language="en",
        )
        session.add(ticket1)
        session.commit()
        session.refresh(ticket1)
        msg1 = TicketMessage(
            ticket_id=ticket1.id,
            author_type=TicketAuthorType.USER,
            author_id=demo_user.id,
            body_markdown="I'm getting a connection timeout error when trying to access the production database.",
        )
        msg2 = TicketMessage(
            ticket_id=ticket1.id,
            author_type=TicketAuthorType.AGENT,
            author_id=demo_user.id,
            body_markdown="I'm looking into this now. Can you provide the exact error message?",
        )
        session.add(msg1)
        session.add(msg2)
        runbook1 = Runbook(
            title="Database Connectivity Issues",
            severity_scope=[TicketSeverity.SEV1, TicketSeverity.SEV2],
            steps_mdx="""1. Check firewall rules.
2. Verify DB credentials.
3. Restart the database server.""",
            visibility=RunbookVisibility.INTERNAL,
        )
        session.add(runbook1)
        sla_policy1 = SLAPolicy(
            name="Enterprise 24x7 SEV1",
            plan="Enterprise",
            severity=TicketSeverity.SEV1,
            first_response_target_min=30,
            next_response_target_min=60,
            resolution_target_min=240,
        )
        session.add(sla_policy1)
        print("Created sample support ticket, runbook, and SLA policy.")
        session.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_data()