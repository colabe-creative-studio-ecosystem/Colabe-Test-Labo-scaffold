from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route
import reflex as rx
from app.integrations.stripe_service import StripeService
from app.core.models import Tenant, Wallet, Subscription, Invoice, CoinPack, AuditLog
import sqlmodel
import logging
from datetime import datetime

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


stripe_webhook_routes = [
    Route("/api/webhook/stripe", endpoint=stripe_webhook, methods=["POST"])
]


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