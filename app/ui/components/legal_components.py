import reflex as rx
from app.ui.states.legal_state import LegalState, Subprocessor, RetentionItem, TocItem
from app.ui.styles import card_style


def legal_disclaimer_banner() -> rx.Component:
    return rx.el.div(
        rx.icon("gavel", class_name="mr-3 flex-shrink-0", size=24),
        rx.el.p(
            "This template is provided for convenience and does not constitute legal advice. Please consult with a legal professional.",
            class_name="text-sm",
        ),
        class_name="flex items-center p-4 mb-8 bg-yellow-900/50 text-accent-yellow border border-accent-yellow/30 rounded-lg",
    )


def legal_page_layout(
    title: rx.Var[str],
    last_updated: rx.Var[str],
    toc_items: rx.Var[list[TocItem]],
    pdf_name: str,
    children: list[rx.Component],
) -> rx.Component:
    return rx.el.div(
        cookie_consent_components(),
        rx.el.div(
            rx.el.main(
                rx.el.div(
                    rx.el.h1(
                        title, class_name="text-4xl font-bold text-text-primary mb-2"
                    ),
                    rx.el.p(
                        f"Last Updated: {last_updated}",
                        class_name="text-sm text-text-secondary",
                    ),
                    rx.el.button(
                        rx.icon("download", class_name="mr-2", size=16),
                        "Download PDF",
                        on_click=LegalState.generate_pdf(pdf_name),
                        class_name="mt-4 flex items-center px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
                    ),
                    class_name="mb-8 pb-8 border-b border-white/10",
                ),
                legal_disclaimer_banner(),
                rx.el.div(
                    rx.el.aside(
                        rx.el.h3(
                            "Table of Contents",
                            class_name="font-semibold text-text-primary mb-4",
                        ),
                        rx.el.ul(
                            rx.foreach(
                                toc_items,
                                lambda item: rx.el.li(
                                    rx.el.a(
                                        item["title"],
                                        href=f"#{item['id']}",
                                        class_name="hover:text-accent-cyan",
                                    )
                                ),
                            ),
                            class_name="space-y-2",
                        ),
                        class_name="sticky top-24 p-6 rounded-lg bg-bg-elevated border border-white/10 w-64 hidden lg:block",
                    ),
                    rx.el.div(
                        *children,
                        class_name="flex-1 space-y-8 prose prose-invert max-w-none text-text-secondary leading-relaxed",
                    ),
                    class_name="flex flex-col lg:flex-row gap-12",
                ),
                class_name="max-w-7xl mx-auto p-8",
            ),
            class_name="colabe-bg min-h-screen font-['Inter'] text-text-primary",
        ),
        on_mount=LegalState.on_load_legal,
    )


def legal_section(
    id: str, title: rx.Var[str], content: list[rx.Component]
) -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            title, class_name="text-2xl font-semibold text-text-primary mt-8 mb-4"
        ),
        *content,
        id=id,
        class_name="space-y-4 scroll-mt-24",
    )


def subprocessor_table() -> rx.Component:
    return rx.el.div(
        rx.el.p(f"Last updated: {LegalState.subprocessors_last_updated}"),
        rx.el.table(
            rx.el.thead(
                rx.el.tr(
                    rx.el.th("Name"),
                    rx.el.th("Purpose"),
                    rx.el.th("Region"),
                    rx.el.th("DPA"),
                )
            ),
            rx.el.tbody(rx.foreach(LegalState.subprocessors, subprocessor_row)),
            class_name="w-full text-left border-collapse",
        ),
        class_name="overflow-x-auto",
    )


def subprocessor_row(item: Subprocessor) -> rx.Component:
    return rx.el.tr(
        rx.el.td(item["name"]),
        rx.el.td(item["purpose"]),
        rx.el.td(item["region"]),
        rx.el.td(
            rx.el.a(
                "View",
                href=item["dpa_url"],
                target="_blank",
                rel="noopener",
                class_name="text-accent-cyan hover:underline",
            )
        ),
        class_name="border-b border-white/10",
    )


def retention_table() -> rx.Component:
    return rx.el.div(
        rx.el.table(
            rx.el.thead(rx.el.tr(rx.el.th("Data Type"), rx.el.th("Retention Period"))),
            rx.el.tbody(rx.foreach(LegalState.retention_schedule, retention_row)),
            class_name="w-full text-left border-collapse",
        ),
        class_name="overflow-x-auto",
    )


def retention_row(item: RetentionItem) -> rx.Component:
    return rx.el.tr(
        rx.el.td(item["data_type"]),
        rx.el.td(item["period"]),
        class_name="border-b border-white/10",
    )


def cookie_consent_components() -> rx.Component:
    return rx.fragment(
        rx.cond(
            LegalState.show_consent_banner & ~LegalState.consent_given, cookie_banner()
        ),
        rx.cond(LegalState.show_preferences_modal, cookie_preferences_modal()),
    )


def cookie_banner() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(
                "We use cookies to enhance your experience. By continuing to visit this site you agree to our use of cookies.",
                class_name="text-text-secondary text-sm",
            ),
            rx.el.div(
                rx.el.button(
                    "Manage",
                    on_click=LegalState.show_cookie_preferences,
                    class_name="px-4 py-2 rounded-lg bg-bg-base text-text-primary font-semibold hover:bg-white/10",
                ),
                rx.el.button(
                    "Reject Non-Essential",
                    on_click=LegalState.reject_non_essential_cookies,
                    class_name="px-4 py-2 rounded-lg bg-danger/80 text-text-primary font-semibold hover:bg-danger",
                ),
                rx.el.button(
                    "Accept All",
                    on_click=LegalState.accept_all_cookies,
                    class_name="px-4 py-2 rounded-lg bg-accent-cyan text-bg-base font-semibold hover:opacity-90",
                ),
                class_name="flex items-center space-x-3 mt-4 sm:mt-0",
            ),
            class_name="container mx-auto flex flex-col sm:flex-row items-center justify-between",
        ),
        class_name="fixed bottom-0 left-0 right-0 p-4 bg-bg-elevated border-t border-white/10 z-50 shadow-lg",
    )


def cookie_preferences_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title("Cookie Preferences"),
            rx.radix.primitives.dialog.description(
                "Manage your cookie settings. You can enable or disable different categories of cookies below."
            ),
            rx.el.div(
                cookie_toggle(
                    "Strictly Necessary",
                    "These cookies are essential for the site to function and cannot be disabled.",
                    "necessary",
                    is_disabled=True,
                ),
                cookie_toggle(
                    "Functional",
                    "These cookies allow the site to remember your choices and provide enhanced features.",
                    "functional",
                ),
                cookie_toggle(
                    "Analytics",
                    "These cookies help us understand how visitors interact with the website.",
                    "analytics",
                ),
                cookie_toggle(
                    "Marketing",
                    "These cookies are used to track visitors across websites to display relevant ads.",
                    "marketing",
                ),
                class_name="space-y-4 my-6",
            ),
            rx.el.div(
                rx.el.button(
                    "Cancel",
                    on_click=LegalState.hide_cookie_preferences,
                    class_name="px-4 py-2 rounded-lg bg-bg-base text-text-primary font-semibold hover:bg-white/10",
                ),
                rx.el.button(
                    "Save Preferences",
                    on_click=LegalState.save_consent,
                    class_name="px-4 py-2 rounded-lg bg-accent-cyan text-bg-base font-semibold hover:opacity-90",
                ),
                class_name="flex justify-end space-x-4",
            ),
            style=card_style("cyan"),
            class_name="bg-bg-elevated p-6 rounded-xl",
        ),
        open=LegalState.show_preferences_modal,
        on_open_change=LegalState.hide_cookie_preferences,
    )


def cookie_toggle(
    title: str, description: str, category: str, is_disabled: bool = False
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(title, class_name="font-semibold text-text-primary"),
            rx.el.p(description, class_name="text-sm text-text-secondary"),
            class_name="flex-grow",
        ),
        rx.el.button(
            rx.el.span(
                class_name=rx.cond(
                    LegalState.consent_preferences[category],
                    "translate-x-5",
                    "translate-x-0",
                )
                + " inline-block h-5 w-5 rounded-full bg-white transform ring-0 transition ease-in-out duration-200"
            ),
            class_name=rx.cond(
                LegalState.consent_preferences[category],
                "bg-accent-cyan",
                "bg-gray-500",
            )
            + " relative inline-flex flex-shrink-0 h-6 w-11 border-2 border-transparent rounded-full cursor-pointer transition-colors ease-in-out duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-accent-cyan disabled:opacity-50",
            on_click=lambda: LegalState.update_consent(
                category, ~LegalState.consent_preferences[category]
            ),
            disabled=is_disabled,
        ),
        class_name="flex items-center justify-between p-4 bg-bg-base rounded-lg",
    )