import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.quality_state import QualityState
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style, card_style


def quality_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    quality_page_content(),
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


def quality_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Quality & Coverage",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Composite quality score and per-file coverage heatmap.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.button(
                "Generate Report for Run 1",
                on_click=QualityState.generate_quality_report(1),
                class_name="mb-6 px-4 py-2 bg-[#00E5FF] text-[#0A0F14] font-semibold rounded-lg hover:opacity-90",
            ),
            rx.el.div(
                quality_score_card(),
                coverage_heatmap(),
                class_name="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8",
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )


def quality_score_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Composite Quality Score",
            class_name="text-xl font-semibold text-[#E8F0FF] mb-4",
        ),
        rx.cond(
            QualityState.quality_score,
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        QualityState.quality_score.composite_score.to_string(),
                        class_name="text-5xl font-bold text-[#00E5FF]",
                    ),
                    rx.el.p("out of 100", class_name="text-[#A9B3C1]"),
                    class_name="text-center",
                ),
                rx.el.div(
                    quality_score_item(
                        "Static Issues", QualityState.quality_score.static_issues_score
                    ),
                    quality_score_item(
                        "Test Pass Rate", QualityState.quality_score.test_pass_rate
                    ),
                    quality_score_item(
                        "Coverage Delta", QualityState.quality_score.coverage_delta
                    ),
                    quality_score_item(
                        "Performance", QualityState.quality_score.performance_score
                    ),
                    quality_score_item(
                        "Accessibility", QualityState.quality_score.accessibility_score
                    ),
                    quality_score_item(
                        "Security", QualityState.quality_score.security_score
                    ),
                    class_name="mt-6 grid grid-cols-2 gap-4 text-sm",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    "No quality data available for this run. Generate a report to see the score.",
                    class_name="text-[#A9B3C1]",
                ),
                class_name="flex items-center justify-center h-full",
            ),
        ),
        **card_style("cyan"),
    )


def quality_score_item(name: str, score: rx.Var[float]) -> rx.Component:
    return rx.el.div(
        rx.el.p(name, class_name="text-[#A9B3C1]"),
        rx.el.p(score.to_string(), class_name="font-semibold text-[#E8F0FF]"),
        class_name="flex justify-between",
    )


def coverage_heatmap() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Coverage Heatmap", class_name="text-xl font-semibold text-[#E8F0FF] mb-4"
        ),
        rx.cond(
            QualityState.coverage_data.length() > 0,
            rx.plotly(data=QualityState.coverage_heatmap_fig),
            rx.el.div(
                rx.el.p(
                    "No coverage data available for this run. Generate a report to see the heatmap.",
                    class_name="text-[#A9B3C1]",
                ),
                class_name="flex items-center justify-center h-full",
            ),
        ),
        **card_style("magenta"),
    )