"""Add Stripe-related columns to tenant, subscription, and invoice tables

Revision ID: add_stripe_columns
Revises: ce8df88099a4
Create Date: 2025-01-15 12:00:00.000000

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "add_stripe_columns"
down_revision: Union[str, Sequence[str], None] = "ce8df88099a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Stripe-related columns."""
    op.add_column(
        "tenant",
        sa.Column(
            "stripe_customer_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.create_index(
        op.f("ix_tenant_stripe_customer_id"),
        "tenant",
        ["stripe_customer_id"],
        unique=False,
    )
    op.add_column(
        "subscription",
        sa.Column(
            "stripe_subscription_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )
    op.add_column(
        "invoice",
        sa.Column(
            "stripe_payment_intent_id",
            sqlmodel.sql.sqltypes.AutoString(),
            nullable=True,
        ),
    )
    op.add_column(
        "invoice",
        sa.Column(
            "stripe_invoice_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True
        ),
    )


def downgrade() -> None:
    """Remove Stripe-related columns."""
    op.drop_column("invoice", "stripe_invoice_id")
    op.drop_column("invoice", "stripe_payment_intent_id")
    op.drop_column("subscription", "stripe_subscription_id")
    op.drop_index(op.f("ix_tenant_stripe_customer_id"), table_name="tenant")
    op.drop_column("tenant", "stripe_customer_id")