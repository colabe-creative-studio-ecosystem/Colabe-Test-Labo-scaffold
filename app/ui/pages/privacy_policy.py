import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.pages.index import sidebar


def legal_page_layout(title: str, children: list[rx.Component]) -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.div(
                rx.el.h1(title, class_name="text-3xl font-bold text-text-primary mb-2"),
                rx.el.p(
                    f"Last Updated: {LegalState.last_updated}",
                    class_name="text-sm text-text-secondary",
                ),
                class_name="mb-8",
            ),
            *children,
            class_name="max-w-4xl mx-auto p-8 text-text-secondary leading-relaxed",
        ),
        class_name="flex min-h-screen colabe-bg font-['Inter'] text-text-primary",
    )


def legal_section(title: str, content: list[rx.Component]) -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            title, class_name="text-2xl font-semibold text-text-primary mt-8 mb-4"
        ),
        *content,
        class_name="space-y-4",
    )


def privacy_policy_page() -> rx.Component:
    return legal_page_layout(
        "Privacy Policy",
        [
            legal_section(
                "1. Data Controller",
                [
                    rx.el.p(
                        "The data controller responsible for your personal data is ",
                        rx.el.strong(LegalState.org_legal_name),
                        ", with VAT number ",
                        rx.el.strong(LegalState.org_vat),
                        ", located at ",
                        rx.el.strong(LegalState.org_address),
                        ". You can contact us at ",
                        rx.el.a(
                            LegalState.org_email,
                            href=f"mailto:{LegalState.org_email}",
                            class_name="text-accent-cyan hover:underline",
                        ),
                        ".",
                    )
                ],
            ),
            legal_section(
                "2. Data We Collect",
                [
                    rx.el.p(
                        "We collect information you provide directly to us, such as when you create an account, use our services, or communicate with us. This may include your name, email address, payment information, and any other information you choose to provide."
                    ),
                    rx.el.p(
                        "We also collect technical data automatically, such as IP address, browser type, and usage information about your interaction with our services."
                    ),
                ],
            ),
            legal_section(
                "3. Legal Basis for Processing",
                [
                    rx.el.p(
                        "We process your data based on several legal grounds, including your consent, the necessity to perform a contract with you, compliance with our legal obligations, and our legitimate interests in providing and improving our services."
                    )
                ],
            ),
            legal_section(
                "4. Data Processors and Transfers",
                [
                    rx.el.p(
                        "We may share your data with third-party service providers (processors) who perform services on our behalf, such as payment processing and hosting. We ensure they are compliant with data protection laws. Data is primarily stored and processed within the European Union."
                    )
                ],
            ),
            legal_section(
                "5. Data Retention",
                [
                    rx.el.p(
                        "We retain your personal data for as long as necessary to fulfill the purposes for which it was collected, including for the purposes of satisfying any legal, accounting, or reporting requirements."
                    )
                ],
            ),
            legal_section(
                "6. Your Rights",
                [
                    rx.el.p(
                        "You have the right to access, rectify, or erase your personal data, as well as the right to restrict and object to certain processing of your data. To exercise these rights, please contact us at ",
                        rx.el.a(
                            LegalState.dpo_email,
                            href=f"mailto:{LegalState.dpo_email}",
                            class_name="text-accent-cyan hover:underline",
                        ),
                        ".",
                    )
                ],
            ),
            legal_section(
                "7. Cookies",
                [
                    rx.el.p(
                        "We use cookies and similar technologies to provide and improve our services. You can control the use of cookies at the individual browser level."
                    )
                ],
            ),
            legal_section(
                "8. Security",
                [
                    rx.el.p(
                        "We implement appropriate technical and organizational measures to protect your personal data against accidental or unlawful destruction, loss, alteration, unauthorized disclosure, or access."
                    )
                ],
            ),
            legal_section(
                "9. Changes to this Policy",
                [
                    rx.el.p(
                        "We may update this privacy policy from time to time. We will notify you of any changes by posting the new privacy policy on this page."
                    )
                ],
            ),
        ],
    )