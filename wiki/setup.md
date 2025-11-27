# Setup & configuration

## Prerequisites
- Python 3.11+
- PostgreSQL (or any SQLModel-compatible database) reachable via `DATABASE_URL`
- Redis for background queues

## Environment variables
Define these in `.env` or your shell before running:

| Variable | Purpose | Default |
| --- | --- | --- |
| `DATABASE_URL` | Application database URL | `postgresql://user:password@localhost:5432/colabe_db` |
| `REDIS_URL` | Redis connection for background queues | `redis://localhost:6379/0` |
| `SECRET_KEY` | Session signing secret | `a_very_secret_key` |
| `CSRF_SECRET_KEY` | CSRF token secret | `another_secret_for_csrf` |
| `S3_ENDPOINT_URL` | Optional S3-compatible endpoint for artifacts | _unset_ |
| `S3_ACCESS_KEY_ID` | Access key for S3-compatible storage | _unset_ |
| `S3_SECRET_ACCESS_KEY` | Secret key for S3-compatible storage | _unset_ |
| `S3_BUCKET_NAME` | Target bucket for artifacts | `colabe-artifacts` |
| `ANTHROPIC_API_KEY` | Optional key for AI-enabled features | _unset_ |

## Local installation
1. Create and activate a virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run database migrations via `reflex db migrate` then `reflex db upgrade`.
4. (Optional) Seed demo data with `python -m app.scripts.seed` to create a demo tenant, owner user, project policy, and sample findings.

## Running the stack
- **Start supporting services:** Launch Redis and an RQ worker (`rq worker default`) so health checks and queued tasks can run.
- **Run the Reflex app:** Execute `reflex run` and open `http://localhost:3000`.

## Demo credentials
Seeding creates `demo@colabe.ai / password` with owner permissions in the `Demo Tenant`, plus wallet credits and a Pro subscription to explore billing flows.
