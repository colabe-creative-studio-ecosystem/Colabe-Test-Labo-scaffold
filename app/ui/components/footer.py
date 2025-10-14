import reflex as rx


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "© 2024 Colabe Test Labo. All rights reserved.",
                    class_name="text-sm text-text-secondary",
                ),
                class_name="flex flex-col gap-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        "Product", class_name="text-sm font-semibold text-text-primary"
                    ),
                    rx.el.a(
                        "API Center",
                        href="/api-docs",
                        class_name="text-sm text-text-secondary hover:text-accent-cyan",
                    ),
                    rx.el.a(
                        "Who We Are",
                        href="/about",
                        class_name="text-sm text-text-secondary hover:text-accent-cyan",
                    ),
                    class_name="flex flex-col gap-2",
                ),
                rx.el.div(
                    rx.el.h3(
                        "Legal", class_name="text-sm font-semibold text-text-primary"
                    ),
                    rx.el.a(
                        "Privacy Policy",
                        href="/legal/privacy",
                        class_name="text-sm text-text-secondary hover:text-accent-cyan",
                    ),
                    rx.el.a(
                        "Terms & Conditions",
                        href="/legal/terms",
                        class_name="text-sm text-text-secondary hover:text-accent-cyan",
                    ),
                    rx.el.a(
                        "Cookie Policy",
                        href="/legal/cookies",
                        class_name="text-sm text-text-secondary hover:text-accent-cyan",
                    ),
                    rx.el.a(
                        "Privacy Center",
                        href="/privacy-center",
                        class_name="text-sm text-text-secondary hover:text-accent-cyan",
                    ),
                    rx.el.a(
                        "Security",
                        href="/security",
                        class_name="text-sm text-text-secondary hover:text-accent-cyan",
                    ),
                    class_name="flex flex-col gap-2",
                ),
                class_name="flex flex-row gap-8",
            ),
            class_name="container mx-auto flex flex-col md:flex-row justify-between items-start md:items-center gap-8 text-text-primary",
        ),
        class_name="p-8 border-t border-white/10 bg-bg-elevated",
    )