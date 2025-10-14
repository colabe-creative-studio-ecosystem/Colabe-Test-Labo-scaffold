import reflex as rx
from .layout import public_page_layout
from app.ui.states.programmatic_page_state import ProgrammaticPageState


def adapters_page() -> rx.Component:
    return public_page_layout(
        rx.el.div(
            rx.el.h1(
                "Adapter: ",
                rx.el.span(
                    ProgrammaticPageState.current_item_title, class_name="capitalize"
                ),
                class_name="text-4xl font-bold text-gray-900",
            ),
            rx.el.p(
                ProgrammaticPageState.current_item_content,
                class_name="mt-4 text-lg text-gray-600",
            ),
            rx.el.div(
                rx.el.h2(
                    "Sample Command", class_name="text-2xl font-semibold mt-8 mb-4"
                ),
                rx.el.code(
                    ProgrammaticPageState.sample_command,
                    class_name="block bg-gray-800 text-white p-4 rounded-lg overflow-x-auto",
                ),
                class_name="mt-8",
            ),
            class_name="container mx-auto px-4 py-16",
        )
    )