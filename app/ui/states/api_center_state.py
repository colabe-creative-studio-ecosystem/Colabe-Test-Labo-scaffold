import reflex as rx
import json
import secrets
import bcrypt
import sqlmodel
from datetime import datetime
from app.ui.states.auth_state import AuthState
from app.core.models import APIKey, User


class ApiCenterState(AuthState):
    openapi_spec: dict = {}
    api_keys: list[dict] = []
    newly_created_key: str = ""
    available_scopes: list[str] = [
        "runs:read",
        "runs:write",
        "artifacts:read",
        "policies:write",
        "autofix:write",
        "billing:read",
    ]

    @rx.event
    def on_load_spec(self):
        self.check_login()
        if not self.openapi_spec:
            self._generate_openapi_spec()

    def _generate_openapi_spec(self):
        self.openapi_spec = {
            "openapi": "3.0.3",
            "info": {
                "title": "Colabe Test Labo API",
                "version": "v1",
                "description": "Developer-first API for Colabe Test Labo.",
                "contact": {"email": "developers@colabe.ai"},
            },
            "servers": [{"url": "/api"}],
            "tags": [
                {"name": "Projects", "description": "Manage projects"},
                {"name": "Runs", "description": "Manage test runs"},
                {"name": "Artifacts", "description": "Access run artifacts"},
                {"name": "Policies", "description": "Manage policies"},
                {"name": "Autofix", "description": "Manage autofix proposals"},
                {"name": "Billing", "description": "Manage billing and wallet"},
                {"name": "Admin", "description": "Service-to-service admin operations"},
            ],
            "paths": self._get_paths(),
            "components": self._get_components(),
        }

    @rx.var
    def get_openapi_json(self) -> dict:
        """API route to serve the OpenAPI JSON."""
        if not self.openapi_spec:
            self._generate_openapi_spec()
        return self.openapi_spec

    @rx.var
    def get_asyncapi_json(self) -> dict:
        """API route to serve the AsyncAPI JSON."""
        return {
            "asyncapi": "2.0.0",
            "info": {"title": "Colabe Test Labo Streams API", "version": "v1"},
            "channels": {},
        }

    @rx.event
    def load_api_keys(self):
        if not self.is_logged_in:
            return rx.redirect("/login")
        with rx.session() as session:
            keys = session.exec(
                sqlmodel.select(APIKey).where(
                    APIKey.tenant_id == self.user.tenant_id, APIKey.revoked == False
                )
            ).all()
            self.api_keys = [
                {
                    "id": key.id,
                    "name": key.name,
                    "prefix": key.prefix,
                    "scopes": key.scopes,
                    "last_used_at": key.last_used_at.strftime("%Y-%m-%d %H:%M")
                    if key.last_used_at
                    else "Never",
                    "created_at": key.created_at.strftime("%Y-%m-%d"),
                }
                for key in keys
            ]

    @rx.event
    def create_api_key(self, form_data: dict):
        if not self.is_logged_in:
            return
        key_name = form_data.get("name")
        selected_scopes = [k for k, v in form_data.items() if k.startswith("scopes[")]
        scopes_list = [s.split("=")[1] for s in selected_scopes if "=" in s]
        if not key_name or not scopes_list:
            return rx.toast(
                "Key name and at least one scope are required.", duration=3000
            )
        prefix = "ctl_" + secrets.token_urlsafe(8)
        api_key_str = secrets.token_urlsafe(32)
        hashed_key = bcrypt.hashpw(api_key_str.encode(), bcrypt.gensalt()).decode()
        with rx.session() as session:
            new_key = APIKey(
                tenant_id=self.user.tenant_id,
                user_id=self.user.id,
                name=key_name,
                prefix=prefix,
                hashed_key=hashed_key,
                scopes=",".join(scopes_list),
            )
            session.add(new_key)
            session.commit()
        self.newly_created_key = f"{prefix}_{api_key_str}"
        self.load_api_keys()

    @rx.event
    def revoke_api_key(self, key_id: int):
        with rx.session() as session:
            key_to_revoke = session.get(APIKey, key_id)
            if key_to_revoke and key_to_revoke.tenant_id == self.user.tenant_id:
                key_to_revoke.revoked = True
                session.add(key_to_revoke)
                session.commit()
        self.load_api_keys()

    @rx.event
    def clear_new_key(self):
        self.newly_created_key = ""

    def _get_paths(self):
        return {
            "/v1/projects": {
                "get": {"tags": ["Projects"], "summary": "List Projects"},
                "post": {
                    "tags": ["Projects"],
                    "summary": "Create Project",
                    "headers": {"Idempotency-Key": {"schema": {"type": "string"}}},
                },
            },
            "/v1/projects/{id}": {
                "get": {"tags": ["Projects"], "summary": "Get Project"},
                "patch": {"tags": ["Projects"], "summary": "Update Project"},
                "delete": {"tags": ["Projects"], "summary": "Delete Project"},
            },
            "/v1/runs": {
                "get": {
                    "tags": ["Runs"],
                    "summary": "List Runs",
                    "parameters": [{"name": "project_id", "in": "query"}],
                },
                "post": {
                    "tags": ["Runs"],
                    "summary": "Create a new Run",
                    "headers": {"Idempotency-Key": {"schema": {"type": "string"}}},
                },
            },
            "/v1/runs/{id}": {"get": {"tags": ["Runs"], "summary": "Get Run details"}},
            "/v1/runs/{id}:cancel": {
                "post": {"tags": ["Runs"], "summary": "Cancel a Run"}
            },
            "/v1/runs/{id}/artifacts": {
                "get": {"tags": ["Artifacts"], "summary": "List Run Artifacts"}
            },
            "/v1/artifacts/{artifact_id}": {
                "get": {"tags": ["Artifacts"], "summary": "Get Artifact details"}
            },
            "/v1/policies": {"get": {"tags": ["Policies"], "summary": "List Policies"}},
            "/v1/policies/{scope}": {
                "get": {"tags": ["Policies"], "summary": "Get Policy for a scope"},
                "put": {"tags": ["Policies"], "summary": "Update Policy for a scope"},
            },
            "/v1/estimates/run": {
                "post": {"tags": ["Billing"], "summary": "Estimate cost for a run"}
            },
            "/v1/usage": {"get": {"tags": ["Billing"], "summary": "Get usage data"}},
            "/v1/autofix/{run_id}:propose": {
                "post": {"tags": ["Autofix"], "summary": "Propose an autofix"}
            },
            "/v1/autofix/{proposal_id}": {
                "get": {"tags": ["Autofix"], "summary": "Get autofix proposal"}
            },
            "/v1/autofix/{proposal_id}:apply": {
                "post": {"tags": ["Autofix"], "summary": "Apply an autofix proposal"}
            },
            "/v1/wallet": {
                "get": {"tags": ["Billing"], "summary": "Get wallet balance"}
            },
            "/v1/invoices": {"get": {"tags": ["Billing"], "summary": "List invoices"}},
            "/v1/wallet:hold": {
                "post": {"tags": ["Billing"], "summary": "Place a hold on wallet"}
            },
            "/v1/wallet:finalize": {
                "post": {
                    "tags": ["Billing"],
                    "summary": "Finalize a wallet transaction",
                }
            },
            "/v1/wallet:refund": {
                "post": {"tags": ["Billing"], "summary": "Refund a wallet transaction"}
            },
            "/v1/admin/provision": {
                "post": {"tags": ["Admin"], "summary": "Provision a new tenant"}
            },
            "/v1/admin/health": {
                "get": {"tags": ["Admin"], "summary": "Get system health"}
            },
        }

    def _get_components(self):
        return {
            "securitySchemes": {
                "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
                "GatewayJWT": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
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