"""
Script to verify that the Stripe columns exist in the database schema.
Run with: python -m app.scripts.verify_schema
"""

import reflex as rx
from sqlalchemy import inspect, text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def verify_stripe_columns():
    """Verify that all Stripe-related columns exist in the database."""
    print("=" * 60)
    print("Verifying Stripe Column Schema")
    print("=" * 60)
    required_columns = {
        "tenant": ["stripe_customer_id"],
        "subscription": ["stripe_subscription_id"],
        "invoice": ["stripe_payment_intent_id", "stripe_invoice_id"],
    }
    all_passed = True
    try:
        with rx.session() as session:
            inspector = inspect(session.bind)
            for table_name, columns in required_columns.items():
                print(f"\n📋 Table: {table_name}")
                print("-" * 40)
                try:
                    existing_columns = [
                        col["name"] for col in inspector.get_columns(table_name)
                    ]
                    for col in columns:
                        if col in existing_columns:
                            print(f"  ✅ {col} - EXISTS")
                        else:
                            print(f"  ❌ {col} - MISSING")
                            all_passed = False
                except Exception as e:
                    logging.exception(f"Error inspecting table {table_name}: {e}")
                    print(f"  ❌ Error inspecting table: {e}")
                    all_passed = False
        print(
            """
"""
            + "=" * 60
        )
        if all_passed:
            print("✅ ALL STRIPE COLUMNS VERIFIED SUCCESSFULLY")
        else:
            print("❌ SOME COLUMNS ARE MISSING - Run migration:")
            print("   alembic upgrade head")
        print("=" * 60)
        return all_passed
    except Exception as e:
        logger.exception(f"Error verifying schema: {e}")
        print(f"\n❌ Could not connect to database: {e}")
        print("""
Make sure:""")
        print("  1. Database is running")
        print("  2. DATABASE_URL environment variable is set correctly")
        print("  3. Initial migration has been applied")
        return False


def show_table_schema(table_name: str):
    """Show the full schema for a table."""
    try:
        with rx.session() as session:
            inspector = inspect(session.bind)
            columns = inspector.get_columns(table_name)
            print(f"\n📋 Schema for {table_name}:")
            print("-" * 50)
            for col in columns:
                nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                print(f"  {col['name']:30} {str(col['type']):20} {nullable}")
    except Exception as e:
        logging.exception(f"Error getting schema for {table_name}: {e}")
        print(f"Error getting schema for {table_name}: {e}")


if __name__ == "__main__":
    result = verify_stripe_columns()
    print("""

Detailed table schemas:""")
    for table in ["tenant", "subscription", "invoice"]:
        show_table_schema(table)
    exit(0 if result else 1)