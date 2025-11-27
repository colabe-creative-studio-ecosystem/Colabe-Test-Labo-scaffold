# Operations playbook

## Authentication & sessions
- Most routes enforce `AuthState.check_login` to protect dashboard surfaces; only login/registration are public. [Source](../app/app.py)
- Session records are persisted through the `Session` model, giving operators visibility into active sessions and allowing cleanup when secrets rotate. [Source](../app/core/models.py)

## Background jobs & health checks
- The System Health page (`/health`) is registered in `app/app.py` and is expected to enqueue work via the `app/orchestrator` helpers into Redis-backed RQ queues. Keep Redis and workers running to prevent UI timeouts. [Source](../app/app.py)
- If background tasks stall, restart the worker and flush stuck jobs from Redis to restore status updates.

## Data management
- Run migrations (`reflex db migrate` / `reflex db upgrade`) after model changes in `app/core/models.py`. [Source](../app/core/models.py)
- Seed environments with `python -m app.scripts.seed` to create the demo tenant, owner user, wallet/subscription, project policy, and sample findings for quick validation. [Source](../app/scripts/seed.py)

## Billing & wallets
- Wallet balances, subscription plans, coin packs, and invoices are modeled in `app/core/models.py`. Use these tables to reconcile purchases and entitlements. [Source](../app/core/models.py)
- The billing page is protected by `AuthState.check_login`; ensure authenticated sessions before testing wallet flows. [Source](../app/app.py)

## Auditing
- Actions can be stored in the `AuditLog` table with optional user and tenant references, enabling cross-tenant compliance reporting. [Source](../app/core/models.py)
