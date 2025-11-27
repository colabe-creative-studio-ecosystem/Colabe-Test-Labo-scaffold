# Colabe Test Labo Scaffold

Colabe Test Labo is a Reflex-based dashboard for orchestrating QA, security, and policy workflows across multi-tenant projects. It includes authentication, billing placeholders, background health checks, auditing, and seeded demo data so you can explore the UI quickly.

## Project structure

- `app/app.py` – Registers the Reflex application, global theme, and routed pages for authentication, dashboards, audits, policies, billing, API docs, and health checks.
- `app/core` – Domain models and configuration (database/Redis URLs, secrets, storage, and AI keys).
- `app/ui` – Page components, shared styles, and state containers that back the UI (authentication, billing, health, etc.).
- `app/orchestrator` – RQ-backed background task helpers used by the health check page.
- `app/scripts/seed.py` – Populates the database with demo tenants, users, projects, and sample security findings.
- `assets/` – Static assets served by Reflex.
- `requirements.txt` – Full dependency lock for the scaffold.

## Prerequisites

- Python 3.11+
- Redis (for the health-check worker queue)
- PostgreSQL (or another SQLModel-compatible database) reachable via `DATABASE_URL`

## Configuration

The app reads its runtime configuration from environment variables (or a `.env` file):

- `DATABASE_URL` (e.g., `postgresql://user:password@localhost:5432/colabe_db`)
- `REDIS_URL` (e.g., `redis://localhost:6379/0`)
- `SECRET_KEY` and `CSRF_SECRET_KEY` for session security
- Optional: `S3_ENDPOINT_URL`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`, `S3_BUCKET_NAME` for artifact storage
- Optional: `ANTHROPIC_API_KEY` for AI-enabled features

## Getting started

1. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

2. **Create the database schema**
   ```bash
   reflex db migrate
   reflex db upgrade
   ```

3. **Seed demo data (optional)**
   ```bash
   python -m app.scripts.seed
   ```

4. **Run supporting services**
   - Start Redis and an RQ worker: `rq worker default`

5. **Start the Reflex app**
   ```bash
   reflex run
   ```
   The development server runs on `http://localhost:3000` by default.

## Development notes

- The authentication state stores sessions in the database and enforces timeouts; keep `SECRET_KEY` and `CSRF_SECRET_KEY` unique per environment.
- Health checks enqueue jobs into Redis via the orchestrator; ensure the worker is running so the System Health page stays responsive.
- The seed script creates a `demo_user` (`demo@colabe.ai` / `password`) with owner permissions and sample security findings to explore dashboards.
- For tests, you can start with `pytest` to exercise any added API/server code.

## Operational checklist

- Configure production database and Redis URLs before deployment.
- Provide object storage credentials if you plan to persist artifacts.
- Rotate secrets regularly and scope API keys to least privilege.
- Monitor the RQ worker and Redis health to keep background tasks flowing.
