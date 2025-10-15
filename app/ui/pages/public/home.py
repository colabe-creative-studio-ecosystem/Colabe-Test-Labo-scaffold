import reflex as rx
from .layout import public_page_layout


def home_page() -> rx.Component:
    return public_page_layout(
        rx.el.div(
            rx.el.h1(
                "Colabe Test Labo",
                class_name="text-6xl font-bold text-gray-900 title-gradient",
            ),
            rx.el.p(
                "The next-generation, cross-stack test automation platform.",
                class_name="mt-4 text-xl text-gray-600",
            ),
            rx.el.div(
                rx.el.a(
                    "Start Free Trial",
                    href="/register",
                    class_name="px-8 py-3 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600",
                ),
                rx.el.a(
                    "Schedule a Demo",
                    href="/demos",
                    class_name="px-8 py-3 bg-gray-200 text-gray-800 font-semibold rounded-lg hover:bg-gray-300",
                ),
                class_name="mt-8 flex gap-4",
            ),
            class_name="container mx-auto px-4 py-32 text-center",
        )
    )