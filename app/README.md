
# Colabe Test Labo (Reflex • Python)

[![CI](https://github.com/colabe/test-labo/actions/workflows/ci.yml/badge.svg)](https://github.com/colabe/test-labo/actions/workflows/ci.yml)
[![Coverage](https://img.shields.io/codecov/c/github/colabe/test-labo.svg)](https://codecov.io/gh/colabe/test-labo)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Colabe Test Labo is an AI-powered website and application testing platform that automatically finds issues, explains fixes, and can autofix your code by opening pull requests.

## Table of Contents

- [Key Features](#key-features)
- [Brand Guidelines](#brand-guidelines)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Core Workflows](#core-workflows)
- [Zero-Defect Gates (CI/CD)](#zero-defect-gates-cicd)
- [Ecosystem Integration](#ecosystem-integration)
- [Contributing](#contributing)
- [License](#license)

## Key Features

- **Project Onboarding**: Add projects from a Git URL or ZIP upload. Stacks are auto-detected.
- **Pluggable Runners**: Extensible adapter system for multiple languages and frameworks.
  - **Supported**: Node(JS/TS), Python, Java/Kotlin, Swift/iOS, Dart/Flutter, PHP, Ruby, Go, .NET.
- **Comprehensive Scanners**:
  - **Security**: `bandit`, `pip-audit`, `gosec`, `brakeman`, `detekt`. Secrets detection, OWASP mapping, CycloneDX SBOMs with OSV vulnerability mapping.
  - **Quality**: `ruff`, `mypy`, `eslint`, `swiftlint`, `phpstan`.
  - **Testing**: `pytest`, `jest`, `rspec`, `go test`.
  - **Performance & A11y**: Lighthouse (LCP, CLS, TBT) and `axe-core` (WCAG).
- **Orchestration**: DAG-based job execution with timeouts, cancellation, and tenant-based concurrency limits.
- **AI-Powered Autofix**: Proposes minimal code patches for issues, creates a branch/PR, re-runs verification gates, and supports auto-merge policies.
- **AI Support Copilot**: In-app assistance to explain issues, provide checklists, and guide users through the platform.
- **Knowledge Base**: Integrated User Guide, FAQ, and powerful search.
- **Payments & Subscriptions**: Self-hosted payments with Free/Pro/Enterprise tiers and a coin-based wallet for metered usage (test minutes, storage, etc.).
- **Ecosystem Ready**: Integrates with Colabe ID (SSO), TriggerBus (eventing), and provides SDKs for developers.

## Brand Guidelines

Test Labo follows the Colabe Creative Studio "cyber-lux" design language.

- **Palette**: Dark, high-contrast theme with neon accents.
  - `bg.base`: `#0A0F14`
  - `bg.elevated`: `#0E1520`
  - `text.primary`: `#E8F0FF`
  - `text.secondary`: `#A9B3C1`
  - `accent.cyan`: `#00E5FF`
  - `accent.magenta`: `#FF3CF7`
  - `accent.gold`: `#D8B76E`
- **Typography**: Headings use a subtle `cyan → magenta → gold` gradient. All text must meet WCAG AAA contrast ratios.
- **UI Elements**: Floating cards with thin neon borders and a soft under-glow.
- **Motion**: All transitions use a `200ms` cubic-bezier curve `(0.2, 0.8, 0.2, 1)`.
- **Radii**: `xl` radius is `20px`.

## Architecture

### Folder Structure

The project is organized into modular directories, each with a distinct responsibility.


app/
├── adapters/         # Pluggable runners for different languages (Python, Node, etc.)
├── api/              # API endpoint definitions and logic
├── autofix/          # AI-powered patch generation and PR management
├── core/             # Core domain models, business logic, and policies
├── integrations/     # Third-party integrations (Colabe ID, Git providers, TriggerBus)
├── knowledge/        # User Guide, FAQ, and search data
├── legal/            # Privacy Policy & Terms and Conditions pages/content
├── orchestrator/     # Background job scheduling and execution (DAGs, workers)
├── payments/         # Subscription and wallet management logic
├── sdk/              # Auto-generated client SDKs (Python, TypeScript)
├── storage/          # Artifact management (S3/MinIO abstraction)
└── ui/               # Reflex frontend (pages, components, states)


### Technology Stack

- **Framework**: [Reflex](https://reflex.dev/) (Web UI), [FastAPI](https://fastapi.tiangolo.com/) (API)
- **Database**: PostgreSQL with [SQLModel](https://sqlmodel.tiangolo.com/)
- **Background Jobs**: Redis + [RQ](https://python-rq.org/)
- **Object Storage**: MinIO (S3-compatible)
- **Code Quality**: `ruff`, `black`, `mypy` (strict), `bandit`
- **CI/CD**: GitHub Actions

## Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Redis 7+
- Docker & Docker Compose (for infra)
- Node.js & npm (for Reflex)

### Installation

1.  **Clone the repository:**
    bash
    git clone https://github.com/your-org/colabe-test-labo.git
    cd colabe-test-labo
    

2.  **Set up environment variables:**
    Copy the example `.env` file and fill in your configuration details.
    bash
    cp .env.example .env
    

3.  **Start infrastructure services:**
    This will launch Postgres, Redis, and MinIO via Docker Compose.
    bash
    docker-compose up -d
    

4.  **Install Python dependencies:**
    bash
    pip install -r requirements.txt
    

5.  **Initialize the database and seed demo data:**
    This creates the necessary tables and populates the app with demo projects so the UI renders correctly on first boot.
    bash
    reflex db migrate
    python app/scripts/seed.py
    

6.  **Run the development server:**
    bash
    reflex run
    
    The application will be available at `http://localhost:3000`.

## Core Workflows

### Project Onboarding

1.  Navigate to the "Projects" page.
2.  Click "Add Project" and provide a Git URL (e.g., a public GitHub repository).
3.  Test Labo will clone the repository and automatically detect the technology stack.

### Running a Scan

1.  From the project dashboard, select a test plan.
2.  Click "Run Sweep" to trigger the analysis.
3.  The orchestrator will execute the relevant scanners in a DAG.
4.  View real-time results on the "Live Runs" page and see final reports for Security, Coverage, Performance, and Accessibility.

### Using Autofix

1.  On the "Security" findings page, locate a vulnerability with an available "Autofix" action.
2.  Click the "Autofix" button.
3.  The system will generate a patch, create a new branch, and open a pull request.
4.  All CI gates will automatically run against the PR to verify the fix.

## Zero-Defect Gates (CI/CD)

Our CI pipeline enforces strict quality gates to ensure code is deployment-ready. A build will fail if any gate does not pass.

-   **Static Analysis**:
    -   `ruff check .`
    -   `black --check .`
    -   `mypy --strict .`
    -   `bandit -r . -ll -iii`
-   **End-to-End Testing (Playwright)**:
    -   Auth flows, core page rendering, and critical path user actions are tested.
    -   Asserts no console errors.
-   **Performance Budgets (Lighthouse)**:
    -   LCP ≤ 2.5s
    -   CLS ≤ 0.1
    -   TBT within budget
-   **Accessibility (axe-core)**:
    -   0 critical accessibility violations.
-   **Content**:
    -   Link checker ensures no broken internal or external links.

## Ecosystem Integration

Test Labo is designed to work seamlessly within the Colabe ecosystem.

-   **Colabe ID**: Single Sign-On (SSO) is handled via Colabe's OIDC-compliant identity provider.
-   **TriggerBus**: The platform publishes events (e.g., `run.completed`, `autofix.pr.opened`) to standard TriggerBus topics and subscribes to relevant events from other services.
-   **SDKs**: Auto-generated Python and TypeScript SDKs from our OpenAPI spec allow for programmatic interaction with the Test Labo API.

## Contributing

We welcome contributions! Please see our [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to submit changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

