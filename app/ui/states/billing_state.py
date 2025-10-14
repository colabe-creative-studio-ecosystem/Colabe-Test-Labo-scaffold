import reflex as rx
import sqlmodel
from typing import Optional
from app.ui.states.auth_state import AuthState
from app.core.models import Wallet, Subscription


class BillingState(AuthState):
    wallet_balance: int = 0
    subscription_plan: str = "Free"
    renewal_date: str = "N/A"

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