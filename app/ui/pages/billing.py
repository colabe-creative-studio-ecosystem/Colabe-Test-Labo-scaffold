import reflex as rx
from app.ui.states.billing_state import BillingState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def billing_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            BillingState.is_logged_in,
            rx.el.div(sidebar(), billing_page_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=BillingState.load_wallet,
    )


def billing_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Billing & Wallet",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Manage your subscription, coins, and view invoices.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Current Plan", class_name="text-xl font-semibold text-text-primary"
                ),
                rx.el.p(
                    BillingState.subscription_plan,
                    class_name="text-3xl font-bold text-accent-gold mt-2",
                ),
                rx.el.p(
                    f"Renews on: {BillingState.renewal_date}",
                    class_name="text-text-secondary",
                ),
                **card_style("gold"),
            ),
            rx.el.div(
                rx.el.h2(
                    "Wallet Balance",
                    class_name="text-xl font-semibold text-text-primary",
                ),
                rx.el.p(
                    BillingState.wallet_balance,
                    class_name="text-3xl font-bold text-accent-cyan mt-2",
                ),
                rx.el.p("coins available", class_name="text-text-secondary"),
                **card_style("cyan"),
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 p-8",
        ),
        class_name=page_content_style,
    )