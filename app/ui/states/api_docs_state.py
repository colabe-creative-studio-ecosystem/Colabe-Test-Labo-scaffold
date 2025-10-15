import reflex as rx
import json
from app.ui.states.auth_state import AuthState


class ApiDocsState(AuthState):
    openapi_json_str: str = ""

    @rx.event
    def generate_openapi_spec(self):
        openapi_spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Colabe Test Labo API",
                "version": "1.0.0",
                "description": "OpenAPI 3.0 for CRUD operations, run triggers, artifact retrieval, webhooks, and API key management.",
            },
            "servers": [{"url": "/api/v1"}],
            "security": [{"ApiKeyAuth": []}],
            "paths": self._get_paths(),
            "components": self._get_components(),
            "webhooks": self._get_webhooks(),
        }
        self.openapi_json_str = json.dumps(openapi_spec, indent=2)

    def _get_paths(self) -> dict:
        return {
            "/projects": {
                "get": {
                    "summary": "List Projects",
                    "description": "Retrieves a list of projects for the authenticated user.",
                    "responses": {
                        "200": {
                            "description": "A list of projects.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Project"
                                        },
                                    }
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                        "429": {"description": "Rate limit exceeded"},
                    },
                },
                "post": {
                    "summary": "Create Project",
                    "description": "Creates a new project.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ProjectInput"}
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Project created.",
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/Project"}
                                }
                            },
                        },
                        "400": {"description": "Invalid input"},
                        "401": {"description": "Unauthorized"},
                    },
                },
            },
            "/projects/{projectId}/runs": {
                "post": {
                    "summary": "Trigger a New Run",
                    "description": "Starts a new test run for a specific project and test plan.",
                    "parameters": [
                        {
                            "name": "projectId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RunInput"}
                            }
                        },
                    },
                    "responses": {
                        "202": {"description": "Run accepted and queued."},
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Project not found"},
                    },
                }
            },
            "/runs/{runId}/artifacts": {
                "get": {
                    "summary": "List Run Artifacts",
                    "description": "Retrieves a list of artifacts for a specific run.",
                    "parameters": [
                        {
                            "name": "runId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "List of artifacts.",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "$ref": "#/components/schemas/Artifact"
                                        },
                                    }
                                }
                            },
                        },
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Run not found"},
                    },
                }
            },
            "/artifacts/{artifactId}": {
                "get": {
                    "summary": "Retrieve Artifact",
                    "description": "Downloads the specified artifact file.",
                    "parameters": [
                        {
                            "name": "artifactId",
                            "in": "path",
                            "required": True,
                            "schema": {"type": "integer"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Artifact file content.",
                            "content": {"application/octet-stream": {}},
                        },
                        "401": {"description": "Unauthorized"},
                        "404": {"description": "Artifact not found"},
                    },
                }
            },
            "/support/v1/tickets": {
                "post": {
                    "summary": "Create Support Ticket",
                    "description": "Creates a new support ticket.",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SupportTicketInput"
                                }
                            }
                        },
                    },
                    "responses": {
                        "201": {
                            "description": "Ticket Created",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/SupportTicket"
                                    }
                                }
                            },
                        }
                    },
                }
            },
        }

    def _get_components(self) -> dict:
        return {
            "securitySchemes": {
                "ApiKeyAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-API-Key",
                    "description": "API key for project-level access.",
                }
            },
            "schemas": {
                "Project": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                    },
                },
                "ProjectInput": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"],
                },
                "RunInput": {
                    "type": "object",
                    "properties": {"test_plan_id": {"type": "integer"}},
                    "required": ["test_plan_id"],
                },
                "Artifact": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "storage_path": {"type": "string"},
                        "created_at": {"type": "string", "format": "date-time"},
                    },
                },
                "RunEvent": {
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string", "enum": ["run.completed"]},
                        "run_id": {"type": "integer"},
                        "status": {"type": "string"},
                        "completed_at": {"type": "string", "format": "date-time"},
                    },
                },
                "PREvent": {
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string", "enum": ["pr.status.updated"]},
                        "repository_url": {"type": "string"},
                        "pr_number": {"type": "integer"},
                        "commit_sha": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["pending", "success", "failure"],
                        },
                    },
                },
                "SupportTicket": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "subject": {"type": "string"},
                        "status": {"type": "string"},
                        "opened_at": {"type": "string", "format": "date-time"},
                    },
                },
                "SupportTicketInput": {
                    "type": "object",
                    "properties": {
                        "subject": {"type": "string"},
                        "body": {"type": "string"},
                        "severity": {
                            "type": "string",
                            "enum": ["SEV1", "SEV2", "SEV3", "SEV4"],
                        },
                    },
                    "required": ["subject", "body"],
                },
                "SupportTicketEvent": {
                    "type": "object",
                    "properties": {
                        "event_type": {"type": "string"},
                        "ticket_id": {"type": "integer"},
                        "status": {"type": "string"},
                        "timestamp": {"type": "string", "format": "date-time"},
                    },
                },
            },
        }

    def _get_webhooks(self) -> dict:
        return {
            "runEvent": {
                "post": {
                    "summary": "Webhook for Run Events",
                    "description": "Triggered when a run completes (succeeds or fails).",
                    "requestBody": {
                        "description": "Run event payload",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/RunEvent"}
                            }
                        },
                    },
                    "responses": {"200": {"description": "Webhook received."}},
                }
            },
            "prStatusUpdate": {
                "post": {
                    "summary": "Webhook for PR Status",
                    "description": "Triggered to update the status of a pull request in the git provider.",
                    "requestBody": {
                        "description": "PR status update payload",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/PREvent"}
                            }
                        },
                    },
                    "responses": {"200": {"description": "Webhook received."}},
                }
            },
            "supportTicketUpdate": {
                "post": {
                    "summary": "Webhook for Support Ticket Updates",
                    "description": "Fired when a support ticket is created, updated, resolved, or closed.",
                    "requestBody": {
                        "description": "Support ticket event payload",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/SupportTicketEvent"
                                }
                            }
                        },
                    },
                    "responses": {"200": {"description": "Webhook received."}},
                }
            },
        }