import reflex as rx
from app.ui.states.kb_state import KBState, FaqItem
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style
from app.ui.components.kb_components import search_bar


def faq_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            KBState.is_logged_in,
            rx.el.div(sidebar(), faq_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=KBState.on_load_kb_content,
    )


def faq_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Frequently Asked Questions",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Find answers to common questions about Colabe Test Labo.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            search_bar(),
            rx.foreach(KBState.faq_categories, render_faq_category),
            class_name="p-8 max-w-4xl mx-auto",
        ),
        class_name=page_content_style,
    )


def render_faq_category(
    category_tuple: rx.Var[tuple[str, list[FaqItem]]],
) -> rx.Component:
    category_name = category_tuple[0]
    items = category_tuple[1]
    return rx.el.div(
        rx.el.h2(
            category_name,
            class_name="text-xl font-semibold text-text-primary mt-8 mb-4",
        ),
        rx.el.div(rx.foreach(items, faq_item), class_name="space-y-4"),
    )


def faq_item(item: FaqItem) -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            rx.el.h3(item["question"], class_name="font-semibold text-text-primary"),
            rx.icon(
                "chevron-down",
                class_name="ml-auto group-open:rotate-180 transition-transform",
            ),
            class_name="flex items-center cursor-pointer p-4 bg-bg-elevated rounded-lg group",
        ),
        rx.el.div(
            rx.el.div(
                class_name="prose prose-invert max-w-none text-text-secondary",
                dangerously_set_inner_html=item["answer_html"],
            ),
            class_name="p-4 bg-bg-base rounded-b-lg border-t border-white/10",
        ),
        class_name="border border-white/10 rounded-lg",
    )