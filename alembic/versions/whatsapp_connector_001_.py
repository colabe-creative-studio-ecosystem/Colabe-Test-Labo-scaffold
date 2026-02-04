"""Add WhatsApp connector settings table

Revision ID: whatsapp_connector_001
Revises: ce8df88099a4
Create Date: 2026-02-04 13:30:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "whatsapp_connector_001"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "whatsappconnectorsettings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("phone_number_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("business_account_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("webhook_verify_token", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("access_token_encrypted", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("environment", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("is_connected", sa.Boolean(), nullable=False),
        sa.Column("last_webhook_received", sa.DateTime(), nullable=True),
        sa.Column("last_health_check", sa.DateTime(), nullable=True),
        sa.Column("health_check_status", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenant.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("whatsappconnectorsettings")
