import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.pages.index import landing_header, footer
from app.ui.components.legal_components import legal_disclaimer_banner


def security_page() -> rx.Component:
    return rx.el.div(
        landing_header(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(
                    "Security & Compliance",
                    class_name="text-4xl md:text-5xl font-bold tracking-tighter title-gradient",
                ),
                rx.el.p(
                    "Our commitment to protecting your data.",
                    class_name="mt-4 text-lg md:text-xl text-text-secondary max-w-2xl text-center",
                ),
                class_name="py-16 text-center",
            ),
            rx.el.div(
                security_overview_section(
                    "Data Residency",
                    "All customer data is processed and stored within the European Union by default. Enterprise customers can pin data to specific geographic regions.",
                    "map-pin",
                ),
                security_overview_section(
                    "Encryption",
                    "Data is encrypted in transit using TLS 1.2+ and at rest using AES-256. We enforce strict key management policies.",
                    "lock",
                ),
                security_overview_section(
                    "Access Control",
                    "We implement strict Role-Based Access Control (RBAC) and Attribute-Based Access Control (ABAC) to ensure least-privilege access.",
                    "users",
                ),
                security_overview_section(
                    "Audits & Monitoring",
                    "All sensitive actions are recorded in immutable audit logs. We continuously monitor our infrastructure for threats and vulnerabilities.",
                    "shield-check",
                ),
                security_overview_section(
                    "SBOM & Vulnerability Management",
                    "We provide a Software Bill of Materials (SBOM) for our application and continuously scan our dependencies for vulnerabilities using OSV.",
                    "package-search",
                ),
                security_overview_section(
                    "Incident Response",
                    "We have a formal incident response plan. In case of a breach, we commit to notifying affected customers within defined timeframes.",
                    "siren",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto px-8",
            ),
            rx.el.div(
                rx.el.a(
                    "View Live System Status",
                    href="/health",
                    class_name="text-accent-cyan hover:underline",
                ),
                rx.el.a(
                    "Contact Security",
                    href=f"mailto:{LegalState.org_email}",
                    class_name="text-accent-cyan hover:underline",
                ),
                class_name="text-center mt-16 space-x-8",
            ),
            class_name="container mx-auto",
        ),
        footer(),
        class_name="colabe-bg min-h-screen text-text-primary font-['Inter']",
    )


def security_overview_section(title: str, text: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.icon(icon, size=24, class_name="text-accent-cyan"),
        rx.el.h3(title, class_name="text-xl font-semibold mt-4 text-text-primary"),
        rx.el.p(text, class_name="mt-2 text-text-secondary"),
        class_name="p-6 bg-bg-elevated rounded-lg border border-white/10",
    )