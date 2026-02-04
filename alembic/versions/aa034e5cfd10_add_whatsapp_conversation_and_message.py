"""Add WhatsApp conversation and message models

Revision ID: aa034e5cfd10
Revises: ce8df88099a4
Create Date: 2026-02-04 13:20:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "aa034e5cfd10"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create conversation table
    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("whatsapp_number", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("contact_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("assigned_agent_id", sa.Integer(), nullable=True),
        sa.Column("ai_summary", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("sla_deadline", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["assigned_agent_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_conversation_tenant_id"), "conversation", ["tenant_id"])
    op.create_index(op.f("ix_conversation_assigned_agent_id"), "conversation", ["assigned_agent_id"])
    op.create_index(op.f("ix_conversation_status"), "conversation", ["status"])

    # Create message table
    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("sender_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=True),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversation.id"]),
        sa.ForeignKeyConstraint(["sender_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_message_conversation_id"), "message", ["conversation_id"])
    op.create_index(op.f("ix_message_timestamp"), "message", ["timestamp"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_message_timestamp"), table_name="message")
    op.drop_index(op.f("ix_message_conversation_id"), table_name="message")
    op.drop_table("message")
    
    op.drop_index(op.f("ix_conversation_status"), table_name="conversation")
    op.drop_index(op.f("ix_conversation_assigned_agent_id"), table_name="conversation")
    op.drop_index(op.f("ix_conversation_tenant_id"), table_name="conversation")
    op.drop_table("conversation")
