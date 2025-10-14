import reflex as rx
from app.ui.states.tenant_state import TenantState
from app.core.models import Tenant
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def admin_tenants_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            TenantState.is_admin,
            rx.el.div(sidebar(), tenants_content(), class_name=page_style),
            rx.el.div(
                "Access Denied. Admins only.",
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=TenantState.load_tenants,
    )


def tenants_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.h1(
                "Tenant Management", class_name="text-2xl font-bold title-gradient"
            ),
            class_name=header_style,
        ),
        rx.el.div(
            provision_tenant_card(),
            tenants_list_card(),
            class_name="p-8 grid grid-cols-1 lg:grid-cols-2 gap-8",
        ),
        class_name=page_content_style,
    )


def provision_tenant_card() -> rx.Component:
    return rx.el.form(
        rx.el.h2("Provision New Tenant", class_name="text-xl font-semibold mb-4"),
        rx.el.div(
            rx.el.label("Tenant Name", class_name="text-sm font-medium"),
            rx.el.input(
                name="tenant_name",
                placeholder="New Corp",
                class_name="w-full mt-1 p-2 rounded-lg bg-bg-base border border-white/20",
            ),
            rx.el.label("Owner Email", class_name="text-sm font-medium mt-4"),
            rx.el.input(
                name="owner_email",
                type="email",
                placeholder="owner@newcorp.com",
                class_name="w-full mt-1 p-2 rounded-lg bg-bg-base border border-white/20",
            ),
            rx.el.label("Plan", class_name="text-sm font-medium mt-4"),
            rx.el.select(
                ["Free", "Pro", "Enterprise"],
                name="plan",
                default_value="Free",
                class_name="w-full mt-1 p-2 rounded-lg bg-bg-base border border-white/20",
            ),
            class_name="space-y-2",
        ),
        rx.el.button(
            "Provision Tenant",
            type="submit",
            class_name="mt-6 w-full py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
        ),
        on_submit=TenantState.provision_tenant,
        reset_on_submit=True,
        **card_style("cyan"),
    )


def tenants_list_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("All Tenants", class_name="text-xl font-semibold mb-4"),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("ID", class_name="p-2 text-left"),
                        rx.el.th("Name", class_name="p-2 text-left"),
                        rx.el.th("Plan", class_name="p-2 text-left"),
                        rx.el.th("Status", class_name="p-2 text-left"),
                        rx.el.th("Actions", class_name="p-2 text-left"),
                    )
                ),
                rx.el.tbody(rx.foreach(TenantState.tenants, render_tenant_row)),
            ),
            class_name="w-full",
        ),
        **card_style("magenta"),
    )


def render_tenant_row(tenant: Tenant) -> rx.Component:
    return rx.el.tr(
        rx.el.td(tenant.id, class_name="p-2"),
        rx.el.td(tenant.name, class_name="p-2"),
        rx.el.td(tenant.plan, class_name="p-2"),
        rx.el.td(
            rx.el.span(
                tenant.status,
                class_name=rx.cond(
                    tenant.status == "active",
                    "px-2 py-1 text-xs font-semibold rounded-full bg-success/20 text-success",
                    "px-2 py-1 text-xs font-semibold rounded-full bg-danger/20 text-danger",
                ),
            ),
            class_name="p-2",
        ),
        rx.el.td(
            rx.el.div(
                rx.cond(
                    tenant.status == "active",
                    rx.el.button(
                        "Suspend",
                        on_click=lambda: TenantState.update_tenant_status(
                            tenant.id, "suspended"
                        ),
                        class_name="px-2 py-1 text-xs bg-warning text-bg-base rounded",
                    ),
                    rx.el.button(
                        "Resume",
                        on_click=lambda: TenantState.update_tenant_status(
                            tenant.id, "active"
                        ),
                        class_name="px-2 py-1 text-xs bg-success text-bg-base rounded",
                    ),
                ),
                rx.el.button(
                    "Close",
                    on_click=lambda: TenantState.update_tenant_status(
                        tenant.id, "closing"
                    ),
                    class_name="ml-2 px-2 py-1 text-xs bg-danger text-bg-base rounded",
                ),
                class_name="flex",
            ),
            class_name="p-2",
        ),
        class_name="border-t border-white/10",
    )