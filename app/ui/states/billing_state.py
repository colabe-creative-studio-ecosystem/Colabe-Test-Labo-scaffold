import reflex as rx
import sqlmodel
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import Wallet, Subscription, Invoice, Tenant
from app.integrations.stripe_service import StripeService
from app.core.settings import settings


class BillingState(AuthState):
    wallet_balance: int = 0
    subscription_plan: str = "Free"
    renewal_date: str = "N/A"
    invoices: list[dict] = []
    payment_status_message: str = ""
    coin_packs: list[dict] = [
        {"coins": 500, "price": 10.0, "label": "Starter Pack"},
        {"coins": 1000, "price": 18.0, "label": "Standard Pack"},
        {"coins": 2500, "price": 40.0, "label": "Pro Pack"},
        {"coins": 5000, "price": 75.0, "label": "Enterprise Pack"},
    ]
    subscription_tiers: list[dict] = [
        {
            "name": "Pro",
            "price": 29.0,
            "features": [
                "Unlimited Projects",
                "Priority Support",
                "Advanced Analytics",
            ],
        },
        {
            "name": "Enterprise",
            "price": 99.0,
            "features": ["SSO", "Dedicated Account Manager", "Custom Integrations"],
        },
    ]

    @rx.event
    def load_billing_data(self):
        self.load_wallet()
        self.check_payment_status()

    @rx.event
    def load_wallet(self):
        if not self.is_logged_in or not self.user:
            return
        with rx.session() as session:
            wallet = session.exec(
                sqlmodel.select(Wallet).where(Wallet.tenant_id == self.user.tenant_id)
            ).first()
            if wallet:
                self.wallet_balance = wallet.coins
            subscription = session.exec(
                sqlmodel.select(Subscription).where(
                    Subscription.tenant_id == self.user.tenant_id
                )
            ).first()
            if subscription:
                self.subscription_plan = subscription.plan
                if subscription.renews_at:
                    self.renewal_date = subscription.renews_at.strftime("%Y-%m-%d")
                else:
                    self.renewal_date = "N/A"
            db_invoices = session.exec(
                sqlmodel.select(Invoice)
                .where(Invoice.tenant_id == self.user.tenant_id)
                .order_by(sqlmodel.desc(Invoice.created_at))
            ).all()
            self.invoices = [
                {
                    "date": inv.created_at.strftime("%Y-%m-%d"),
                    "amount": f"€{inv.amount:.2f}",
                    "status": inv.status.title(),
                    "pdf_url": inv.download_url,
                }
                for inv in db_invoices
            ]

    @rx.event
    def check_payment_status(self):
        query_params = self.router.url.query_parameters
        if "success" in query_params:
            self.payment_status_message = (
                "Payment successful! Thank you for your purchase."
            )
            return rx.toast(
                "Payment Successful",
                description="Your account has been updated.",
                style={"background_color": "#00D68F", "color": "white"},
            )
        elif "canceled" in query_params:
            self.payment_status_message = "Payment was canceled."
            return rx.toast(
                "Payment Canceled",
                description="No charges were made.",
                style={"background_color": "#FF3B3B", "color": "white"},
            )

    @rx.event
    async def buy_coins(self, amount: int, price: float):
        if not self.user:
            return
        service = StripeService()
        customer_id = await self._ensure_customer_id()
        if not customer_id:
            return rx.toast(
                "Billing Error", description="Could not verify customer account."
            )
        price_data = {
            "currency": "eur",
            "product_data": {
                "name": f"{amount} Coins",
                "description": "Credits for running test scans",
            },
            "unit_amount": int(price * 100),
        }
        metadata = {
            "type": "coin_pack",
            "tenant_id": str(self.user.tenant_id),
            "coins": str(amount),
        }
        url = service.create_checkout_session(
            customer_id=customer_id,
            price_data=price_data,
            mode="payment",
            metadata=metadata,
            success_url=f"{settings.DOMAIN}/billing?success=true",
            cancel_url=f"{settings.DOMAIN}/billing?canceled=true",
        )
        if url:
            return rx.redirect(url)
        else:
            return rx.toast("Stripe Error", description="Could not initiate checkout.")

    @rx.event
    async def subscribe(self, plan_name: str, price: float):
        if not self.user:
            return
        service = StripeService()
        customer_id = await self._ensure_customer_id()
        if not customer_id:
            return rx.toast(
                "Billing Error", description="Could not verify customer account."
            )
        price_data = {
            "currency": "eur",
            "product_data": {
                "name": f"{plan_name} Plan",
                "description": f"Subscription to {plan_name} tier",
            },
            "unit_amount": int(price * 100),
            "recurring": {"interval": "month"},
        }
        metadata = {
            "type": "subscription",
            "tenant_id": str(self.user.tenant_id),
            "plan": plan_name,
        }
        url = service.create_checkout_session(
            customer_id=customer_id,
            price_data=price_data,
            mode="subscription",
            metadata=metadata,
            success_url=f"{settings.DOMAIN}/billing?success=true",
            cancel_url=f"{settings.DOMAIN}/billing?canceled=true",
        )
        if url:
            return rx.redirect(url)

    @rx.event
    async def manage_subscription(self):
        if not self.user:
            return
        service = StripeService()
        customer_id = await self._ensure_customer_id()
        if not customer_id:
            return
        url = service.create_portal_session(
            customer_id=customer_id, return_url=f"{settings.DOMAIN}/billing"
        )
        if url:
            return rx.redirect(url)

    async def _ensure_customer_id(self) -> Optional[str]:
        """Ensures the tenant has a Stripe Customer ID."""
        with rx.session() as session:
            tenant = session.exec(
                sqlmodel.select(Tenant).where(Tenant.id == self.user.tenant_id)
            ).first()
            if not tenant:
                return None
            if tenant.stripe_customer_id:
                return tenant.stripe_customer_id
            service = StripeService()
            c_id = service.create_customer(
                name=tenant.name, email=self.user.email, tenant_id=tenant.id
            )
            if c_id:
                tenant.stripe_customer_id = c_id
                session.add(tenant)
                session.commit()
                session.refresh(tenant)
                return c_id
            return None