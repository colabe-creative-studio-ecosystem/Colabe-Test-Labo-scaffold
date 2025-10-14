import reflex as rx
from app.ui.states.ops_dashboard_state import OpsDashboardState, HpaStatus
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def ops_dashboard_page() -> rx.Component:
    return rx.el.div(
        rx.el.div(sidebar(), ops_dashboard_content(), class_name=page_style),
        class_name="font-['Inter']",
        on_mount=OpsDashboardState.load_ops_data,
    )


def ops_dashboard_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Operations Dashboard",
                    class_name="text-2xl font-bold title-gradient",
                ),
                rx.el.p(
                    "Live metrics and status for production systems.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            deployment_info_card(),
            hpa_status_card(),
            pod_health_card(),
            monitoring_card(),
            backup_dr_card(),
            security_ops_card(),
            class_name="p-8 grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6",
        ),
        class_name=page_content_style,
    )


def info_row(label: str, value: rx.Var[str]) -> rx.Component:
    return rx.el.div(
        rx.el.span(label, class_name="text-text-secondary"),
        rx.el.span(value, class_name="font-mono text-sm"),
        class_name="flex justify-between items-center",
    )


def deployment_info_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Deployment", class_name="text-xl font-semibold mb-4"),
        info_row("Build SHA", OpsDashboardState.build_info["sha"]),
        info_row(
            "Signatures Verified", OpsDashboardState.build_info["signatures_verified"]
        ),
        info_row("Helm Release", OpsDashboardState.helm_info["release_version"]),
        info_row("Helm Values Hash", OpsDashboardState.helm_info["values_hash"]),
        **card_style("cyan"),
    )


def hpa_status_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("HPA Status", class_name="text-xl font-semibold mb-4"),
        rx.foreach(OpsDashboardState.hpa_status, render_hpa_row),
        **card_style("magenta"),
    )


def render_hpa_row(hpa: HpaStatus) -> rx.Component:
    return rx.el.div(
        rx.el.span(hpa.name, class_name="text-text-secondary"),
        rx.el.span(hpa.state, class_name="font-semibold text-accent-cyan"),
        class_name="flex justify-between items-center",
    )


def pod_health_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Pod Health", class_name="text-xl font-semibold mb-4"),
        info_row("Running", OpsDashboardState.pod_health["running"].to_string()),
        info_row("Pending", OpsDashboardState.pod_health["pending"].to_string()),
        info_row("Failed", OpsDashboardState.pod_health["failed"].to_string()),
        **card_style("gold"),
    )


def monitoring_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Monitoring", class_name="text-xl font-semibold mb-4"),
        info_row(
            "Error Budget Burn (30d)",
            f"{OpsDashboardState.error_budget_burn.to_string()}%",
        ),
        info_row("Synthetics Last Pass", OpsDashboardState.synthetics_last_pass),
        **card_style("blue"),
    )


def backup_dr_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Backups & DR", class_name="text-xl font-semibold mb-4"),
        info_row("Last Backup Check", OpsDashboardState.last_backup_check),
        info_row("Last DR Drill", OpsDashboardState.last_dr_drill),
        **card_style("success"),
    )


def security_ops_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Security Ops", class_name="text-xl font-semibold mb-4"),
        info_row(
            "WAF Rate Limits (1h)",
            OpsDashboardState.waf_counters["rate_limited_ips"].to_string(),
        ),
        info_row("Residency Enforcement", OpsDashboardState.residency_check),
        **card_style("warning"),
    )