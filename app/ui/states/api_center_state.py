import reflex as rx
import json
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta
import sqlmodel
from app.ui.states.auth_state import AuthState
from app.core.settings import settings
from app.core.models import ApiKey


class ApiCenterState(AuthState):
    active_tab: str = "rest"
    openapi_json_str: str = ""
    api_keys: list[ApiKey] = []
    new_api_key: str = ""
    webhook_events: list[str] = [
        "testlabo.run.started",
        "testlabo.run.updated",
        "testlabo.run.completed",
        "testlabo.autofix.proposed",
        "testlabo.autofix.applied",
        "testlabo.policy.gate.passed",
        "testlabo.policy.gate.blocked",
        "testlabo.billing.hold",
        "testlabo.billing.finalized",
        "testlabo.billing.refunded",
    ]

    @rx.var
    def webhook_py_example(self) -> str:
        return f'\nimport hmac\nimport hashlib\nimport time\n\n# Get this from your tenant settings\nWEBHOOK_SECRET = "{settings.WEBHOOK_SIGNING_SECRET[:10]}..."\n\ndef verify_signature(payload_body: bytes, timestamp: str, signature: str) -> bool:\n    if abs(time.time() - int(timestamp)) > 300:\n        # Timestamp is too old\n        return False\n\n    signed_payload = f"{{timestamp}}.{{payload_body.decode()}}".encode()\n    expected_signature = hmac.new(\n        WEBHOOK_SECRET.encode(),\n        msg=signed_payload,\n        digestmod=hashlib.sha256\n    ).hexdigest()\n\n    return hmac.compare_digest(expected_signature, signature)\n'

    @rx.var
    def webhook_ts_example(self) -> str:
        return f"\nimport * as crypto from 'crypto';\n\n// Get this from your tenant settings\nconst webhookSecret = '{settings.WEBHOOK_SIGNING_SECRET[:10]}...';\n\nfunction verifySignature(payloadBody: string, timestamp: string, signature: string): boolean {{\n    const fiveMinutes = 5 * 60 * 1000;\n    if (Math.abs(Date.now() - parseInt(timestamp, 10) * 1000) > fiveMinutes) {{\n        // Timestamp is too old\n        return false;\n    }}\n\n    const signedPayload = `${{timestamp}}.${{payloadBody}}`;\n    const expectedSignature = crypto\n        .createHmac('sha256', webhookSecret)\n        .update(signedPayload)\n        .digest('hex');\n\n    return crypto.timingSafeEqual(Buffer.from(expectedSignature), Buffer.from(signature));\n}}\n"

    @rx.var
    def sdk_py_example(self) -> str:
        return """
from colabe_testlabo import ColabeClient

client = ColabeClient(api_key="YOUR_API_KEY")

# List projects
projects = client.projects.list()
for project in projects:
    print(project.name)

# Create a run
new_run = client.runs.create(project_id=projects[0].id, ...)
print(f"Started run: {{new_run.id}}")

# Stream logs
for log_entry in client.runs.stream_logs(run_id=new_run.id):
    print(log_entry)
"""

    @rx.var
    def sdk_ts_example(self) -> str:
        return """
import {{ ColabeClient }} from '@colabe/testlabo';

const client = new ColabeClient({{ apiKey: 'YOUR_API_KEY' }});

async function main() {{
    // List projects
    const projects = await client.projects.list();
    projects.forEach(project => console.log(project.name));

    // Create a run
    if (projects.length > 0) {{
        const newRun = await client.runs.create({{ projectId: projects[0].id, ... }});
        console.log(`Started run: ${{newRun.id}}`);

        // Stream events
        for await (const event of client.runs.streamEvents(newRun.id)) {{
            console.log(event);
        }}
    }}
}}

main();
"""

    @rx.event
    def set_active_tab(self, tab_name: str):
        self.active_tab = tab_name

    @rx.event
    def load_api_center_data(self):
        yield ApiCenterState.generate_openapi_spec()
        yield ApiCenterState.load_api_keys()

    @rx.event
    def generate_openapi_spec(self):
        openapi_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": settings.OPENAPI_TITLE,
                "version": "v1",
                "description": "Developer-first API for Colabe Test Labo.",
                "contact": {"email": settings.OPENAPI_CONTACT_EMAIL},
            },
            "servers": [{"url": "/api"}],
            "tags": [
                {"name": "Projects", "description": "Manage projects"},
                {"name": "Runs", "description": "Manage test runs"},
                {"name": "Artifacts", "description": "Access run artifacts"},
                {"name": "Policies", "description": "Manage policies"},
                {"name": "Usage", "description": "Billing and usage data"},
                {"name": "Autofix", "description": "Manage autofix proposals"},
                {"name": "Admin", "description": "Service-to-service operations"},
            ],
            "paths": self._get_paths(),
            "components": self._get_components(),
        }
        self.openapi_json_str = json.dumps(openapi_spec, indent=2)

    @rx.event
    def load_api_keys(self):
        if not self.is_logged_in or not self.user:
            return
        with rx.session() as session:
            self.api_keys = session.exec(
                sqlmodel.select(ApiKey)
                .where(ApiKey.tenant_id == self.user.tenant_id)
                .order_by(sqlmodel.desc(ApiKey.created_at))
            ).all()

    @rx.event
    def create_api_key(self, form_data: dict):
        self.new_api_key = ""
        name = form_data.get("name")
        scopes = form_data.get("scopes", "")
        if not name:
            return rx.toast("Key name is required.", duration=3000)
        if not self.is_logged_in or not self.user:
            return
        prefix = "ctl_"
        token = secrets.token_urlsafe(32)
        full_key = f"{prefix}{token}"
        hashed_key = hashlib.sha256(full_key.encode()).hexdigest()
        with rx.session() as session:
            api_key = ApiKey(
                user_id=self.user.id,
                tenant_id=self.user.tenant_id,
                name=name,
                key_prefix=prefix,
                hashed_key=hashed_key,
                scopes=scopes,
            )
            session.add(api_key)
            session.commit()
        self.new_api_key = full_key
        self._log_audit("apikey.create", details=f"Key name: {name}")
        return ApiCenterState.load_api_keys

    @rx.event
    def revoke_api_key(self, key_id: int):
        if not self.is_logged_in:
            return
        with rx.session() as session:
            key_to_delete = session.get(ApiKey, key_id)
            if key_to_delete and key_to_delete.tenant_id == self.user.tenant_id:
                session.delete(key_to_delete)
                session.commit()
                self._log_audit("apikey.revoke", details=f"Key ID: {key_id}")
        return ApiCenterState.load_api_keys

    def _get_paths(self):
        return {
            "/v1/projects": {
                "get": {
                    "tags": ["Projects"],
                    "summary": "List Projects",
                    "responses": {"200": {"description": "OK"}},
                },
                "post": {
                    "tags": ["Projects"],
                    "summary": "Create Project",
                    "responses": {"201": {"description": "Created"}},
                },
            },
            "/v1/projects/{id}": {
                "get": {
                    "tags": ["Projects"],
                    "summary": "Get Project",
                    "responses": {"200": {"description": "OK"}},
                },
                "patch": {
                    "tags": ["Projects"],
                    "summary": "Update Project",
                    "responses": {"200": {"description": "OK"}},
                },
                "delete": {
                    "tags": ["Projects"],
                    "summary": "Delete Project",
                    "responses": {"204": {"description": "No Content"}},
                },
            },
            "/v1/runs": {
                "post": {
                    "tags": ["Runs"],
                    "summary": "Create a new Run",
                    "parameters": [
                        {
                            "name": "Idempotency-Key",
                            "in": "header",
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {"202": {"description": "Accepted"}},
                },
                "get": {
                    "tags": ["Runs"],
                    "summary": "List Runs",
                    "parameters": [
                        {
                            "name": "project_id",
                            "in": "query",
                            "schema": {"type": "string"},
                        },
                        {"name": "limit", "in": "query", "schema": {"type": "integer"}},
                        {"name": "cursor", "in": "query", "schema": {"type": "string"}},
                    ],
                    "responses": {"200": {"description": "OK"}},
                },
            },
            "/v1/runs/{id}": {
                "get": {
                    "tags": ["Runs"],
                    "summary": "Get Run",
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/v1/runs/{id}:cancel": {
                "post": {
                    "tags": ["Runs"],
                    "summary": "Cancel a Run",
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/v1/runs/{id}/artifacts": {
                "get": {
                    "tags": ["Artifacts"],
                    "summary": "List Run Artifacts",
                    "responses": {"200": {"description": "OK"}},
                }
            },
            "/v1/artifacts/{artifact_id}": {
                "get": {
                    "tags": ["Artifacts"],
                    "summary": "Get Artifact Details",
                    "responses": {"200": {"description": "OK"}},
                }
            },
        }

    def _get_components(self):
        return {
            "securitySchemes": {
                "GatewayJWT": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "Colabe Gateway JWT for end-users.",
                },
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "Personal Access Token (PAT) for programmatic access.",
                },
            },
            "schemas": {
                "Error": {
                    "type": "object",
                    "properties": {
                        "error_code": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object"},
                        "trace_id": {"type": "string"},
                    },
                }
            },
        }