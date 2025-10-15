import reflex as rx
from .layout import public_page_layout


def pricing_page() -> rx.Component:
    return public_page_layout(
        rx.el.div(
            rx.el.h1("Pricing", class_name="text-4xl font-bold text-gray-900"),
            rx.el.p(
                "Find the perfect plan for your team.",
                class_name="mt-4 text-lg text-gray-600",
            ),
            class_name="container mx-auto px-4 py-16 text-center",
        )
    )