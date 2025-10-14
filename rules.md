REFLEX AI — INSTRUCTION PROMPT (Colabe Test Labo)

You are the Reflex AI builder. Build a production-ready Python/Reflex app named Colabe Test Labo that tests websites/apps across stacks, explains fixes, and can open autofix PRs. Enforce Colabe Creative Studio branding and integrate Colabe Payments and Colabe Ecosystem (Colabe ID SSO, TriggerBus, API Center, Service Catalog). The result must be deployable with zero-defect verification (type/lint/security/a11y/perf/tests) and preloaded demo data.

1) Architecture & Quality Bar

Framework: Reflex (Python, typed). Enforce mypy --strict, ruff, black --check, bandit -ll -iii.

Modules: ui/, core/, orchestrator/, adapters/, autofix/, knowledge/, legal/, payments/, integrations/, storage/, api/, sdk/.

Infra: Postgres, Redis (+RQ/Celery workers), MinIO (S3). Provide docker-compose.yml, .env.example, health/readiness endpoints.

Seed: Demo tenant, demo repos, seeded runs so all dashboards render on first boot.

CI: GitHub Actions workflow running: ruff, black, mypy, bandit, Playwright smoke, Lighthouse, axe, link-check, i18n check, SBOM + OSV audit.

2) Brand System (Colabe Creative Studio)

Tokens (single source of truth):

bg.base:#0A0F14, bg.elevated:#0E1520, text.primary:#E8F0FF, text.secondary:#A9B3C1,

accent.cyan:#00E5FF, accent.magenta:#FF3CF7, accent.yellow:#FFE600, accent.gold:#D8B76E,

radii: xl=20px, motion: 200ms cubic-bezier(0.2,0.8,0.2,1).

Atmosphere: subtle animated fine raster background; floating cards with thin neon border + under-glow; AAA contrast.

Components: TopNav (tenant switch, wallet, notifications), SideNav (Projects, Test Plans, Runs, Diffs, Coverage, Security, Accessibility, Performance, Policies, Billing & Wallet, Audit, Settings), Buttons (primary/secondary/ghost), Tables (sticky header, row glow), Code/Diff viewer, Toasts.

3) Core Testing Features

Onboarding: connect Git URL / upload ZIP / use demo project; auto-detect stacks & tools.

Adapters (pluggable): Node(JS/TS), Python, Java/Kotlin, Swift/iOS, Dart/Flutter, PHP, Ruby, Go, .NET.

Methods: discover, static, unit, integration, e2e, perf, a11y, security, coverage, sbom.

Scanners: eslint/tsc/jest/playwright/lighthouse/axe; ruff/mypy/pytest/bandit/pip-audit; detekt/spotbugs; swiftlint/xcodebuild; flutter analyze/test; phpstan/psalm/phpunit; rubocop/rspec/brakeman; go vet/test/gosec; dotnet test/analyzers.

Orchestrator: DAG per Test Plan, timeouts, cancel/resume, per-tenant concurrency caps; capture artifacts (logs, JUnit, LCOV, HTML, CycloneDX SBOM) to S3.

Security: OWASP mapping, secrets detector, OSV vuln mapping from SBOM.

Perf & A11y: headless Lighthouse budgets (LCP/CLS/TBT), axe-core WCAG mapping.

Coverage & Quality: normalize multi-lang coverage; composite “Quality Score”.

4) Autofix Engine

Generate minimal patches aligned to repo style; explain rationale.

Git flow: create branch → commit → open PR → re-run relevant jobs → auto-merge only if all policy gates pass.

Guardrails: never touch secrets/infra; max diff 200 LOC unless owner overrides.

5) AI Support Copilot (for first-timers & second-timers)

Persistent “? Help” + hotkey Shift+/.

First-Timer Mode: guided checklist (Connect repo → Run Quick Sweep → Review findings → Try Autofix → Set budgets).

Second-Timer Mode: concise recipes/tooltips; “Explain this” button next to complex settings.

Context-aware help referencing KB sections; safe actions: navigate, open Policies/Billing with the exact control focused, start demo run if wallet gates pass.

Telemetry: help.opened, tour.completed, faq.viewed, search.query.

6) Knowledge Base + Global Search

User Guide (step-by-step): onboarding, adapters, orchestration, autofix, policies/budgets, billing, integrations, troubleshooting (include verification & rollback steps).

FAQ: ≥40 Q&As across Onboarding/Runs/Autofix/Budgets/Payments/Compliance/Exports; mark 10 as “quick answers”.

Search: global bar (header + KB), typo-tolerant with synonyms (e.g., a11y↔accessibility, sweep↔scan); results include deep-link buttons to open exact settings.

7) Public & App Pages

Landing (public): hero (subtle neon raster), CTAs (SSO, Demo Sweep), value cards, 3-step “How it works”, KPI tiles, pricing teaser, SEO meta, Lighthouse/axe budgets must pass.

Homepage (auth): wallet badge, Quick Sweep CTA, grids (Recent Runs, Policy Gates, Autofix Queue, Usage/Spend), live event feed.

Who We Are: ecosystem diagram (TriggerBus, API Center, GPT Hub, Payments, Domains, SEO Boosters); accessible, lazy-loaded visuals.

Footer/Header links: KB, Privacy, T&C, API Center, Status, Security, Compliance, Contact. Generate sitemap.xml.

8) Legal: Privacy Policy & Terms (EU-first)

Dynamic variables: ORG_LEGAL_NAME, ORG_ADDRESS, ORG_COUNTRY=Spain, ORG_VAT, ORG_EMAIL, DPO_EMAIL (optional), GOVERNING_LAW=Spain, VENUE=Barcelona.

Privacy: controller, data categories, legal bases, processors, transfers/residency, retention, data rights & request flow, cookies, security, changes.

T&C: service description, account/roles, pricing/coins/auto-top-up/refunds, acceptable use (no scanning targets you don’t own), IP & feedback, SLAs/maintenance, warranties/limits, termination, governing law/venue, notices.

Privacy Center: DSR export/delete forms → queued, audited.

9) Payments: Colabe Self-Hosted (subs + coins)

Plans: Free (500 coins/mo), Pro €49/mo (10k coins, 3 concurrency, 20GB, 30-day retention, Autofix), Enterprise (custom).

Meters: run mins, Playwright/Appium mins, Lighthouse scans, Autofix attempts, storage GB-days.

Flow: pre-run estimate → place hold → finalize/refund delta on completion; Auto Top-Up toggle.

Wallet UI: balances, usage charts (7/30d), coin packs, plan upgrade, invoices with filters.

Integrate via environment endpoints (assume provided): COLABE_PAYMENTS_*; signed webhooks with HMAC & timestamp skew ≤ 5m; idempotent processing; audit every money event.

10) Ecosystem Integration

Identity: Colabe ID (OIDC) SSO; JWT audience colabe.testlabo; short-lived access tokens; refresh rotation.

Tenancy: tenant_id on every row/event; data residency tag (EU default); region-pinned storage.

TriggerBus: publish testlabo.run.started|updated|completed, autofix.proposed|applied, billing.hold|finalized|refunded, policy.gate.passed|blocked; subscribe to repo.updated, policy.updated, payments.intent.*, tenant.flags.updated, runner.scale.hint. Envelope: event_id, ts, tenant_id, source, schema_version, idempotency_key, region, payload. Exactly-once via outbox + retries.

Service Catalog: self-register on boot with capabilities/endpoints.

API Center: expose OpenAPI 3.0 for /api/v1/* (runs, artifacts, policies, usage, webhooks). Provide Python/TS SDKs + examples. Playground with tenant-scoped token.

Embeds: signed-token widgets for Runs/Coverage/Security/Perf/A11y.

11) Observability, SLOs, FinOps

OpenTelemetry traces/metrics/logs (attributes: tenant_id, run_id, plan_id).

SLOs: p95 queue wait ≤30s; p95 Quick Sweep ≤6m; event publish ≥99.9%; webhook lag p95 ≤10s. Burn-rate alerts & runbook links.

FinOps: per-run infra cost estimate aligned to coins; tenant/adapter/storage dashboards; anomaly alerts.

Autoscaling hints from queue depth; respect tenant caps.

12) Zero-Defect Verification (hard gates)

Static: ruff clean; black check; mypy strict; bandit low/no findings (app code).

E2E (Playwright): Landing (no console errors), Login (mock OIDC), Homepage widgets, Demo Quick Sweep run, paywall path when coins insufficient.

Perf: Lighthouse budgets on Landing/Homepage — LCP ≤2.5s, CLS ≤0.1, TBT within budget.

A11y: axe-core — 0 critical violations.

Content: 0 broken links; external links rel="noopener".

i18n: EN/ES coverage with no missing keys on public routes.

Supply: CycloneDX SBOM; OSV audit for demo deps.

System Health page: display last run & artifacts for every gate; block publish when any gate is red.

13) Environment Variables (document in README)
COLABE_ID_ISSUER, COLABE_JWKS_URL, COLABE_GATEWAY_AUDIENCE
COLABE_SERVICE_CATALOG_URL, COLABE_API_CENTER_URL
COLABE_TRIGGERBUS_BROKER_URL, TRIGGERBUS_CLIENT_ID, TRIGGERBUS_CLIENT_SECRET
COLABE_PAYMENTS_BASE_URL, COLABE_PAYMENTS_CLIENT_ID, COLABE_PAYMENTS_CLIENT_SECRET, COLABE_PAYMENTS_WEBHOOK_SECRET
DB_URL, REDIS_URL, S3_ENDPOINT, S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET
DATA_RESIDENCY_DEFAULT=EU, DEFAULT_CURRENCY=EUR, SIGNING_KEYS_ROTATION_DAYS=30

14) Acceptance Criteria (must be true before you finish)

Dev boots; all routes render without console errors.

Seeded tenant shows dashboards populated.

Payments purchase→webhook→wallet/invoice completes; run gates block/allow correctly.

TriggerBus events validate with standard envelope; consumers ingest without schema errors.

OpenAPI imports cleanly in API Center; SDK examples run.

CI pipeline green; System Health fully green; artifacts linked.

If any requirement is ambiguous, choose conservative defaults, document in README, and keep security/readability first.