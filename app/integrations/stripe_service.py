import stripe
import logging
from app.core.settings import settings
from typing import Optional

logger = logging.getLogger(__name__)


class StripeService:
    def __init__(self):
        if settings.STRIPE_SECRET_KEY:
            stripe.api_key = settings.STRIPE_SECRET_KEY
        else:
            logger.warning(
                "STRIPE_SECRET_KEY not set. Stripe features will be disabled."
            )

    def create_customer(self, name: str, email: str, tenant_id: int) -> Optional[str]:
        """Creates a new Stripe customer for the tenant."""
        if not stripe.api_key:
            return None
        try:
            customer = stripe.Customer.create(
                name=name, email=email, metadata={"tenant_id": str(tenant_id)}
            )
            return customer.id
        except Exception as e:
            logger.exception(f"Failed to create Stripe customer: {e}")
            return None

    def create_checkout_session(
        self,
        customer_id: str,
        price_data: dict,
        mode: str,
        metadata: dict,
        success_url: str,
        cancel_url: str,
    ) -> Optional[str]:
        """Creates a Stripe Checkout Session."""
        if not stripe.api_key:
            return None
        try:
            session = stripe.checkout.Session.create(
                customer=customer_id,
                payment_method_types=["card"],
                line_items=[{"price_data": price_data, "quantity": 1}],
                mode=mode,
                success_url=success_url,
                cancel_url=cancel_url,
                metadata=metadata,
            )
            return session.url
        except Exception as e:
            logger.exception(f"Failed to create checkout session: {e}")
            return None

    def create_portal_session(self, customer_id: str, return_url: str) -> Optional[str]:
        """Creates a Billing Portal session for managing subscriptions."""
        if not stripe.api_key:
            return None
        try:
            session = stripe.billing_portal.Session.create(
                customer=customer_id, return_url=return_url
            )
            return session.url
        except Exception as e:
            logger.exception(f"Failed to create portal session: {e}")
            return None

    def list_invoices(self, customer_id: str, limit: int = 10) -> list[dict]:
        """Retrieves a list of invoices for the customer."""
        try:
            invoices = stripe.Invoice.list(
                customer=customer_id, limit=limit, status="paid"
            )
            return [
                {
                    "id": inv.id,
                    "amount": inv.amount_paid / 100.0,
                    "currency": inv.currency.upper(),
                    "date": inv.created,
                    "status": inv.status,
                    "pdf_url": inv.hosted_invoice_url,
                    "number": inv.number,
                }
                for inv in invoices.data
            ]
        except Exception as e:
            logger.exception(f"Failed to list invoices: {e}")
            return []

    def construct_event(
        self, payload: bytes, sig_header: str
    ) -> Optional[stripe.Event]:
        """Verifies and constructs a webhook event."""
        try:
            return stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except ValueError as e:
            logger.exception(f"Invalid payload: {e}")
            return None
        except stripe.error.SignatureVerificationError as e:
            logger.exception(f"Invalid signature: {e}")
            return None