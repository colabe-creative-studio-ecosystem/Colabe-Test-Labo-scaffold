import reflex as rx
from app.ui.states.help_state import HelpState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style
from app.ui.components.help_copilot import help_copilot_shell


def ai_help_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "AI Support Copilot",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Your intelligent assistant for navigating Colabe Test Labo.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "What is the AI Copilot?",
                    class_name="text-xl font-semibold mb-4 text-text-primary",
                ),
                rx.el.p(
                    "The AI Copilot is a context-aware assistant designed to help you get the most out of Colabe Test Labo. You can access it anytime by clicking the 'Help' beacon at the bottom-right of your screen, or by pressing Shift + ?.",
                    class_name="text-text-secondary",
                ),
                class_name="p-6 bg-bg-elevated rounded-lg border border-white/10",
            ),
            rx.el.div(
                rx.el.h2(
                    "How to use it",
                    class_name="text-xl font-semibold mb-4 text-text-primary",
                ),
                rx.el.ul(
                    rx.el.li(
                        "Explain: Get detailed explanations about the current page or feature.",
                        class_name="mb-2",
                    ),
                    rx.el.li(
                        "Steps: Find step-by-step guides for common tasks.",
                        class_name="mb-2",
                    ),
                    rx.el.li(
                        "Recipes: Discover quick actions and pre-configured settings.",
                        class_name="mb-2",
                    ),
                    rx.el.li(
                        "Search: Look up any topic in our knowledge base.",
                        class_name="mb-2",
                    ),
                    rx.el.li(
                        "FAQ: Get answers to frequently asked questions.",
                        class_name="mb-2",
                    ),
                    class_name="list-disc list-inside text-text-secondary",
                ),
                class_name="p-6 bg-bg-elevated rounded-lg border border-white/10",
            ),
            class_name="p-8 space-y-6",
        ),
        class_name=page_content_style,
    )


def ai_help_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            HelpState.is_logged_in,
            rx.el.div(
                sidebar(),
                ai_help_page_content(),
                help_copilot_shell(),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=HelpState.check_login,
    )