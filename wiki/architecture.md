# Architecture

## High-level view
- **Framework & routing:** The app is built with Reflex Enterprise, registers its theme, global styles, and page routes in `app/app.py`, and wires authentication checks into most pages via `AuthState.check_login`.\
  Pages cover dashboards, health checks, security/quality views, billing, policies, API docs, and authentication flows. [Source](../app/app.py)
- **Configuration:** Environment-driven settings (database, Redis, secrets, storage, AI keys) are declared in `app/core/settings.py` and loaded via `dotenv`, keeping runtime knobs centralized. [Source](../app/core/settings.py)
- **Domain model:** SQLModel-backed tables in `app/core/models.py` cover tenants, users/roles, projects and policies, repositories, runs/findings, SBOM components, autofix runs, sessions, wallets/subscriptions, invoices, and audit logs. [Source](../app/core/models.py)

## UI composition
- **Pages & layout:** `app/ui/pages/index.py` defines the dashboard shell with sidebar navigation, user menu, and hero content. Styles and reusable components live under `app/ui/styles.py` and related modules. [Source](../app/ui/pages/index.py)
- **States:** Authentication, billing, and other interactive features are coordinated through Reflex state classes in `app/ui/states/`. `AuthState` secures routes and exposes the current user/role, while billing state tracks wallet balances. [Source](../app/ui/states)

## Data lifecycle
- **Seeding:** `app/scripts/seed.py` provisions a demo tenant, wallet/subscription, owner user, sample project, and sample security findings to help new environments start with meaningful data. [Source](../app/scripts/seed.py)
- **Sessions:** User sessions are stored in the database through the `Session` model, with expiration handling defined in settings. [Source](../app/core/models.py)
- **Artifacts & storage:** Artifact metadata is stored via the `Artifact` table, while optional S3-compatible settings in `app/core/settings.py` let you offload binary artifacts to external storage. [Source](../app/core/settings.py)

## Background work
- **Health & orchestration:** Health check pages enqueue work to Redis-backed RQ queues through helpers in `app/orchestrator`, keeping long-running tasks off the main request path. [Source](../app/orchestrator)
- **Autofix:** Autofix runs and generated patches are tracked via `AutofixRun` and `AutofixPatch` tables, enabling auditability of automated remediation efforts. [Source](../app/core/models.py)
