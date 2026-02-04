"""Add WhatsApp conversation state store tables

Revision ID: add_conversation_tables
Revises: ce8df88099a4
Create Date: 2026-02-04 13:40:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "add_conversation_tables"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add conversation state store tables."""
    
    # Create contact table
    op.create_table(
        "contact",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("phone_e164", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("display_name", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("locale", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("tags", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes for contact
    op.create_index("ix_contact_workspace_id", "contact", ["workspace_id"])
    op.create_index("ix_contact_phone_e164", "contact", ["phone_e164"])
    op.create_index(
        "ix_contact_workspace_phone", "contact", ["workspace_id", "phone_e164"]
    )
    
    # Create conversation table
    op.create_table(
        "conversation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("channel", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("contact_id", sa.Integer(), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("last_message_at", sa.DateTime(), nullable=True),
        sa.Column("last_intent", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("stage", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("assigned_agent_id", sa.Integer(), nullable=True),
        sa.Column("awaiting_reply_key", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["tenant.id"]),
        sa.ForeignKeyConstraint(["contact_id"], ["contact.id"]),
        sa.ForeignKeyConstraint(["assigned_agent_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes for conversation
    op.create_index("ix_conversation_workspace_id", "conversation", ["workspace_id"])
    op.create_index("ix_conversation_contact_id", "conversation", ["contact_id"])
    op.create_index(
        "ix_conversation_workspace_status",
        "conversation",
        ["workspace_id", "status"],
    )
    op.create_index(
        "ix_conversation_contact_status",
        "conversation",
        ["contact_id", "status"],
    )
    
    # Create message table
    op.create_table(
        "message",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("direction", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("content", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("message_metadata", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversation.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes for message
    op.create_index("ix_message_conversation_id", "message", ["conversation_id"])
    op.create_index("ix_message_created_at", "message", ["created_at"])
    op.create_index(
        "ix_message_conversation_created",
        "message",
        ["conversation_id", "created_at"],
    )


def downgrade() -> None:
    """Downgrade schema - remove conversation state store tables."""
    
    # Drop indexes first
    op.drop_index("ix_message_conversation_created", table_name="message")
    op.drop_index("ix_message_created_at", table_name="message")
    op.drop_index("ix_message_conversation_id", table_name="message")
    
    op.drop_index("ix_conversation_contact_status", table_name="conversation")
    op.drop_index("ix_conversation_workspace_status", table_name="conversation")
    op.drop_index("ix_conversation_contact_id", table_name="conversation")
    op.drop_index("ix_conversation_workspace_id", table_name="conversation")
    
    op.drop_index("ix_contact_workspace_phone", table_name="contact")
    op.drop_index("ix_contact_phone_e164", table_name="contact")
    op.drop_index("ix_contact_workspace_id", table_name="contact")
    
    # Drop tables in reverse order of creation
    op.drop_table("message")
    op.drop_table("conversation")
    op.drop_table("contact")
