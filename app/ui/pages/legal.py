import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def legal_page_layout(page_content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.cond(
            LegalState.is_logged_in,
            rx.el.div(sidebar(), page_content, class_name=page_style),
            rx.el.div(
                public_navbar(),
                page_content,
                class_name="flex flex-col min-h-screen colabe-bg font-['Inter'] text-text-primary",
            ),
        )
    )


def public_navbar():
    return rx.el.nav(
        rx.el.div(
            rx.el.a(
                rx.icon("flask-conical", size=32, class_name="text-accent-cyan"),
                rx.text(
                    "Colabe Test Labo", class_name="text-xl font-bold text-text-primary"
                ),
                href="/",
                class_name="flex items-center space-x-2",
            ),
            rx.el.div(
                rx.el.a(
                    "Login",
                    href="/login",
                    class_name="text-text-secondary hover:text-text-primary",
                ),
                rx.el.a(
                    "Register",
                    href="/register",
                    class_name="ml-4 px-4 py-2 text-sm font-medium text-bg-base bg-accent-cyan rounded-lg hover:opacity-90",
                ),
                class_name="flex items-center",
            ),
            class_name="container mx-auto flex items-center justify-between",
        ),
        class_name="p-4 border-b border-white/10 bg-bg-elevated sticky top-0 z-50",
    )


def legal_doc_view(
    title: rx.Var[str], sections: rx.Var[list[dict]], disclaimer: rx.Var[str]
) -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    title,
                    class_name="text-3xl font-bold text-text-primary title-gradient",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("languages", size=16),
                        "English",
                        on_click=lambda: LegalState.set_lang("en"),
                        class_name=rx.cond(
                            LegalState.lang == "en",
                            "text-accent-cyan",
                            "text-text-secondary",
                        )
                        + " flex items-center gap-2",
                    ),
                    rx.el.span("|", class_name="text-text-secondary"),
                    rx.el.button(
                        rx.icon("languages", size=16),
                        "Español",
                        on_click=lambda: LegalState.set_lang("es"),
                        class_name=rx.cond(
                            LegalState.lang == "es",
                            "text-accent-cyan",
                            "text-text-secondary",
                        )
                        + " flex items-center gap-2",
                    ),
                    class_name="flex items-center gap-2",
                ),
            ),
            class_name=f"{header_style} flex-col md:flex-row items-start md:items-center gap-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("scale", size=16),
                        rx.el.p(disclaimer, class_name="text-sm text-text-secondary"),
                        class_name="flex items-center gap-2 p-4 rounded-lg bg-bg-base border border-accent-gold/20 mb-8",
                    ),
                    rx.foreach(sections, render_section),
                    rx.cond(title.contains("Privacy"), subprocessors_table()),
                    class_name="col-span-12 lg:col-span-9 space-y-8",
                ),
                rx.el.div(
                    rx.el.h3(
                        "On this page",
                        class_name="font-semibold text-text-primary mb-4",
                    ),
                    rx.el.ul(
                        rx.foreach(
                            sections,
                            lambda section: rx.el.li(
                                rx.el.a(
                                    section["title"],
                                    href=f"#{section['id']}",
                                    class_name="text-text-secondary hover:text-text-primary text-sm",
                                )
                            ),
                        ),
                        class_name="space-y-2 border-l border-white/10 pl-4",
                    ),
                    class_name="hidden lg:block lg:col-span-3 sticky top-24 h-fit",
                ),
                class_name="grid grid-cols-12 gap-8",
            ),
            class_name="p-8",
        ),
        class_name=page_content_style,
    )


def render_section(section: dict) -> rx.Component:
    return rx.el.section(
        rx.el.h2(
            section["title"],
            id=section["id"],
            class_name="text-2xl font-semibold text-text-primary title-gradient mb-4 scroll-mt-24",
        ),
        rx.el.p(section["content"], class_name="text-text-secondary leading-relaxed"),
        class_name="",
    )


def subprocessors_table() -> rx.Component:
    return rx.el.section(
        rx.el.h2(
            "Subprocessors",
            class_name="text-2xl font-semibold text-text-primary title-gradient mb-4",
        ),
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th("Name", class_name="p-4 text-left"),
                        rx.el.th("Purpose", class_name="p-4 text-left"),
                        rx.el.th("Region", class_name="p-4 text-left"),
                        rx.el.th("DPA", class_name="p-4 text-left"),
                    )
                ),
                rx.el.tbody(
                    rx.foreach(LegalState.subprocessors, render_subprocessor_row)
                ),
                class_name="w-full text-sm",
            ),
            class_name="overflow-x-auto rounded-lg border border-white/10",
        ),
    )


def render_subprocessor_row(sub: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(sub["name"], class_name="p-4 border-t border-white/10"),
        rx.el.td(sub["purpose"], class_name="p-4 border-t border-white/10"),
        rx.el.td(sub["region"], class_name="p-4 border-t border-white/10"),
        rx.el.td(
            rx.el.a(
                "Link",
                href=sub["dpa_url"],
                target="_blank",
                class_name="text-accent-cyan hover:underline",
            ),
            class_name="p-4 border-t border-white/10",
        ),
        class_name="bg-bg-elevated",
    )