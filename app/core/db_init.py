import reflex as rx
from sqlalchemy import inspect, text
import logging

logger = logging.getLogger(__name__)


def initialize_db():
    """
    Checks for missing columns in the database and adds them if necessary.
    This ensures the schema matches the models even if migrations were skipped.
    """
    try:
        from app.core.settings import settings

        if not settings.DATABASE_URL:
            return
        print("Checking database schema for missing columns...")
        with rx.session() as session:
            try:
                inspector = inspect(session.bind)
                existing_tables = inspector.get_table_names()
            except Exception as e:
                logger.exception(f"Database schema check skipped: {e}")
                return

            def add_column(table, col_name, col_type, index_sql=None):
                if table not in existing_tables:
                    return
                try:
                    columns = [c["name"] for c in inspector.get_columns(table)]
                    if col_name not in columns:
                        logger.info(f"Adding missing column {col_name} to {table}")
                        print(f"  + Adding {col_name} to {table}")
                        session.exec(
                            text(
                                f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
                            )
                        )
                        if index_sql:
                            session.exec(text(index_sql))
                        session.commit()
                except Exception as e:
                    logger.exception(f"Failed to add column {col_name} to {table}: {e}")
                    session.rollback()

            add_column(
                "tenant",
                "stripe_customer_id",
                "VARCHAR",
                "CREATE INDEX IF NOT EXISTS ix_tenant_stripe_customer_id ON tenant (stripe_customer_id)",
            )
            add_column("subscription", "stripe_subscription_id", "VARCHAR")
            add_column("invoice", "stripe_payment_intent_id", "VARCHAR")
            add_column("invoice", "stripe_invoice_id", "VARCHAR")
    except Exception as e:
        logger.exception(f"Database initialization error: {e}")