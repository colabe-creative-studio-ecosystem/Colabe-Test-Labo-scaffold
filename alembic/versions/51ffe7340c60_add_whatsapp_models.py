"""add whatsapp models

Revision ID: 51ffe7340c60
Revises: ce8df88099a4
Create Date: 2026-02-04 13:18:15.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "51ffe7340c60"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create WhatsAppAccount table
    op.create_table(
        "whatsappaccount",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("provider", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("phone_number_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("business_account_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("display_phone_number", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("ACTIVE", "DISABLED", name="whatsappaccountstatusenum"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    # Create index on phone_number_id for efficient webhook lookups
    op.create_index(
        "ix_whatsappaccount_phone_number_id",
        "whatsappaccount",
        ["phone_number_id"],
    )
    
    # Create WhatsAppSecret table
    op.create_table(
        "whatsappsecret",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("workspace_id", sa.Integer(), nullable=False),
        sa.Column("key_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("secret_encrypted", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["workspace_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("whatsappsecret")
    op.drop_index("ix_whatsappaccount_phone_number_id", table_name="whatsappaccount")
    op.drop_table("whatsappaccount")
