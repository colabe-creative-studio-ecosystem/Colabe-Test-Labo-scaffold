import reflex as rx
import sqlmodel
from typing import Optional, TypedDict, Literal
from app.ui.states.auth_state import AuthState
from app.core.models import Wallet, Subscription, InvoicesIndex, BillingSettings
import datetime
import plotly.graph_objects as go

PlanID = Literal["free", "pro", "enterprise"]


class Plan(TypedDict):
    id: PlanID
    name: str
    price_monthly: float
    coins_per_month: int
    concurrency: int
    artifacts_gb: int
    retention_days: int
    autofix_attempts: int


class CoinPack(TypedDict):
    id: str
    name: str
    coins: int
    price_eur: float


class Invoice(TypedDict):
    id: str
    date: str
    status: str
    amount: float
    pdf_url: str


class BillingState(AuthState):
    wallet_balance: int = 0
    plan_id: str = "free"
    renewal_date: str = "N/A"
    is_admin_or_owner: bool = False
    pricing_last_updated: str = ""
    plans: list[Plan] = []
    coin_packs: list[CoinPack] = []
    invoices: list[Invoice] = []
    usage_data_7d: list[dict] = []
    usage_data_30d: list[dict] = []
    billing_settings: BillingSettings | None = None
    show_paywall_modal: bool = False
    paywall_reason: str = ""
    estimated_cost: int = 0
    selected_coin_pack_id: str = ""

    def _load_mock_data(self):
        self.pricing_last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.plans = [
            {
                "id": "free",
                "name": "Free",
                "price_monthly": 0,
                "coins_per_month": 500,
                "concurrency": 1,
                "artifacts_gb": 1,
                "retention_days": 7,
                "autofix_attempts": 0,
            },
            {
                "id": "pro",
                "name": "Pro",
                "price_monthly": 49,
                "coins_per_month": 10000,
                "concurrency": 3,
                "artifacts_gb": 20,
                "retention_days": 30,
                "autofix_attempts": 200,
            },
            {
                "id": "enterprise",
                "name": "Enterprise",
                "price_monthly": -1,
                "coins_per_month": -1,
                "concurrency": -1,
                "artifacts_gb": -1,
                "retention_days": -1,
                "autofix_attempts": -1,
            },
        ]
        self.coin_packs = [
            {"id": "pack_1k", "name": "1,000 Coins", "coins": 1000, "price_eur": 10.0},
            {"id": "pack_5k", "name": "5,000 Coins", "coins": 5000, "price_eur": 45.0},
            {
                "id": "pack_20k",
                "name": "20,000 Coins",
                "coins": 20000,
                "price_eur": 160.0,
            },
        ]
        self.invoices = [
            {
                "id": "inv_1",
                "date": "2024-07-01",
                "status": "Paid",
                "amount": 49.0,
                "pdf_url": "#",
            },
            {
                "id": "inv_2",
                "date": "2024-06-01",
                "status": "Paid",
                "amount": 49.0,
                "pdf_url": "#",
            },
        ]
        self.usage_data_30d = [
            {"name": "Quick Sweep", "coins": 1500},
            {"name": "Playwright", "coins": 4200},
            {"name": "Appium", "coins": 2500},
            {"name": "Lighthouse", "coins": 800},
            {"name": "Autofix", "coins": 1250},
            {"name": "Storage", "coins": 320},
        ]
        self.usage_data_7d = [
            {"name": "Quick Sweep", "coins": 350},
            {"name": "Playwright", "coins": 1100},
            {"name": "Appium", "coins": 600},
            {"name": "Lighthouse", "coins": 200},
            {"name": "Autofix", "coins": 500},
            {"name": "Storage", "coins": 80},
        ]

    @rx.event
    def load_billing_page(self):
        if not self.is_logged_in or not self.user:
            return rx.redirect("/login")
        with rx.session() as session:
            wallet = session.exec(
                sqlmodel.select(Wallet).where(Wallet.tenant_id == self.user.tenant_id)
            ).first()
            if wallet:
                self.wallet_balance = wallet.coins_balance
            subscription = session.exec(
                sqlmodel.select(Subscription).where(
                    Subscription.tenant_id == self.user.tenant_id
                )
            ).first()
            if subscription:
                self.plan_id = subscription.plan_id
                self.renewal_date = (
                    subscription.renews_at.strftime("%Y-%m-%d")
                    if subscription.renews_at
                    else "N/A"
                )
            self.billing_settings = session.exec(
                sqlmodel.select(BillingSettings).where(
                    BillingSettings.tenant_id == self.user.tenant_id
                )
            ).first()
        self._load_mock_data()
        self.is_admin_or_owner = self.current_user_role in ["admin", "owner"]
        self._log_audit("billing.page.viewed")

    @rx.var
    def current_plan(self) -> Plan | None:
        for plan in self.plans:
            if plan["id"] == self.plan_id:
                return plan
        return None

    @rx.var
    def usage_chart_fig(self) -> go.Figure:
        if not self.usage_data_30d:
            return go.Figure()
        names = [d["name"] for d in self.usage_data_30d]
        coins = [d["coins"] for d in self.usage_data_30d]
        fig = go.Figure(
            data=[
                go.Bar(
                    name="Usage",
                    x=coins,
                    y=names,
                    orientation="h",
                    marker=dict(color="var(--accent-cyan)"),
                )
            ]
        )
        fig.update_layout(
            title_text="Coin Usage (Last 30 Days)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="var(--text-secondary)"),
            showlegend=False,
            margin=dict(l=100, r=20, t=40, b=20),
            xaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
            yaxis=dict(gridcolor="rgba(255,255,255,0.1)"),
        )
        return fig

    @rx.event
    def update_billing_settings(self, form_data: dict):
        if not self.is_admin_or_owner:
            return rx.toast("Permission denied.", duration=3000)
        with rx.session() as session:
            settings = self.billing_settings or BillingSettings(
                tenant_id=self.user.tenant_id
            )
            settings.auto_top_up_enabled = form_data.get("auto_top_up_enabled") == "on"
            settings.auto_top_up_threshold = int(form_data["auto_top_up_threshold"])
            settings.auto_top_up_amount = int(form_data["auto_top_up_amount"])
            settings.billing_email = form_data["billing_email"]
            settings.vat_id = form_data["vat_id"]
            session.add(settings)
            session.commit()
            session.refresh(settings)
            self.billing_settings = settings
        self._log_audit("billing.settings.updated")
        return rx.toast("Settings updated!", duration=3000)

    @rx.event
    def select_coin_pack(self, pack_id: str):
        self.selected_coin_pack_id = pack_id

    @rx.event
    def purchase_coins(self):
        if not self.selected_coin_pack_id:
            return rx.toast("Please select a coin pack.", duration=3000)
        self._log_audit(
            f"billing.coins.purchase.initiated",
            details=f"pack_id={self.selected_coin_pack_id}",
        )
        self.show_paywall_modal = False
        return rx.toast("Redirecting to checkout...", duration=3000)

    @rx.event
    def upgrade_plan(self, plan_id: str):
        self._log_audit(
            f"billing.subscription.upgrade.initiated", details=f"plan_id={plan_id}"
        )
        self.show_paywall_modal = False
        return rx.toast("Redirecting to checkout...", duration=3000)

    @rx.event
    def open_paywall(self, reason: str, cost: int):
        self.paywall_reason = reason
        self.estimated_cost = cost
        self.show_paywall_modal = True

    @rx.event
    def close_paywall(self):
        self.show_paywall_modal = False