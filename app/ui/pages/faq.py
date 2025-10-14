import reflex as rx
from app.ui.states.kb_state import KBState, FaqItem
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style


def faq_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            KBState.is_logged_in,
            rx.el.div(sidebar(), faq_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
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
            rx.foreach(KBState.faq_items, faq_item),
            class_name="p-8 space-y-4 max-w-4xl mx-auto",
        ),
        class_name=page_content_style,
    )


def faq_item(item: FaqItem) -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            rx.el.h3(item["question"], class_name="font-semibold text-text-primary"),
            rx.icon("chevron-down", class_name="ml-auto group-open:rotate-180"),
            class_name="flex items-center cursor-pointer p-4 bg-bg-elevated rounded-lg group",
        ),
        rx.el.div(
            rx.el.p(item["answer"], class_name="text-text-secondary"),
            class_name="p-4 bg-bg-base rounded-b-lg",
        ),
        class_name="border border-white/10 rounded-lg",
    )