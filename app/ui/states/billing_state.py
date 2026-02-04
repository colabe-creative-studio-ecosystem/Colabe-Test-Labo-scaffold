import reflex as rx
import sqlmodel
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import Wallet, Subscription, Invoice, Tenant
from app.integrations.stripe_service import StripeService
from app.core.settings import settings
from app.ui.utils import get_logger, notify_error, notify_success, notify_info

logger = get_logger(__name__)


class InvoiceDisplay(rx.Base):
    """Display model for invoice information."""
    date: str
    amount: str
    status: str
    pdf_url: str = ""


class CoinPackDisplay(rx.Base):
    """Display model for coin pack offerings."""
    coins: int
    price: float
    label: str


class TierDisplay(rx.Base):
    """Display model for subscription tier offerings."""
    name: str
    price: float
    features: list[str]


class BillingState(rx.State):
    """
    Billing and subscription management state.
    
    Handles wallet balance, coin purchases, subscription management,
    and Stripe integration for payment processing.
    """
    wallet_balance: int = 0
    subscription_plan: str = "Free"
    renewal_date: str = "N/A"
    invoices: list[InvoiceDisplay] = []
    payment_status_message: str = ""
    coin_packs: list[CoinPackDisplay] = [
        CoinPackDisplay(coins=500, price=10.0, label="Starter Pack"),
        CoinPackDisplay(coins=1000, price=18.0, label="Standard Pack"),
        CoinPackDisplay(coins=2500, price=40.0, label="Pro Pack"),
        CoinPackDisplay(coins=5000, price=75.0, label="Enterprise Pack"),
    ]
    subscription_tiers: list[TierDisplay] = [
        TierDisplay(
            name="Pro",
            price=29.0,
            features=["Unlimited Projects", "Priority Support", "Advanced Analytics"],
        ),
        TierDisplay(
            name="Enterprise",
            price=99.0,
            features=["SSO", "Dedicated Account Manager", "Custom Integrations"],
        ),
    ]

    async def _load_wallet(self):
        """Load wallet balance, subscription, and invoices for current user."""
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.is_logged_in or not auth_state.user:
                logger.debug("User not logged in, skipping wallet load")
                return
                
            with rx.session() as session:
                # Load wallet
                wallet = session.exec(
                    sqlmodel.select(Wallet).where(
                        Wallet.tenant_id == auth_state.user.tenant_id
                    )
                ).first()
                if wallet:
                    self.wallet_balance = wallet.coins
                    logger.debug(f"Loaded wallet balance: {wallet.coins} coins")
                    
                # Load subscription
                subscription = session.exec(
                    sqlmodel.select(Subscription).where(
                        Subscription.tenant_id == auth_state.user.tenant_id
                    )
                ).first()
                if subscription:
                    self.subscription_plan = subscription.plan
                    if subscription.renews_at:
                        self.renewal_date = subscription.renews_at.strftime("%Y-%m-%d")
                    else:
                        self.renewal_date = "N/A"
                    logger.debug(f"Loaded subscription: {subscription.plan}")
                    
                # Load invoices
                db_invoices = session.exec(
                    sqlmodel.select(Invoice)
                    .where(Invoice.tenant_id == auth_state.user.tenant_id)
                    .order_by(sqlmodel.desc(Invoice.created_at))
                ).all()
                self.invoices = [
                    InvoiceDisplay(
                        date=inv.created_at.strftime("%Y-%m-%d"),
                        amount=f"€{inv.amount:.2f}",
                        status=inv.status.title(),
                        pdf_url=inv.download_url or "",
                    )
                    for inv in db_invoices
                ]
                logger.info(f"Loaded {len(self.invoices)} invoices")
                
        except Exception as e:
            logger.exception(f"Error loading wallet data: {str(e)}")
            return notify_error("Failed to load billing information.")

    async def _check_payment_status(self):
        """Check URL parameters for payment status and notify user."""
        try:
            query_params = self.router.url.query_parameters
            if "success" in query_params:
                self.payment_status_message = (
                    "Payment successful! Thank you for your purchase."
                )
                logger.info("Payment successful")
                return notify_success("Payment successful! Your account has been updated.")
            elif "canceled" in query_params:
                self.payment_status_message = "Payment was canceled."
                logger.info("Payment canceled by user")
                return notify_info("Payment canceled. No charges were made.")
        except Exception as e:
            logger.error(f"Error checking payment status: {str(e)}")

    @rx.event
    async def load_billing_data(self):
        await self._load_wallet()
        await self._check_payment_status()

    @rx.event
    async def load_wallet(self):
        await self._load_wallet()

    @rx.event
    async def check_payment_status(self):
        await self._check_payment_status()

    @rx.event
    async def buy_coins(self, amount: int, price: float):
        """
        Initiate Stripe checkout for coin purchase.
        
        Args:
            amount: Number of coins to purchase
            price: Price in EUR
        """
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                logger.warning("Attempted coin purchase without authentication")
                return notify_error("Please log in to purchase coins.")
                
            service = StripeService()
            customer_id = await self._ensure_customer_id()
            if not customer_id:
                logger.error("Failed to get/create Stripe customer ID")
                return notify_error("Could not verify customer account.")
                
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
                "tenant_id": str(auth_state.user.tenant_id),
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
                logger.info(f"Created checkout session for {amount} coins")
                return rx.redirect(url)
            else:
                logger.error("Stripe checkout session creation failed")
                return notify_error("Could not initiate checkout.")
                
        except Exception as e:
            logger.exception(f"Error initiating coin purchase: {str(e)}")
            return notify_error("Failed to initiate purchase. Please try again.")

    @rx.event
    async def subscribe(self, plan_name: str, price: float):
        """
        Initiate Stripe checkout for subscription.
        
        Args:
            plan_name: Name of the subscription plan
            price: Monthly price in EUR
        """
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                logger.warning("Attempted subscription without authentication")
                return notify_error("Please log in to subscribe.")
                
            service = StripeService()
            customer_id = await self._ensure_customer_id()
            if not customer_id:
                logger.error("Failed to get/create Stripe customer ID for subscription")
                return notify_error("Could not verify customer account.")
                
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
                "tenant_id": str(auth_state.user.tenant_id),
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
                logger.info(f"Created subscription checkout for plan: {plan_name}")
                return rx.redirect(url)
            else:
                logger.error("Stripe subscription checkout creation failed")
                return notify_error("Could not initiate subscription checkout.")
                
        except Exception as e:
            logger.exception(f"Error initiating subscription: {str(e)}")
            return notify_error("Failed to initiate subscription. Please try again.")

    @rx.event
    async def manage_subscription(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
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
        """
        Ensures the tenant has a Stripe Customer ID.
        
        Creates a new customer in Stripe if one doesn't exist.
        
        Returns:
            Stripe customer ID or None on error
        """
        try:
            auth_state = await self.get_state(AuthState)
            if not auth_state.user:
                return None
                
            with rx.session() as session:
                tenant = session.exec(
                    sqlmodel.select(Tenant).where(Tenant.id == auth_state.user.tenant_id)
                ).first()
                if not tenant:
                    logger.error(f"Tenant not found: {auth_state.user.tenant_id}")
                    return None
                    
                if tenant.stripe_customer_id:
                    logger.debug(f"Using existing Stripe customer ID: {tenant.stripe_customer_id}")
                    return tenant.stripe_customer_id
                    
                service = StripeService()
                c_id = service.create_customer(
                    name=tenant.name, email=auth_state.user.email, tenant_id=tenant.id
                )
                if c_id:
                    tenant.stripe_customer_id = c_id
                    session.add(tenant)
                    session.commit()
                    session.refresh(tenant)
                    logger.info(f"Created new Stripe customer: {c_id}")
                    return c_id
                    
                logger.error("Failed to create Stripe customer")
                return None
                
        except Exception as e:
            logger.exception(f"Error ensuring customer ID: {str(e)}")
            return None