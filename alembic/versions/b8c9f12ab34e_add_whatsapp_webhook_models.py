"""Add WhatsApp webhook models

Revision ID: b8c9f12ab34e
Revises: ce8df88099a4
Create Date: 2026-02-04 13:15:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "b8c9f12ab34e"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create WhatsAppPhoneMapping table
    op.create_table(
        "whatsappphonemapping",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("phone_number_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone_number_id"),
    )
    op.create_index(
        op.f("ix_whatsappphonemapping_phone_number_id"),
        "whatsappphonemapping",
        ["phone_number_id"],
        unique=False,
    )

    # Create EventLog table
    op.create_table(
        "eventlog",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=True),
        sa.Column("event_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("event_source", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("payload", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("processed", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("eventlog")
    op.drop_index(
        op.f("ix_whatsappphonemapping_phone_number_id"),
        table_name="whatsappphonemapping",
    )
    op.drop_table("whatsappphonemapping")
