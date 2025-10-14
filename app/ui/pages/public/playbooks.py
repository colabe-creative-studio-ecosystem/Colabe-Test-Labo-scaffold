import reflex as rx
from .layout import public_page_layout
from app.ui.states.programmatic_page_state import ProgrammaticPageState


def playbooks_page() -> rx.Component:
    return public_page_layout(
        rx.el.div(
            rx.el.h1(
                "Playbook: ",
                rx.el.span(
                    ProgrammaticPageState.current_item_title, class_name="capitalize"
                ),
                class_name="text-4xl font-bold text-gray-900",
            ),
            rx.el.p(
                ProgrammaticPageState.current_item_content,
                class_name="mt-4 text-lg text-gray-600",
            ),
            class_name="container mx-auto px-4 py-16",
        )
    )