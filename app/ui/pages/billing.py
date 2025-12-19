import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.billing_state import (
    BillingState,
    CoinPackDisplay,
    TierDisplay,
    InvoiceDisplay,
)
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def billing_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    billing_page_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def billing_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Billing & Wallet",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Manage your subscription, coins, and view invoices.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.cond(
                BillingState.payment_status_message != "",
                rx.el.div(
                    BillingState.payment_status_message,
                    class_name="mb-6 p-4 rounded-lg bg-blue-500/20 border border-blue-500 text-blue-200",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Current Plan",
                            class_name="text-xl font-semibold text-[#E8F0FF]",
                        ),
                        rx.el.p(
                            BillingState.subscription_plan,
                            class_name="text-3xl font-bold text-[#D8B76E] mt-2",
                        ),
                        rx.el.p(
                            f"Renews on: {BillingState.renewal_date}",
                            class_name="text-[#A9B3C1]",
                        ),
                    ),
                    rx.cond(
                        BillingState.subscription_plan == "Free",
                        rx.el.div(
                            rx.el.h3(
                                "Upgrade Plan",
                                class_name="text-lg font-semibold mt-6 mb-4",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    BillingState.subscription_tiers, render_tier_card
                                ),
                                class_name="space-y-4",
                            ),
                        ),
                        rx.el.button(
                            "Manage Subscription",
                            on_click=BillingState.manage_subscription,
                            class_name="mt-6 w-full py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors",
                        ),
                    ),
                    **card_style("gold"),
                ),
                rx.el.div(
                    rx.el.h2(
                        "Wallet Balance",
                        class_name="text-xl font-semibold text-[#E8F0FF]",
                    ),
                    rx.el.p(
                        BillingState.wallet_balance,
                        class_name="text-3xl font-bold text-[#00E5FF] mt-2",
                    ),
                    rx.el.p("coins available", class_name="text-[#A9B3C1] mb-6"),
                    rx.el.h3("Purchase Coins", class_name="text-lg font-semibold mb-4"),
                    rx.el.div(
                        rx.foreach(BillingState.coin_packs, render_coin_pack),
                        class_name="grid grid-cols-2 gap-4",
                    ),
                    **card_style("cyan"),
                ),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-6",
            ),
            rx.el.div(
                rx.el.h2(
                    "Invoice History",
                    class_name="text-xl font-semibold text-[#E8F0FF] mb-4",
                ),
                rx.el.div(
                    rx.el.table(
                        rx.el.thead(
                            rx.el.tr(
                                rx.el.th(
                                    "Date",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Amount",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Status",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                                ),
                                rx.el.th(
                                    "Invoice",
                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider",
                                ),
                            )
                        ),
                        rx.el.tbody(
                            rx.foreach(BillingState.invoices, render_invoice_row),
                            class_name="divide-y divide-gray-700",
                        ),
                        class_name="min-w-full divide-y divide-gray-700",
                    ),
                    class_name="overflow-hidden rounded-lg border border-white/10",
                ),
                class_name=f"mt-8 {card_style('magenta')['class_name']}",
                style=card_style("magenta")["style"],
            ),
            class_name="p-8 max-w-7xl mx-auto",
        ),
        class_name=page_content_style,
    )


def render_tier_card(tier: TierDisplay) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h4(tier.name, class_name="font-bold text-lg"),
            rx.el.span("€", tier.price, "/mo", class_name="text-[#D8B76E]"),
            class_name="flex justify-between items-center",
        ),
        rx.el.button(
            "Upgrade",
            on_click=BillingState.subscribe(tier.name, tier.price),
            class_name="mt-2 w-full py-1 text-sm bg-[#D8B76E] text-[#0A0F14] font-bold rounded hover:opacity-90",
        ),
        class_name="p-3 rounded-lg bg-[#0A0F14] border border-white/10",
    )


def render_coin_pack(pack: CoinPackDisplay) -> rx.Component:
    return rx.el.button(
        rx.el.div(pack.coins, " Coins", class_name="font-bold text-[#00E5FF]"),
        rx.el.div("€", pack.price, class_name="text-sm text-[#A9B3C1]"),
        on_click=BillingState.buy_coins(pack.coins, pack.price),
        class_name="flex flex-col items-center justify-center p-3 rounded-lg bg-[#0A0F14] border border-white/10 hover:border-[#00E5FF] transition-colors",
    )


def render_invoice_row(inv: InvoiceDisplay) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            inv.date, class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]"
        ),
        rx.el.td(
            inv.amount, class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]"
        ),
        rx.el.td(
            rx.el.span(
                inv.status,
                class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-900/50 text-green-200",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.cond(
                inv.pdf_url != "",
                rx.el.a(
                    rx.icon("download", size=16),
                    " PDF",
                    href=inv.pdf_url,
                    target="_blank",
                    class_name="text-[#00E5FF] hover:underline flex items-center gap-1",
                ),
                rx.el.span("Processing", class_name="text-[#A9B3C1] italic"),
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm",
        ),
    )