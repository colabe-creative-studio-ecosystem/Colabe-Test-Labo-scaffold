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
            
            # Add WhatsApp template tables
            if "whatsapptemplate" not in existing_tables:
                logger.info("Creating whatsapptemplate table")
                print("  + Creating whatsapptemplate table")
                session.exec(text("""
                    CREATE TABLE IF NOT EXISTS whatsapptemplate (
                        id INTEGER PRIMARY KEY,
                        workspace_id INTEGER NOT NULL,
                        name VARCHAR NOT NULL,
                        language VARCHAR NOT NULL DEFAULT 'en',
                        category VARCHAR NOT NULL DEFAULT 'utility',
                        body VARCHAR NOT NULL,
                        variables_json VARCHAR NOT NULL DEFAULT '[]',
                        status VARCHAR NOT NULL DEFAULT 'draft',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (workspace_id) REFERENCES tenant(id)
                    )
                """))
                session.commit()
            
            # Add ActionPlan table
            if "actionplan" not in existing_tables:
                logger.info("Creating actionplan table")
                print("  + Creating actionplan table")
                session.exec(text("""
                    CREATE TABLE IF NOT EXISTS actionplan (
                        id INTEGER PRIMARY KEY,
                        project_id INTEGER NOT NULL,
                        name VARCHAR NOT NULL,
                        kind VARCHAR NOT NULL,
                        template_id INTEGER,
                        config_json VARCHAR NOT NULL DEFAULT '{}',
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (project_id) REFERENCES project(id),
                        FOREIGN KEY (template_id) REFERENCES whatsapptemplate(id)
                    )
                """))
                session.commit()
    except Exception as e:
        logger.exception(f"Database initialization error: {e}")