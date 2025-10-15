import reflex as rx
import sqlmodel
from app.ui.states.security_state import SecurityState
from app.ui.states.autofix_state import AutofixState
from app.core.models import SecurityFinding, SBOMComponent
from app.ui.pages.index import sidebar, user_dropdown


def security_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            SecurityState.is_logged_in,
            rx.el.div(
                sidebar(),
                security_page_content(),
                class_name="flex min-h-screen bg-gray-50 font-['Inter']",
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen",
            ),
        )
    )


def security_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Security Dashboard", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Code, Secret, and Dependency Vulnerabilities",
                    class_name="text-gray-500",
                ),
            ),
            user_dropdown(),
            class_name="flex items-center justify-between p-4 border-b bg-white",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button("Scan Now", on_click=SecurityState.run_security_scans)
            ),
            rx.el.div(
                security_findings_table(),
                sbom_table(),
                class_name="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8",
            ),
            class_name="p-8",
        ),
        class_name="flex-1 flex flex-col",
        on_mount=SecurityState.load_security_data,
    )


def security_findings_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Security Findings", class_name="text-xl font-semibold mb-4"),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Severity"),
                        rx.el.th("Description"),
                        rx.el.th("OWASP"),
                        rx.el.th("OWASP"),
                        rx.el.th("File"),
                        rx.el.th("Status"),
                        rx.el.th("Actions"),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(SecurityState.security_findings, render_finding_row)
                ),
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
        ),
    )


def render_finding_row(finding: SecurityFinding) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.span(
                finding.severity,
                class_name=rx.cond(
                    finding.severity == "HIGH",
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800",
                    rx.cond(
                        finding.severity == "MEDIUM",
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800",
                        "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800",
                    ),
                ),
            )
        ),
        rx.el.td(finding.description),
        rx.el.td(finding.owasp_category),
        rx.el.td(f"{finding.file_path}:{finding.line_number.to_string()}"),
        rx.el.td(finding.status),
        rx.el.td(
            rx.el.button(
                "Fix",
                on_click=lambda: AutofixState.trigger_autofix(finding.id),
                class_name="px-2 py-1 text-xs font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700",
                size="1",
            )
        ),
        class_name="text-sm text-gray-600",
    )


def sbom_table() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Software Bill of Materials (SBOM)", class_name="text-xl font-semibold mb-4"
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Component"),
                        rx.el.th("Version"),
                        rx.el.th("Vulnerabilities"),
                    )
                ),
                rx.el.tbody(rx.foreach(SecurityState.sbom_components, render_sbom_row)),
                class_name="min-w-full divide-y divide-gray-200",
            ),
            class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg",
        ),
    )


def render_sbom_row(component: SBOMComponent) -> rx.Component:
    return rx.el.tr(
        rx.el.td(component.name),
        rx.el.td(component.version),
        rx.el.td(component.vulnerabilities.length().to_string()),
        class_name="text-sm text-gray-600",
    )