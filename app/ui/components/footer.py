import reflex as rx


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Product of Colabe Creative Studio, part of Colabe Ecosystem",
                        class_name="text-gray-500 font-medium",
                    ),
                    rx.el.p(
                        "© 2025 Colabe Solutions Limited. All rights reserved.",
                        class_name="text-gray-600 mt-1",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "AV rep Argentina 41, 08023 Barcelona",
                            class_name="text-gray-600",
                        ),
                        rx.el.a(
                            "Colabe@mail.com",
                            href="mailto:Colabe@mail.com",
                            class_name="text-accent-cyan hover:underline ml-4",
                        ),
                        class_name="flex flex-wrap items-center mt-2 gap-y-2",
                    ),
                ),
                rx.el.div(
                    rx.el.a(
                        "Terms and Conditions",
                        href="/terms",
                        class_name="text-gray-500 hover:text-text-primary transition-colors",
                    ),
                    rx.el.a(
                        "Privacy Policy",
                        href="/privacy",
                        class_name="text-gray-500 hover:text-text-primary transition-colors",
                    ),
                    class_name="flex space-x-6 mt-4 md:mt-0",
                ),
                class_name="flex flex-col md:flex-row justify-between items-center text-sm",
            ),
            class_name="max-w-7xl mx-auto px-6",
        ),
        class_name="w-full border-t border-white/10 py-8 bg-bg-elevated mt-auto",
    )