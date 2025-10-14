import reflex as rx
import bcrypt
from sqlmodel import Session, select
from app.core.models import (
    Organization,
    Tenant,
    User,
    Membership,
    RoleEnum,
    Project,
    ProjectPolicy,
    Wallet,
    Subscription,
    SecurityFinding,
)


def seed_data():
    """Seeds the database with initial demo data for a multi-tenant setup."""
    print("Starting database seeding...")
    with rx.session() as session:
        if session.exec(select(Tenant).where(Tenant.name == "tn_demo_eu")).first():
            print("Demo data already exists. Skipping seeding.")
            return
        demo_org = Organization(name="Colabe Demo Org")
        session.add(demo_org)
        session.commit()
        session.refresh(demo_org)
        print(f"Created Organization: {demo_org.name}")
        tenant_eu = Tenant(
            name="tn_demo_eu", region="eu-central-1", organization_id=demo_org.id
        )
        tenant_us = Tenant(
            name="tn_demo_us", region="us-east-1", organization_id=demo_org.id
        )
        session.add_all([tenant_eu, tenant_us])
        session.commit()
        session.refresh(tenant_eu)
        session.refresh(tenant_us)
        print(f"Created Tenant: {tenant_eu.name} in {tenant_eu.region}")
        print(f"Created Tenant: {tenant_us.name} in {tenant_us.region}")
        wallet_eu = Wallet(tenant_id=tenant_eu.id, coins=10000)
        sub_eu = Subscription(tenant_id=tenant_eu.id, plan="Pro")
        wallet_us = Wallet(tenant_id=tenant_us.id, coins=5000)
        sub_us = Subscription(tenant_id=tenant_us.id, plan="Free")
        session.add_all([wallet_eu, sub_eu, wallet_us, sub_us])
        print(f"Created Wallet and Pro Subscription for {tenant_eu.name}")
        print(f"Created Wallet and Free Subscription for {tenant_us.name}")
        password = "password"
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        users_data = {
            "owner": {"username": "owner_user", "email": "owner@colabe.ai"},
            "admin": {"username": "admin_user", "email": "admin@colabe.ai"},
            "dev": {"username": "dev_user", "email": "dev@colabe.ai"},
            "viewer": {"username": "viewer_user", "email": "viewer@colabe.ai"},
        }
        created_users = {}
        for role, user_info in users_data.items():
            user = User(
                username=user_info["username"],
                email=user_info["email"],
                password_hash=password_hash,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            created_users[role] = user
            print(f"Created User: {user.username}")
        memberships = [
            Membership(
                user_id=created_users["owner"].id,
                tenant_id=tenant_eu.id,
                role=RoleEnum.OWNER,
            ),
            Membership(
                user_id=created_users["admin"].id,
                tenant_id=tenant_eu.id,
                role=RoleEnum.ADMIN,
            ),
            Membership(
                user_id=created_users["dev"].id,
                tenant_id=tenant_eu.id,
                role=RoleEnum.DEVELOPER,
            ),
            Membership(
                user_id=created_users["viewer"].id,
                tenant_id=tenant_eu.id,
                role=RoleEnum.VIEWER,
            ),
            Membership(
                user_id=created_users["owner"].id,
                tenant_id=tenant_us.id,
                role=RoleEnum.OWNER,
            ),
            Membership(
                user_id=created_users["dev"].id,
                tenant_id=tenant_us.id,
                role=RoleEnum.VIEWER,
            ),
        ]
        session.add_all(memberships)
        print("Assigned user memberships to tenants.")
        project_eu = Project(name="EU Showcase Project", tenant_id=tenant_eu.id)
        project_us = Project(name="US Showcase Project", tenant_id=tenant_us.id)
        session.add_all([project_eu, project_us])
        session.commit()
        session.refresh(project_eu)
        session.refresh(project_us)
        print(f"Created Project: {project_eu.name} in tenant {tenant_eu.name}")
        print(f"Created Project: {project_us.name} in tenant {tenant_us.name}")
        project_policy_eu = ProjectPolicy(project_id=project_eu.id)
        project_policy_us = ProjectPolicy(project_id=project_us.id)
        session.add_all([project_policy_eu, project_policy_us])
        print("Created default policies for projects.")
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
            finding = SecurityFinding(project_id=project_eu.id, **data)
            session.add(finding)
        print(f"Created {len(findings_data)} sample security findings for EU project.")
        session.commit()
        print("Database seeding completed successfully.")


if __name__ == "__main__":
    seed_data()