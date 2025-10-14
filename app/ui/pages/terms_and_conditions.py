import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.pages.privacy_policy import legal_page_layout, legal_section


def terms_and_conditions_page() -> rx.Component:
    return legal_page_layout(
        "Terms and Conditions",
        [
            legal_section(
                "1. Service Description",
                [
                    rx.el.p(
                        "Colabe Test Labo provides a cloud-based platform for automated software testing, analysis, and quality assurance. Services are provided on an 'as is' and 'as available' basis."
                    )
                ],
            ),
            legal_section(
                "2. Accounts and Roles",
                [
                    rx.el.p(
                        "You are responsible for maintaining the security of your account and for all activities that occur under the account. You must be a human. Accounts registered by 'bots' or other automated methods are not permitted."
                    )
                ],
            ),
            legal_section(
                "3. Pricing and Payments",
                [
                    rx.el.p(
                        "Our services are billed on a subscription basis and/or through a pre-paid 'coins' system. By providing a payment method, you expressly authorize us to charge you for the services. All payments are non-refundable."
                    )
                ],
            ),
            legal_section(
                "4. Acceptable Use",
                [
                    rx.el.p(
                        "You may not use our service for any illegal or unauthorized purpose. You must not, in the use of the Service, violate any laws in your jurisdiction. Specifically, you may only scan, test, or analyze repositories and applications for which you have explicit ownership or authorization."
                    )
                ],
            ),
            legal_section(
                "5. Intellectual Property",
                [
                    rx.el.p(
                        "We claim no intellectual property rights over the material you provide to the Service. Your profile and materials uploaded remain yours. However, by setting your pages to be viewed publicly, you agree to allow others to view your content."
                    )
                ],
            ),
            legal_section(
                "6. Limitation of Liability",
                [
                    rx.el.p(
                        "In no event shall ",
                        rx.el.strong(LegalState.org_legal_name),
                        " be liable for any direct, indirect, incidental, special, consequential or exemplary damages, including but not limited to, damages for loss of profits, goodwill, use, data or other intangible losses.",
                    )
                ],
            ),
            legal_section(
                "7. Termination",
                [
                    rx.el.p(
                        "We reserve the right to suspend or terminate your account and refuse any and all current or future use of the Service for any reason at any time."
                    )
                ],
            ),
            legal_section(
                "8. Governing Law",
                [
                    rx.el.p(
                        "These Terms shall be governed by the laws of ",
                        rx.el.strong(LegalState.governing_law),
                        ", without regard to its conflict of law provisions. Any dispute arising from these Terms shall be resolved in the courts of ",
                        rx.el.strong(LegalState.venue),
                        ".",
                    )
                ],
            ),
        ],
    )