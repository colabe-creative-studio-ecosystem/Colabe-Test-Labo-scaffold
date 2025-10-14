import reflex as rx
import plotly.graph_objects as go
from app.ui.states.quality_state import QualityState
from app.ui.pages.index import sidebar, user_dropdown


def quality_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            QualityState.is_logged_in,
            rx.el.div(
                sidebar(),
                quality_page_content(),
                class_name="flex min-h-screen bg-gray-50 font-['Inter']",
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen",
            ),
        )
    )


def quality_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Quality & Coverage", class_name="text-2xl font-bold text-gray-900"
                ),
                rx.el.p(
                    "Composite quality score and per-file coverage heatmap.",
                    class_name="text-gray-500",
                ),
            ),
            user_dropdown(),
            class_name="flex items-center justify-between p-4 border-b bg-white",
        ),
        rx.el.div(
            rx.el.button(
                "Generate Report for Run 1",
                on_click=lambda: QualityState.generate_quality_report(1),
                class_name="mb-6 px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600",
            ),
            rx.el.div(
                quality_score_card(),
                coverage_heatmap(),
                class_name="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-8",
            ),
            class_name="p-8",
        ),
        class_name="flex-1 flex flex-col",
        on_mount=lambda: QualityState.load_quality_data(1),
    )


def quality_score_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Composite Quality Score", class_name="text-xl font-semibold mb-4"),
        rx.cond(
            QualityState.quality_score,
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        QualityState.quality_score.composite_score.to_string(),
                        class_name="text-5xl font-bold text-blue-600",
                    ),
                    rx.el.p("out of 100", class_name="text-gray-500"),
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
                    class_name="text-gray-500",
                ),
                class_name="flex items-center justify-center h-full",
            ),
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def quality_score_item(name: str, score: rx.Var[float]) -> rx.Component:
    return rx.el.div(
        rx.el.p(name, class_name="text-gray-600"),
        rx.el.p(score.to_string(), class_name="font-semibold text-gray-800"),
        class_name="flex justify-between",
    )


def coverage_heatmap() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Coverage Heatmap", class_name="text-xl font-semibold mb-4"),
        rx.cond(
            QualityState.coverage_data.length() > 0,
            rx.plotly(data=QualityState.coverage_heatmap_fig),
            rx.el.div(
                rx.el.p(
                    "No coverage data available for this run. Generate a report to see the heatmap.",
                    class_name="text-gray-500",
                ),
                class_name="flex items-center justify-center h-full",
            ),
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )