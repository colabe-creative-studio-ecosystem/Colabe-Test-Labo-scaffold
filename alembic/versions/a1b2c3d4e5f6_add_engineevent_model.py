"""Add EngineEvent model for WhatsApp

Revision ID: a1b2c3d4e5f6
Revises: ce8df88099a4
Create Date: 2026-02-04 14:09:00.000000

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
    op.create_table(
        "engineevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("workspace_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("conversation_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("contact_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("message_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("text", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("interactive_type", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("interactive_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("interactive_title", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("engineevent")
