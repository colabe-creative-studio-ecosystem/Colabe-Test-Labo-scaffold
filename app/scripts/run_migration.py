"""
Script to run the Alembic migration programmatically.
Run with: python -m app.scripts.run_migration
"""

import subprocess
import sys
import os
import logging


def run_migration():
    """Run alembic upgrade to apply pending migrations."""
    print("=" * 60)
    print("Running Alembic Migration: Add Stripe Columns")
    print("=" * 60)
    print("""
This migration adds the following columns:""")
    print("  - tenant.stripe_customer_id (indexed)")
    print("  - subscription.stripe_subscription_id")
    print("  - invoice.stripe_payment_intent_id")
    print("  - invoice.stripe_invoice_id")
    print(
        """
"""
        + "-" * 60
    )
    os.chdir(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    try:
        result = subprocess.run(
            ["alembic", "upgrade", "head"], capture_output=True, text=True, check=True
        )
        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        print("""
✅ Migration completed successfully!""")
        return 0
    except subprocess.CalledProcessError as e:
        logging.exception(f"Migration failed: {e}")
        print(f"\n❌ Migration failed with exit code {e.returncode}")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return 1
    except FileNotFoundError as e:
        logging.exception(f"Alembic not found: {e}")
        print("""
❌ Alembic not found. Make sure it's installed:""")
        print("   pip install alembic")
        return 1


def show_current_revision():
    """Show the current database revision."""
    try:
        result = subprocess.run(["alembic", "current"], capture_output=True, text=True)
        print("""
Current database revision:""")
        print(result.stdout or "  (no revision applied)")
    except Exception as e:
        logging.exception(f"Could not check current revision: {e}")
        print(f"Could not check current revision: {e}")


def show_pending_migrations():
    """Show pending migrations."""
    try:
        result = subprocess.run(
            ["alembic", "history", "--verbose"], capture_output=True, text=True
        )
        print("""
Migration history:""")
        print(result.stdout)
    except Exception as e:
        logging.exception(f"Could not check migration history: {e}")
        print(f"Could not check migration history: {e}")


if __name__ == "__main__":
    show_current_revision()
    print()
    exit_code = run_migration()
    sys.exit(exit_code)