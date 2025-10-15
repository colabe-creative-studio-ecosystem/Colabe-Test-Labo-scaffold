import reflex as rx
from .layout import public_page_layout


def contact_page() -> rx.Component:
    return public_page_layout(
        rx.el.div(
            rx.el.h1("Contact Us", class_name="text-4xl font-bold text-gray-900"),
            rx.el.p(
                "Get in touch with our sales or support teams.",
                class_name="mt-4 text-lg text-gray-600",
            ),
            class_name="container mx-auto px-4 py-16 text-center",
        )
    )