import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.security_state import SecurityState
from app.ui.states.autofix_state import AutofixState
from app.ui.states.auth_state import AuthState
from app.core.models import SecurityFinding, SBOMComponent
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style
from app.ui.states.security_state import SBOMComponentDisplay


def security_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    security_page_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def security_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Security Dashboard",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Code, Secret, and Dependency Vulnerabilities",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    "Scan Now",
                    on_click=SecurityState.run_security_scans,
                    class_name="px-4 py-2 bg-[#FF3CF7] text-[#0A0F14] font-semibold rounded-lg hover:opacity-90",
                )
            ),
            rx.el.div(
                security_findings_table(),
                sbom_table(),
                class_name="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8",
            ),
            class_name="p-8 flex-1",
        ),
        class_name=page_content_style,
    )


def security_findings_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Security Findings", class_name="text-xl font-semibold text-[#E8F0FF] mb-4"
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Severity",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Description",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "OWASP",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "File",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Status",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Actions",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(SecurityState.security_findings, render_finding_row),
                    class_name="divide-y divide-white/10",
                ),
                class_name="min-w-full divide-y divide-white/10",
            ),
            class_name="overflow-hidden rounded-xl border border-white/10 bg-[#0E1520]",
        ),
    )


def render_finding_row(finding: SecurityFinding) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.span(
                finding.severity,
                class_name=rx.cond(
                    finding.severity == "HIGH",
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#FF3B3B]/20 text-[#FF3B3B]",
                    rx.cond(
                        finding.severity == "MEDIUM",
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#FFB020]/20 text-[#FFB020]",
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#A9B3C1]/20 text-[#A9B3C1]",
                    ),
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            finding.description,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]",
        ),
        rx.el.td(
            finding.owasp_category,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]",
        ),
        rx.el.td(
            finding.file_path + ":" + finding.line_number.to_string(),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#00E5FF] font-mono",
        ),
        rx.el.td(
            finding.status,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]",
        ),
        rx.el.td(
            rx.el.button(
                "Fix",
                on_click=AutofixState.trigger_autofix(finding.id),
                class_name="px-3 py-1 text-xs font-bold text-[#0A0F14] bg-[#FF3CF7] rounded hover:opacity-90",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-sm",
        ),
    )


def sbom_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Software Bill of Materials (SBOM)",
            class_name="text-xl font-semibold text-[#E8F0FF] mb-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Component",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Version",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Vulnerabilities",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(SecurityState.sbom_components, render_sbom_row),
                    class_name="divide-y divide-white/10",
                ),
                class_name="min-w-full divide-y divide-white/10",
            ),
            class_name="overflow-hidden rounded-xl border border-white/10 bg-[#0E1520]",
        ),
    )


def render_sbom_row(component: SBOMComponentDisplay) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            component.name,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]",
        ),
        rx.el.td(
            component.version,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#00E5FF] font-mono",
        ),
        rx.el.td(
            component.vulnerabilities.length().to_string(),
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#FF3B3B] font-bold",
        ),
    )