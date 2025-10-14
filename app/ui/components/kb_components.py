import reflex as rx
from app.ui.states.kb_state import KBState


def search_bar() -> rx.Component:
    """A search bar component for the knowledge base."""
    return rx.el.div(
        rx.icon(
            "search",
            class_name="absolute left-4 top-1/2 -translate-y-1/2 text-text-secondary",
        ),
        rx.el.input(
            placeholder="Search articles, FAQs, settings...",
            default_value=KBState.search_query,
            on_change=KBState.set_search_query,
            class_name="w-full bg-bg-elevated rounded-lg border border-white/10 py-3 pl-12 pr-4 placeholder:text-text-secondary focus:outline-none focus:ring-2 focus:ring-accent-cyan",
        ),
        class_name="relative w-full mb-8",
    )