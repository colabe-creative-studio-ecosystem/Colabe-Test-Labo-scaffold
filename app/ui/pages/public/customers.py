import reflex as rx
from .layout import public_page_layout


def customers_page() -> rx.Component:
    return public_page_layout(
        rx.el.div(
            rx.el.h1("Customer Stories", class_name="text-4xl font-bold text-gray-900"),
            rx.el.p(
                "See how leading companies use Colabe Test Labo.",
                class_name="mt-4 text-lg text-gray-600",
            ),
            class_name="container mx-auto px-4 py-16 text-center",
        )
    )


def customer_profile_page() -> rx.Component:
    return public_page_layout(
        rx.el.div(
            rx.el.h1("Customer Profile", class_name="text-4xl font-bold text-gray-900"),
            rx.el.p(
                "An in-depth look at a customer's success.",
                class_name="mt-4 text-lg text-gray-600",
            ),
            class_name="container mx-auto px-4 py-16 text-center",
        )
    )