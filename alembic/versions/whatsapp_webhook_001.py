"""Add WhatsApp webhook models

Revision ID: whatsapp_webhook_001
Revises: ce8df88099a4
Create Date: 2026-02-04 13:30:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "whatsapp_webhook_001"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add tables for WhatsApp webhook handling"""
    
    # WebhookEvent table for idempotency tracking
    op.create_table(
        "webhookevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("event_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("payload", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("processed_at", sa.DateTime(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_id"),
    )
    op.create_index(op.f("ix_webhookevent_message_id"), "webhookevent", ["message_id"], unique=False)
    
    # DeadLetterEvent table for failed events
    op.create_table(
        "deadletterevent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("message_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("event_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("payload", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("failed_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_deadletterevent_message_id"), "deadletterevent", ["message_id"], unique=False)
    
    # WebhookMetrics table for monitoring counters
    op.create_table(
        "webhookmetrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("source", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("inbound_events", sa.Integer(), nullable=False),
        sa.Column("outbound_sends", sa.Integer(), nullable=False),
        sa.Column("failures", sa.Integer(), nullable=False),
        sa.Column("circuit_breaker_trips", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_webhookmetrics_source"), "webhookmetrics", ["source"], unique=False)
    op.create_index(op.f("ix_webhookmetrics_date"), "webhookmetrics", ["date"], unique=False)


def downgrade() -> None:
    """Remove WhatsApp webhook tables"""
    op.drop_index(op.f("ix_webhookmetrics_date"), table_name="webhookmetrics")
    op.drop_index(op.f("ix_webhookmetrics_source"), table_name="webhookmetrics")
    op.drop_table("webhookmetrics")
    
    op.drop_index(op.f("ix_deadletterevent_message_id"), table_name="deadletterevent")
    op.drop_table("deadletterevent")
    
    op.drop_index(op.f("ix_webhookevent_message_id"), table_name="webhookevent")
    op.drop_table("webhookevent")
