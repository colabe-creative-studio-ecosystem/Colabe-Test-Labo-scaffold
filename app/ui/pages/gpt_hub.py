import reflex as rx
from app.ui.states.gpt_hub_state import GptHubState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def gpt_hub_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            GptHubState.is_logged_in,
            rx.el.div(sidebar(), gpt_hub_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=GptHubState.load_overview,
    )


def gpt_hub_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "GPT Hub",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "AI-powered summaries, PR reviews, and doc generation.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                overview_card(
                    "Latest Summaries",
                    GptHubState.latest_summaries.length().to_string(),
                    "summaries",
                    "file-text",
                    "cyan",
                ),
                overview_card(
                    "PRs Awaiting Review",
                    GptHubState.prs_awaiting_review.length().to_string(),
                    "pr-reviews",
                    "git-pull-request-arrow",
                    "magenta",
                ),
                overview_card(
                    "Doc Drafts",
                    GptHubState.doc_drafts.length().to_string(),
                    "docs",
                    "notebook-tabs",
                    "yellow",
                ),
                overview_card(
                    "Token/Coin Usage (30d)",
                    GptHubState.token_usage.to_string(),
                    "settings",
                    "coins",
                    "gold",
                ),
                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6",
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )


def overview_card(
    title: str, value: str, link_path: str, icon: str, accent_color: str
) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.h3(title, class_name="text-lg font-semibold text-text-primary"),
                rx.el.p(
                    value,
                    class_name=f"text-4xl font-bold mt-2 text-accent-{accent_color}",
                ),
                class_name="flex-grow",
            ),
            rx.icon(icon, size=24, class_name=f"text-accent-{accent_color} opacity-70"),
            class_name="flex justify-between items-start h-full",
        ),
        href=f"/gpt-hub/{link_path}",
        **card_style(accent_color),
    )