
# Colabe Test Labo

A comprehensive test automation platform built with Reflex that provides security scanning, quality assessment, policy enforcement, and automated code fixing capabilities.

## Overview

Colabe Test Labo is an enterprise-grade test automation platform that helps development teams:

- **Security Scanning**: Static analysis with Bandit, dependency vulnerability scanning with CycloneDX + OSV
- **Quality Assessment**: Code coverage tracking, composite quality scoring
- **Policy Enforcement**: Configurable gates for merge blocking based on severity, coverage, and performance
- **Automated Fixing**: AI-powered patch generation for security vulnerabilities
- **Multi-tenancy**: Support for multiple organizations with role-based access control
- **Audit Trail**: Complete logging of all user actions and system events

## Architecture

The application follows a modular architecture:


app/
├── adapters/           # Language runners and external integrations
├── autofix/           # AI-powered patch generation
├── core/              # Domain models, settings, and business logic
├── integrations/      # Git providers and webhook handlers
├── orchestrator/      # Background job management (Redis + RQ)
├── storage/           # Artifact management and S3 integration
├── ui/                # Reflex frontend components and pages
│   ├── pages/         # Application pages
│   ├── states/        # Reflex state management
│   └── styles.py      # Theme and styling
└── scripts/           # Database seeding and maintenance


## Features

### 🔐 Security & Authentication
- Multi-tenant architecture with role-based access control
- Secure session management with configurable timeouts
- User registration with tenant creation
- Audit logging for all user actions

### 🛡️ Security Scanning
- **Static Analysis**: Integration with Bandit for Python security issues
- **Dependency Scanning**: CycloneDX SBOM generation with OSV vulnerability database
- **Vulnerability Tracking**: Complete OWASP mapping and CWE classification
- **Automated Remediation**: AI-powered security patch generation

### 📊 Quality & Coverage
- **Coverage Tracking**: Per-file coverage analysis with heatmap visualization
- **Quality Scoring**: Composite scores including static analysis, test pass rates, and security metrics
- **Trend Analysis**: Coverage delta tracking and performance monitoring
- **Visual Reports**: Interactive Plotly charts and heatmaps

### ⚙️ Policy Management
- **Configurable Gates**: Set blocking severity levels for merge requests
- **Coverage Requirements**: Minimum coverage thresholds
- **SLA Management**: Configurable response times by severity
- **Auto-merge**: Automated PR merging when all checks pass
- **Autofix Scoping**: Control which issue types are eligible for automated fixing

### 💰 Billing & Wallet System
- **Coin-based Pricing**: Pay-per-use model with coin wallets
- **Subscription Plans**: Free and Pro tiers
- **Usage Tracking**: Monitor coin consumption per operation
- **Invoice Management**: Automated billing and payment processing

## Tech Stack

- **Frontend**: Reflex (Python-based React framework)
- **Backend**: FastAPI with SQLModel
- **Database**: PostgreSQL with SQLAlchemy
- **Task Queue**: Redis + RQ for background jobs
- **Storage**: S3-compatible object storage
- **AI**: Anthropic Claude for code patch generation
- **Security Tools**: Bandit, CycloneDX, OSV
- **Visualization**: Plotly for charts and graphs

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL
- Redis
- Node.js (for frontend compilation)

### Environment Setup

1. Clone the repository:
bash
git clone <repository-url>
cd colabe-test-labo


2. Install dependencies:
bash
pip install -r requirements.txt


3. Set up environment variables:
bash
cp .env.example .env
# Edit .env with your configuration


Required environment variables:
env
DATABASE_URL=postgresql://user:password@localhost:5432/colabe_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-here
CSRF_SECRET_KEY=another-secret-key
ANTHROPIC_API_KEY=your-anthropic-api-key
S3_ENDPOINT_URL=your-s3-endpoint
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=colabe-artifacts


4. Initialize the database:
bash
reflex db migrate
python app/scripts/seed.py


### Development Server

Start the development server:
bash
reflex run


The application will be available at `http://localhost:3000`

### Production Deployment

1. Build the application:
bash
reflex export --frontend-only


2. Start background workers:
bash
rq worker --url redis://localhost:6379/0


3. Run the production server:
bash
reflex run --env prod


## Usage

### Getting Started

1. **Register**: Create a new account at `/register`
   - This creates both a user account and a new tenant organization
   - You'll be assigned the "Owner" role automatically

2. **Dashboard**: After login, access the main dashboard at `/`
   - View your coin balance and subscription status
   - Navigate to different sections using the sidebar

3. **Security Scanning**: Visit `/security`
   - Click "Scan Now" to run Bandit and dependency scans
   - View findings with severity classifications
   - Trigger automated fixes for eligible vulnerabilities

4. **Policy Configuration**: Go to `/policies`
   - Set blocking severity levels
   - Configure minimum coverage requirements
   - Enable/disable auto-merge functionality
   - Adjust SLA timeframes

### API Usage

The platform provides a REST API documented at `/api-docs`. Key endpoints include:

- `GET /api/v1/projects` - List projects
- `POST /api/v1/projects/{id}/runs` - Trigger test runs
- `GET /api/v1/runs/{id}/artifacts` - Download artifacts

Authentication is via API keys provided in the `X-API-Key` header.

### Webhook Integration

Configure webhooks to receive notifications for:
- Run completions
- Security finding updates
- Pull request status changes

## Development

### Code Structure

- **State Management**: Each page has its own Reflex state class in `app/ui/states/`
- **Component Architecture**: Reusable components follow the atomic design pattern
- **Styling**: Uses TailwindCSS with a custom cyber-lux theme
- **Background Tasks**: Long-running operations use RQ workers

### Adding New Features

1. **Create Models**: Add new SQLModel classes in `app/core/models.py`
2. **Create State**: Add state management in `app/ui/states/`
3. **Create UI**: Build components in `app/ui/pages/`
4. **Add Routes**: Register pages in `app/app.py`

### Testing

Run the test suite:
bash
pytest


For security scanning:
bash
bandit -r app/


For code quality:
bash
ruff check app/
black --check app/
mypy app/


## API Reference

### Authentication
All API endpoints require authentication via the `X-API-Key` header.

### Rate Limits
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated requests

### Webhooks
Configure webhook URLs in your project settings. Webhook payloads include:

**Run Completion**:
on
{
  "event_type": "run.completed",
  "run_id": 123,
  "status": "success",
  "completed_at": "2024-01-15T10:30:00Z"
}


## Configuration

### Database Configuration
The application uses PostgreSQL with automatic migrations. Connection settings are configured via the `DATABASE_URL` environment variable.

### Redis Configuration
Background job processing requires Redis. Configure via the `REDIS_URL` environment variable.

### S3 Storage
Artifacts are stored in S3-compatible storage. Required environment variables:
- `S3_ENDPOINT_URL`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`

### AI Integration
Security patch generation uses Anthropic's Claude API. Set your API key in the `ANTHROPIC_API_KEY` environment variable.

## Monitoring & Health Checks

### Health Endpoint
Check system health at `/health`:
- Database connectivity
- Redis connectivity  
- Background worker status

### Audit Logging
All user actions are logged in the audit trail available at `/audits`. This includes:
- User authentication events
- Policy changes
- Security scan triggers
- Autofix operations

## Troubleshooting

### Common Issues

**Database Connection Errors**:
- Verify PostgreSQL is running
- Check `DATABASE_URL` format
- Ensure database exists and user has permissions

**Redis Connection Issues**:
- Verify Redis server is running
- Check `REDIS_URL` configuration
- Ensure Redis is accessible from application

**Background Jobs Not Processing**:
- Start RQ worker: `rq worker --url redis://localhost:6379/0`
- Check Redis connectivity
- Review worker logs for errors

**Security Scanning Failures**:
- Ensure Bandit is installed: `pip install bandit`
- Check file permissions for repository access
- Verify CycloneDX tools are available

### Logging

Application logs are configured via Python's logging module. Set the log level with:

import logging
logging.basicConfig(level=logging.INFO)


For debugging, use `DEBUG` level to see detailed request/response information.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality  
5. Ensure all tests pass
6. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code style
- Use type hints for all function signatures
- Add docstrings for public methods
- Maintain test coverage above 80%

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation at `/api-docs`
- Review the audit logs at `/audits` for system events

---

**Colabe Test Labo** - Automated testing and security scanning platform
Built with ❤️ using Reflex and modern Python technologies.

