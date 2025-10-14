import reflex as rx
from app.ui.states.billing_state import BillingState, Plan, CoinPack, Invoice
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style
import plotly.graph_objects as go


def billing_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            BillingState.is_logged_in,
            rx.el.div(
                sidebar(),
                billing_page_content(),
                paywall_modal(),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=BillingState.load_billing_page,
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
            balances_section(),
            usage_section(),
            buy_coins_section(),
            subscriptions_section(),
            invoices_section(),
            billing_settings_section(),
            class_name="p-8 space-y-8",
        ),
        class_name=page_content_style,
    )


def balances_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Current Plan", class_name="text-xl font-semibold text-text-primary"
            ),
            rx.el.p(
                BillingState.current_plan["name"],
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
                "Wallet Balance", class_name="text-xl font-semibold text-text-primary"
            ),
            rx.el.p(
                BillingState.wallet_balance,
                class_name="text-3xl font-bold text-accent-cyan mt-2",
            ),
            rx.el.p("coins available", class_name="text-text-secondary"),
            **card_style("cyan"),
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
    )


def usage_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Usage", class_name="text-xl font-semibold text-text-primary mb-4"),
        rx.plotly(
            data=BillingState.usage_chart_fig,
            style={"height": "300px", "width": "100%"},
        ),
        **card_style("magenta"),
    )


def buy_coins_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Buy Coins", class_name="text-xl font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            rx.foreach(BillingState.coin_packs, coin_pack_card),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-4",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Promo Code",
                class_name="p-2 rounded bg-bg-base border border-white/10",
            ),
            rx.el.button(
                "Purchase Coins",
                on_click=BillingState.purchase_coins,
                is_disabled=~BillingState.is_admin_or_owner,
                class_name="px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90 disabled:opacity-50",
            ),
            class_name="mt-4 flex items-center justify-between",
        ),
        **card_style("cyan"),
    )


def coin_pack_card(pack: CoinPack) -> rx.Component:
    is_selected = BillingState.selected_coin_pack_id == pack["id"]
    return rx.el.div(
        rx.el.p(pack["name"], class_name="font-bold text-lg"),
        rx.el.p(f"€{pack['price_eur']}", class_name="text-2xl font-bold"),
        on_click=lambda: BillingState.select_coin_pack(pack["id"]),
        class_name=rx.cond(
            is_selected,
            "p-4 text-center rounded-lg border-2 border-accent-cyan bg-accent-cyan/10 cursor-pointer",
            "p-4 text-center rounded-lg border border-white/10 bg-bg-base hover:bg-white/5 cursor-pointer",
        ),
    )


def subscriptions_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Subscriptions", class_name="text-xl font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            rx.foreach(BillingState.plans, plan_card),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6",
        ),
        **card_style("gold"),
    )


def plan_card(plan: Plan) -> rx.Component:
    is_current = BillingState.plan_id == plan["id"]
    return rx.el.div(
        rx.el.h3(plan["name"], class_name="text-2xl font-bold"),
        rx.el.p(
            rx.cond(
                plan["price_monthly"] == 0,
                "Free",
                rx.cond(
                    plan["price_monthly"] > 0,
                    f"€{plan['price_monthly']}/mo",
                    "Contact Us",
                ),
            ),
            class_name="text-3xl font-extrabold my-4",
        ),
        rx.el.ul(
            plan_feature("Coins", f"{plan['coins_per_month']}/mo"),
            plan_feature("Concurrency", plan["concurrency"]),
            plan_feature("Artifacts", f"{plan['artifacts_gb']} GB"),
            plan_feature("Retention", f"{plan['retention_days']} days"),
            plan_feature("Autofix Attempts", plan["autofix_attempts"]),
            class_name="space-y-2 text-left",
        ),
        rx.el.button(
            rx.cond(is_current, "Current Plan", "Upgrade"),
            on_click=lambda: BillingState.upgrade_plan(plan["id"]),
            is_disabled=is_current | ~BillingState.is_admin_or_owner,
            class_name="w-full mt-6 py-2 rounded-lg font-semibold disabled:opacity-50 "
            + rx.cond(
                is_current,
                "bg-bg-base text-text-secondary border border-white/20",
                "bg-accent-gold text-bg-base hover:opacity-90",
            ),
        ),
        class_name="p-6 text-center rounded-lg border border-white/10 bg-bg-base",
    )


def plan_feature(name: str, value: rx.Var) -> rx.Component:
    return rx.el.li(
        rx.icon("check", class_name="text-success mr-2"),
        rx.el.span(f"{name}: "),
        rx.el.span(value, class_name="font-semibold"),
        class_name="flex items-center",
    )


def invoices_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Invoices", class_name="text-xl font-semibold text-text-primary mb-4"),
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Date"),
                    rx.el.th("Status"),
                    rx.el.th("Amount"),
                    rx.el.th(""),
                )
            ),
            rx.el.tbody(rx.foreach(BillingState.invoices, invoice_row)),
            class_name="w-full text-left",
        ),
        **card_style("yellow"),
    )


def invoice_row(invoice: Invoice) -> rx.Component:
    return rx.el.tr(
        rx.el.td(invoice["date"]),
        rx.el.td(invoice["status"]),
        rx.el.td(f"€{invoice['amount']:.2f}"),
        rx.el.td(
            rx.el.a(
                rx.icon("download", class_name="mr-2"),
                "PDF",
                href=invoice["pdf_url"],
                class_name="flex items-center text-accent-cyan hover:underline",
            )
        ),
        class_name="border-b border-white/10",
    )


def billing_settings_section() -> rx.Component:
    input_class = "w-full p-2 bg-bg-base border border-white/10 rounded-lg"
    return rx.el.form(
        rx.el.h2("Settings", class_name="text-xl font-semibold text-text-primary mb-4"),
        rx.el.div(
            rx.el.label(
                rx.el.input(
                    type="checkbox",
                    name="auto_top_up_enabled",
                    default_checked=BillingState.billing_settings.auto_top_up_enabled,
                ),
                " Enable Auto Top-Up",
                class_name="flex items-center space-x-2",
            ),
            rx.el.div(
                rx.el.label("Top-up when balance falls below:"),
                rx.el.input(
                    name="auto_top_up_threshold",
                    type="number",
                    default_value=BillingState.billing_settings.auto_top_up_threshold,
                    class_name=input_class,
                ),
                class_name="mt-2",
            ),
            rx.el.div(
                rx.el.label("Top-up amount:"),
                rx.el.input(
                    name="auto_top_up_amount",
                    type="number",
                    default_value=BillingState.billing_settings.auto_top_up_amount,
                    class_name=input_class,
                ),
                class_name="mt-2",
            ),
            rx.el.div(
                rx.el.label("Billing Contact Email"),
                rx.el.input(
                    name="billing_email",
                    type="email",
                    default_value=BillingState.billing_settings.billing_email,
                    class_name=input_class,
                ),
                class_name="mt-4",
            ),
            rx.el.div(
                rx.el.label("VAT/Tax ID"),
                rx.el.input(
                    name="vat_id",
                    default_value=BillingState.billing_settings.vat_id,
                    class_name=input_class,
                ),
                class_name="mt-4",
            ),
            rx.el.button(
                "Save Settings",
                type="submit",
                is_disabled=~BillingState.is_admin_or_owner,
                class_name="mt-4 px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90 disabled:opacity-50",
            ),
            class_name="space-y-4",
        ),
        on_submit=BillingState.update_billing_settings,
        **card_style("cyan"),
    )


def paywall_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.cond(
            BillingState.show_paywall_modal,
            rx.radix.primitives.dialog.content(
                rx.radix.primitives.dialog.title(
                    rx.icon("flag_triangle_right", class_name="text-warning mr-2"),
                    "Action Required",
                ),
                rx.radix.primitives.dialog.description(
                    f"Reason: {BillingState.paywall_reason}",
                    rx.el.p(
                        f"Estimated cost for this run: {BillingState.estimated_cost} coins."
                    ),
                ),
                rx.cond(
                    BillingState.paywall_reason.contains("coins"),
                    rx.el.div(
                        rx.el.h3("Buy More Coins", class_name="font-bold mt-4"),
                        rx.el.div(
                            rx.foreach(BillingState.coin_packs, coin_pack_card),
                            class_name="grid grid-cols-3 gap-2 my-4",
                        ),
                        rx.el.button(
                            "Purchase & Continue",
                            on_click=BillingState.purchase_coins,
                            class_name="w-full bg-accent-cyan text-bg-base rounded p-2 font-semibold",
                        ),
                    ),
                    rx.el.div(
                        rx.el.h3("Upgrade Your Plan", class_name="font-bold mt-4"),
                        rx.el.p("Your current plan does not support this feature."),
                        rx.el.button(
                            "Upgrade to Pro",
                            on_click=lambda: BillingState.upgrade_plan("pro"),
                            class_name="w-full mt-4 bg-accent-gold text-bg-base rounded p-2 font-semibold",
                        ),
                    ),
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        "Cancel",
                        on_click=BillingState.close_paywall,
                        class_name="mt-4 text-text-secondary",
                    )
                ),
                class_name="bg-bg-elevated p-6 rounded-lg border border-white/10 shadow-lg text-text-primary",
            ),
        ),
        open=BillingState.show_paywall_modal,
        on_open_change=BillingState.close_paywall,
    )