import reflex as rx
from app.ui.components.footer import footer
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.states.auth_state import AuthState
from app.ui.states.accessibility_state import (
    AccessibilityState,
    ViolationDisplay,
    AuditStats,
    WCAGBreakdown,
)
from app.ui.styles import page_style, page_content_style, header_style, card_style


def accessibility_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    accessibility_content(),
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


def accessibility_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Accessibility",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Automated WCAG compliance audits and violation reports.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.cond(
                        AccessibilityState.is_loading,
                        rx.el.span("Running Audit...", class_name="animate-pulse"),
                        "Run New Audit",
                    ),
                    on_click=AccessibilityState.run_audit,
                    disabled=AccessibilityState.is_loading,
                    class_name="px-4 py-2 bg-[#00E5FF] text-[#0A0F14] font-semibold rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-wait transition-all",
                ),
                class_name="mb-8 flex justify-end",
            ),
            rx.cond(
                AccessibilityState.has_data,
                rx.el.div(
                    summary_section(),
                    wcag_breakdown_section(),
                    violations_section(),
                    class_name="space-y-8",
                ),
                empty_state(),
            ),
            class_name="p-8 flex-1",
        ),
        class_name=page_content_style,
    )


def summary_section() -> rx.Component:
    return rx.el.div(
        summary_card(
            "Overall Score",
            AccessibilityState.audit_stats.overall_score.to_string(),
            "/ 100",
            "cyan",
        ),
        summary_card(
            "Compliance",
            AccessibilityState.audit_stats.compliance_percentage.to_string() + "%",
            "WCAG 2.1",
            "success",
        ),
        summary_card(
            "Total Violations",
            AccessibilityState.audit_stats.total_violations.to_string(),
            "Issues Found",
            "danger",
        ),
        summary_card(
            "Pages Audited",
            AccessibilityState.audit_stats.pages_audited.to_string(),
            "Pages Scanned",
            "gold",
        ),
        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
    )


def summary_card(
    title: str, value: str, subtitle: str, color_theme: str
) -> rx.Component:
    text_color = {
        "cyan": "text-[#00E5FF]",
        "success": "text-[#00D68F]",
        "danger": "text-[#FF3B3B]",
        "gold": "text-[#D8B76E]",
    }.get(color_theme, "text-[#E8F0FF]")
    return rx.el.div(
        rx.el.h3(title, class_name="text-sm font-medium text-[#A9B3C1] uppercase"),
        rx.el.div(
            rx.el.span(value, class_name=f"text-3xl font-bold {text_color}"),
            class_name="mt-2",
        ),
        rx.el.p(subtitle, class_name="text-xs text-[#A9B3C1] mt-1"),
        class_name="bg-[#0E1520] p-6 rounded-xl border border-white/10 shadow-lg",
    )


def wcag_breakdown_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "WCAG Violation Breakdown",
            class_name="text-xl font-semibold text-[#E8F0FF] mb-4",
        ),
        rx.el.div(
            wcag_level_bar(
                "Level A (Basic)",
                AccessibilityState.wcag_breakdown.level_a,
                "text-[#FF3B3B]",
                "bg-[#FF3B3B]",
            ),
            wcag_level_bar(
                "Level AA (Intermediate)",
                AccessibilityState.wcag_breakdown.level_aa,
                "text-[#FFB020]",
                "bg-[#FFB020]",
            ),
            wcag_level_bar(
                "Level AAA (Advanced)",
                AccessibilityState.wcag_breakdown.level_aaa,
                "text-[#00E5FF]",
                "bg-[#00E5FF]",
            ),
            class_name="grid grid-cols-1 md:grid-cols-3 gap-6",
        ),
        **card_style("cyan"),
    )


def wcag_level_bar(
    label: str, count: rx.Var[int], text_color: str, bg_color: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(label, class_name="text-sm font-medium text-[#E8F0FF]"),
            rx.el.span(count, class_name=f"text-lg font-bold {text_color}"),
            class_name="flex justify-between items-center mb-2",
        ),
        rx.el.div(
            rx.el.div(
                class_name=f"h-full rounded-full {bg_color}", style={"width": "100%"}
            ),
            class_name="w-full h-2 bg-[#0A0F14] rounded-full overflow-hidden",
        ),
        class_name="p-4 rounded-lg bg-[#0A0F14] border border-white/5",
    )


def violations_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h2(
                "Detailed Violations", class_name="text-xl font-semibold text-[#E8F0FF]"
            ),
            rx.el.div(
                filter_button("All"),
                filter_button("Critical"),
                filter_button("Serious"),
                filter_button("Moderate"),
                filter_button("Minor"),
                class_name="flex space-x-2",
            ),
            class_name="flex flex-col md:flex-row justify-between items-center mb-6 gap-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "Impact",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Rule ID",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Description",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Element",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "WCAG",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                        rx.el.th(
                            "Count",
                            class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                        ),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(
                        AccessibilityState.filtered_violations, render_violation_row
                    ),
                    class_name="divide-y divide-white/10",
                ),
                class_name="min-w-full divide-y divide-white/10",
            ),
            class_name="overflow-hidden rounded-xl border border-white/10 bg-[#0E1520]",
        ),
    )


def filter_button(label: str) -> rx.Component:
    return rx.el.button(
        label,
        on_click=lambda: AccessibilityState.set_filter_impact(label),
        class_name=rx.cond(
            AccessibilityState.filter_impact == label,
            "px-3 py-1 rounded-full text-sm font-medium bg-[#00E5FF] text-[#0A0F14]",
            "px-3 py-1 rounded-full text-sm font-medium bg-[#0A0F14] text-[#A9B3C1] hover:text-[#E8F0FF] border border-white/10",
        ),
    )


def render_violation_row(violation: ViolationDisplay) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            impact_badge(violation.impact), class_name="px-6 py-4 whitespace-nowrap"
        ),
        rx.el.td(
            violation.rule_id,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF] font-mono",
        ),
        rx.el.td(
            rx.el.div(
                violation.description,
                rx.el.a(
                    "Help",
                    href=violation.help_url,
                    target="_blank",
                    class_name="ml-2 text-[#00E5FF] hover:underline text-xs",
                ),
                class_name="text-sm text-[#A9B3C1]",
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.el.code(
                violation.element,
                class_name="px-2 py-1 bg-[#0A0F14] rounded text-xs text-[#E8F0FF] font-mono border border-white/10",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            violation.wcag_criterion,
            class_name="px-6 py-4 whitespace-nowrap text-sm text-[#A9B3C1]",
        ),
        rx.el.td(
            violation.count,
            class_name="px-6 py-4 whitespace-nowrap text-sm font-bold text-[#E8F0FF]",
        ),
    )


def impact_badge(impact: str) -> rx.Component:
    return rx.el.span(
        impact,
        class_name=rx.cond(
            impact == "critical",
            "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#FF3B3B]/20 text-[#FF3B3B] uppercase",
            rx.cond(
                impact == "serious",
                "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#FFB020]/20 text-[#FFB020] uppercase",
                rx.cond(
                    impact == "moderate",
                    "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#D8B76E]/20 text-[#D8B76E] uppercase",
                    "px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-[#00E5FF]/20 text-[#00E5FF] uppercase",
                ),
            ),
        ),
    )


def empty_state() -> rx.Component:
    return rx.el.div(
        rx.icon("accessibility", size=48, class_name="text-[#A9B3C1] opacity-50 mb-4"),
        rx.el.h3(
            "No Accessibility Data", class_name="text-xl font-semibold text-[#E8F0FF]"
        ),
        rx.el.p(
            "Run an audit to generate accessibility compliance reports.",
            class_name="text-[#A9B3C1] mt-2",
        ),
        class_name="flex flex-col items-center justify-center py-20 text-center rounded-2xl border-2 border-dashed border-white/10 bg-[#0E1520]/50",
    )