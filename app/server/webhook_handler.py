"""
Webhook handler for inbound events
Integrates with the inbound processor pipeline
"""

from starlette.requests import Request
from starlette.responses import JSONResponse
import logging
import json

from app.server.inbound_processor import (
    process_inbound_event,
    TransientError,
    PermanentError,
)

logger = logging.getLogger(__name__)


async def inbound_webhook_handler(request: Request):
    """
    Handle incoming webhook events and route to inbound processor

    Expected payload:
    {
        "type": "message.received",
        "workspace_id": "123",
        "conversation_id": "conv_456",
        "channel": "slack",
        "payload": {...}
    }
    """
    try:
        # Parse request body
        body = await request.body()
        event_data = json.loads(body.decode("utf-8"))

        logger.info(f"Received inbound webhook event: {event_data.get('type')}")

        # Process the event through the pipeline
        result = await process_inbound_event(event_data)

        return JSONResponse(
            {
                "status": "success",
                "result": result,
            },
            status_code=200,
        )

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON payload: {e}")
        return JSONResponse(
            {"status": "error", "error": "Invalid JSON payload"}, status_code=400
        )

    except PermanentError as e:
        logger.error(f"Permanent error processing webhook: {e}")
        return JSONResponse(
            {"status": "error", "error": str(e), "retryable": False}, status_code=400
        )

    except TransientError as e:
        logger.warning(f"Transient error processing webhook: {e}")
        return JSONResponse(
            {"status": "error", "error": str(e), "retryable": True}, status_code=503
        )

    except Exception as e:
        logger.exception(f"Unexpected error processing webhook: {e}")
        return JSONResponse(
            {"status": "error", "error": "Internal server error"}, status_code=500
        )
