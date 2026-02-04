from starlette.requests import Request
from starlette.responses import JSONResponse
import reflex as rx
from app.integrations.stripe_service import StripeService
from app.core.models import Tenant, Wallet, Subscription, Invoice, CoinPack, AuditLog, EngineEvent
import sqlmodel
import logging
from datetime import datetime
from app.integrations.whatsapp_parser import (
    parse_whatsapp_webhook,
    validate_webhook_signature,
    WhatsAppParserError,
    UnsupportedMessageTypeError,
    InvalidMessageFormatError,
)
import os
import json

logger = logging.getLogger(__name__)
stripe_service = StripeService()


async def stripe_webhook(request: Request):
    stripe_signature = request.headers.get("stripe-signature")
    if not stripe_signature:
        return JSONResponse({"detail": "Missing signature"}, status_code=400)
    payload = await request.body()
    event = stripe_service.construct_event(payload, stripe_signature)
    if not event:
        return JSONResponse({"detail": "Invalid payload or signature"}, status_code=400)
    try:
        if event["type"] == "checkout.session.completed":
            session = event["data"]["object"]
            await handle_checkout_completed(session)
        elif event["type"] == "invoice.payment_succeeded":
            invoice = event["data"]["object"]
            await handle_invoice_payment_succeeded(invoice)
        elif event["type"] == "customer.subscription.updated":
            sub = event["data"]["object"]
            await handle_subscription_updated(sub)
        elif event["type"] == "customer.subscription.deleted":
            sub = event["data"]["object"]
            await handle_subscription_deleted(sub)
        return JSONResponse({"status": "success"})
    except Exception as e:
        logger.exception(f"Error processing webhook: {e}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


async def handle_checkout_completed(session: dict):
    metadata = session.get("metadata", {})
    tenant_id = metadata.get("tenant_id")
    type_ = metadata.get("type")
    if not tenant_id:
        return
    with rx.session() as db_session:
        tenant_id = int(tenant_id)
        if type_ == "coin_pack":
            coins = int(metadata.get("coins", 0))
            amount_paid = session.get("amount_total", 0) / 100.0
            currency = session.get("currency", "eur")
            wallet = db_session.exec(
                sqlmodel.select(Wallet).where(Wallet.tenant_id == tenant_id)
            ).first()
            if wallet:
                wallet.coins += coins
                db_session.add(wallet)
            invoice = Invoice(
                tenant_id=tenant_id,
                amount=amount_paid,
                currency=currency,
                status="paid",
                paid_at=datetime.now(),
                stripe_payment_intent_id=session.get("payment_intent"),
                download_url=None,
            )
            db_session.add(invoice)
            db_session.commit()
        elif type_ == "subscription":
            sub_id = session.get("subscription")
            plan_name = metadata.get("plan")
            subscription = db_session.exec(
                sqlmodel.select(Subscription).where(Subscription.tenant_id == tenant_id)
            ).first()
            if subscription:
                subscription.stripe_subscription_id = sub_id
                subscription.plan = plan_name
                subscription.status = "active"
                db_session.add(subscription)
                db_session.commit()


async def handle_invoice_payment_succeeded(invoice_data: dict):
    customer_id = invoice_data.get("customer")
    if not customer_id:
        return
    with rx.session() as db_session:
        tenant = db_session.exec(
            sqlmodel.select(Tenant).where(Tenant.stripe_customer_id == customer_id)
        ).first()
        if not tenant:
            return
        amount_paid = invoice_data.get("amount_paid", 0) / 100.0
        currency = invoice_data.get("currency", "eur")
        hosted_invoice_url = invoice_data.get("hosted_invoice_url")
        existing = db_session.exec(
            sqlmodel.select(Invoice).where(
                Invoice.stripe_invoice_id == invoice_data.get("id")
            )
        ).first()
        if not existing:
            new_invoice = Invoice(
                tenant_id=tenant.id,
                amount=amount_paid,
                currency=currency,
                status="paid",
                paid_at=datetime.now(),
                stripe_invoice_id=invoice_data.get("id"),
                download_url=hosted_invoice_url,
            )
            db_session.add(new_invoice)
            db_session.commit()


async def handle_subscription_updated(sub: dict):
    sub_id = sub.get("id")
    status = sub.get("status")
    with rx.session() as db_session:
        subscription = db_session.exec(
            sqlmodel.select(Subscription).where(
                Subscription.stripe_subscription_id == sub_id
            )
        ).first()
        if subscription:
            subscription.status = status
            db_session.add(subscription)
            db_session.commit()


async def handle_subscription_deleted(sub: dict):
    sub_id = sub.get("id")
    with rx.session() as db_session:
        subscription = db_session.exec(
            sqlmodel.select(Subscription).where(
                Subscription.stripe_subscription_id == sub_id
            )
        ).first()
        if subscription:
            subscription.status = "canceled"
            subscription.plan = "Free"
            subscription.stripe_subscription_id = None
            db_session.add(subscription)
            db_session.commit()


async def whatsapp_webhook(request: Request):
    """
    Handle WhatsApp webhook events for inbound messages.
    
    Supports:
    - Text messages
    - Button replies
    - List replies
    - Media metadata (reference only)
    - Delivery/read receipts (optional)
    
    Returns EngineEvent with structured data.
    """
    # Get webhook verification mode (for initial setup)
    if request.method == "GET":
        # WhatsApp webhook verification
        query_params = request.query_params
        mode = query_params.get("hub.mode")
        token = query_params.get("hub.verify_token")
        challenge = query_params.get("hub.challenge")
        
        verify_token = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
        
        if mode == "subscribe" and token == verify_token:
            logger.info("WhatsApp webhook verified successfully")
            return JSONResponse({"hub.challenge": challenge}, status_code=200)
        else:
            logger.warning("WhatsApp webhook verification failed")
            return JSONResponse({"detail": "Verification failed"}, status_code=403)
    
    # Handle POST webhooks (actual events)
    try:
        # Get signature for validation
        signature = request.headers.get("x-hub-signature-256", "")
        payload = await request.body()
        
        # Validate signature if secret is configured
        app_secret = os.environ.get("WHATSAPP_APP_SECRET", "")
        if app_secret:
            if not validate_webhook_signature(payload, signature, app_secret):
                logger.error("Invalid WhatsApp webhook signature")
                return JSONResponse({"detail": "Invalid signature"}, status_code=401)
        
        # Parse payload
        try:
            webhook_data = json.loads(payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error(f"Failed to parse webhook payload: {e}")
            return JSONResponse({"detail": "Invalid JSON payload"}, status_code=400)
        
        # Parse WhatsApp event
        try:
            event_data = parse_whatsapp_webhook(webhook_data)
        except InvalidMessageFormatError as e:
            logger.error(f"Invalid message format: {e}")
            return JSONResponse({"detail": str(e)}, status_code=400)
        except UnsupportedMessageTypeError as e:
            logger.info(f"Unsupported message type: {e}")
            # Return 200 to acknowledge receipt, but don't process
            return JSONResponse({"status": "unsupported_type"}, status_code=200)
        except WhatsAppParserError as e:
            logger.error(f"WhatsApp parsing error: {e}")
            return JSONResponse({"detail": str(e)}, status_code=400)
        
        # If no event data (e.g., not a message), acknowledge and return
        if not event_data:
            return JSONResponse({"status": "acknowledged"}, status_code=200)
        
        # Store event in database
        with rx.session() as db_session:
            engine_event = EngineEvent(
                type=event_data["type"],
                workspace_id=event_data["workspace_id"],
                conversation_id=event_data["conversation_id"],
                contact_id=event_data["contact_id"],
                message_id=event_data["message_id"],
                text=event_data.get("text"),
                interactive_type=event_data.get("interactive_type"),
                interactive_id=event_data.get("interactive_id"),
                interactive_title=event_data.get("interactive_title"),
                timestamp=event_data["timestamp"],
            )
            db_session.add(engine_event)
            db_session.commit()
            db_session.refresh(engine_event)
            
            logger.info(f"Stored WhatsApp event: {engine_event.id}")
        
        return JSONResponse({"status": "success", "event_id": engine_event.id})
        
    except Exception as e:
        logger.exception(f"Error processing WhatsApp webhook: {e}")
        return JSONResponse({"detail": "Internal server error"}, status_code=500)