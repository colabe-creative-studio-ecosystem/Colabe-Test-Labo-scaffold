"""add outbound messaging guardrails

Revision ID: a1b2c3d4e5f6
Revises: ce8df88099a4
Create Date: 2026-02-04 13:35:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create outboundmessage table
    op.create_table(
        "outboundmessage",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("conversation_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("recipient_email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("message_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("failure_reason", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_outboundmessage_tenant_id"), "outboundmessage", ["tenant_id"], unique=False
    )
    op.create_index(
        op.f("ix_outboundmessage_conversation_id"),
        "outboundmessage",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outboundmessage_recipient_email"),
        "outboundmessage",
        ["recipient_email"],
        unique=False,
    )

    # Create conversationratelimit table
    op.create_table(
        "conversationratelimit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_conversationratelimit_conversation_id"),
        "conversationratelimit",
        ["conversation_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_conversationratelimit_tenant_id"),
        "conversationratelimit",
        ["tenant_id"],
        unique=False,
    )

    # Create contactcooldown table
    op.create_table(
        "contactcooldown",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contact_email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("last_message_sent_at", sa.DateTime(), nullable=False),
        sa.Column("cooldown_until", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_contactcooldown_contact_email"),
        "contactcooldown",
        ["contact_email"],
        unique=False,
    )
    op.create_index(
        op.f("ix_contactcooldown_tenant_id"), "contactcooldown", ["tenant_id"], unique=False
    )

    # Create workspacequiethours table
    op.create_table(
        "workspacequiethours",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False),
        sa.Column("start_hour", sa.Integer(), nullable=False),
        sa.Column("end_hour", sa.Integer(), nullable=False),
        sa.Column("timezone", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id"),
    )

    # Create circuitbreakerstate table
    op.create_table(
        "circuitbreakerstate",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("state", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("failure_count", sa.Integer(), nullable=False),
        sa.Column("last_failure_at", sa.DateTime(), nullable=True),
        sa.Column("window_start", sa.DateTime(), nullable=False),
        sa.Column("circuit_opened_at", sa.DateTime(), nullable=True),
        sa.Column("admin_notified_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("circuitbreakerstate")
    op.drop_table("workspacequiethours")
    op.drop_index(op.f("ix_contactcooldown_tenant_id"), table_name="contactcooldown")
    op.drop_index(op.f("ix_contactcooldown_contact_email"), table_name="contactcooldown")
    op.drop_table("contactcooldown")
    op.drop_index(
        op.f("ix_conversationratelimit_tenant_id"), table_name="conversationratelimit"
    )
    op.drop_index(
        op.f("ix_conversationratelimit_conversation_id"), table_name="conversationratelimit"
    )
    op.drop_table("conversationratelimit")
    op.drop_index(op.f("ix_outboundmessage_recipient_email"), table_name="outboundmessage")
    op.drop_index(op.f("ix_outboundmessage_conversation_id"), table_name="outboundmessage")
    op.drop_index(op.f("ix_outboundmessage_tenant_id"), table_name="outboundmessage")
    op.drop_table("outboundmessage")
