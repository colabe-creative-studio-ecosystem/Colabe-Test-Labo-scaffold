import reflex as rx
from app.ui.states.kb_state import KBState, Article, SearchResult
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style
from app.ui.components.kb_components import search_bar
from app.ui.components.help_copilot import help_copilot_shell


def kb_page_layout(
    title: rx.Var[str], subtitle: rx.Var[str], content: rx.Component
) -> rx.Component:
    return rx.el.div(
        rx.cond(
            KBState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.main(
                    rx.el.header(
                        rx.el.div(
                            rx.el.h1(
                                title,
                                class_name="text-2xl font-bold text-text-primary title-gradient",
                            ),
                            rx.el.p(subtitle, class_name="text-text-secondary"),
                        ),
                        class_name=header_style,
                    ),
                    content,
                    class_name=page_content_style,
                ),
                help_copilot_shell(),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=KBState.on_load_kb_content,
    )


def kb_hub_page() -> rx.Component:
    return kb_page_layout(
        rx.Var.create("Knowledge Base"),
        rx.Var.create(
            "Explore guides, articles, and resources to master Colabe Test Labo."
        ),
        rx.el.div(
            search_bar(),
            rx.el.div(
                rx.foreach(KBState.guide_categories.items(), render_guide_category),
                class_name="space-y-8",
            ),
            class_name="p-8 max-w-4xl mx-auto",
        ),
    )


def render_guide_category(
    category_tuple: rx.Var[tuple[str, list[Article]]],
) -> rx.Component:
    category_name = category_tuple[0]
    articles = category_tuple[1]
    return rx.el.div(
        rx.el.h2(
            category_name, class_name="text-xl font-semibold text-text-primary mb-4"
        ),
        rx.el.div(
            rx.foreach(articles, render_article_card),
            class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
        ),
    )


def render_article_card(article: Article) -> rx.Component:
    return rx.el.a(
        rx.el.h3(article["title"], class_name="font-semibold text-text-primary"),
        rx.el.p(article["summary"], class_name="text-sm text-text-secondary mt-1"),
        rx.el.div(
            rx.el.p(
                f"Updated: {article['updated_at']}",
                class_name="text-xs text-text-secondary",
            ),
            class_name="mt-4 pt-2 border-t border-white/10",
        ),
        href=f"/kb/guides/{article['slug']}",
        class_name="block p-4 bg-bg-elevated rounded-lg border border-white/10 hover:border-accent-cyan/50 hover:bg-white/5 transition-all",
    )


def kb_article_page() -> rx.Component:
    return kb_page_layout(
        rx.cond(KBState.current_article, KBState.current_article["title"], ""),
        rx.cond(KBState.current_article, KBState.current_article["summary"], ""),
        rx.cond(
            KBState.current_article,
            article_view(),
            rx.el.div(rx.el.p("Article not found."), class_name="p-8"),
        ),
    )


def article_view() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            class_name="prose prose-invert max-w-none text-text-secondary p-8",
            dangerously_set_inner_html=KBState.current_article["content_html"],
        )
    )


def kb_search_page() -> rx.Component:
    return kb_page_layout(
        rx.Var.create("Search Results"),
        rx.Var.create(f"Results for: '{KBState.search_query}'"),
        rx.el.div(
            search_bar(),
            rx.el.div(
                rx.foreach(KBState.search_results, render_search_result),
                class_name="space-y-4",
            ),
            class_name="p-8 max-w-4xl mx-auto",
        ),
    )


def render_search_result(result: SearchResult) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.p(
                result["type"],
                class_name="text-xs font-semibold uppercase text-accent-cyan",
            ),
            rx.el.h3(
                result["title"], class_name="font-semibold text-text-primary mt-1"
            ),
            rx.el.p(result["summary"], class_name="text-sm text-text-secondary mt-1"),
            class_name="flex-grow",
        ),
        href=result["route"],
        class_name="block p-4 bg-bg-elevated rounded-lg border border-white/10 hover:border-accent-cyan/50 hover:bg-white/5 transition-all",
    )


def kb_changelog_page() -> rx.Component:
    return kb_page_layout(
        rx.Var.create("Changelog"),
        rx.Var.create("Latest updates and features for Colabe Test Labo."),
        rx.el.div(
            rx.el.p("Changelog content coming soon."),
            class_name="p-8 max-w-4xl mx-auto text-text-secondary",
        ),
    )