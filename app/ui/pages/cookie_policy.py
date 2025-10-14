import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.components.legal_components import legal_page_layout, legal_section


def cookie_policy_page() -> rx.Component:
    return legal_page_layout(
        title=rx.Var.create("Cookie Policy"),
        last_updated=LegalState.last_updated,
        toc_items=LegalState.cookies_toc,
        pdf_name="cookie_policy.pdf",
        children=[
            legal_section(
                "s1",
                rx.Var.create("1. What Are Cookies?"),
                [
                    rx.el.p(
                        "Cookies are small text files stored on your device that help us operate and personalize our services. We use them to understand user activity, improve security, and serve relevant ads."
                    )
                ],
            ),
            legal_section(
                "s2",
                rx.Var.create("2. Cookie Categories"),
                [
                    rx.el.h3(
                        "Strictly Necessary",
                        class_name="font-semibold text-text-primary mt-4",
                    ),
                    rx.el.p(
                        "Essential for you to browse the website and use its features, such as accessing secure areas. These cookies cannot be disabled."
                    ),
                    rx.el.h3(
                        "Functional", class_name="font-semibold text-text-primary mt-4"
                    ),
                    rx.el.p(
                        "Used to remember choices you make, such as your language preference, to provide a more personalized experience."
                    ),
                    rx.el.h3(
                        "Analytics", class_name="font-semibold text-text-primary mt-4"
                    ),
                    rx.el.p(
                        "Help us understand how our services are being used, measure the effectiveness of marketing campaigns, and help us customize and improve our services for you."
                    ),
                    rx.el.h3(
                        "Marketing", class_name="font-semibold text-text-primary mt-4"
                    ),
                    rx.el.p(
                        "Used to make advertising messages more relevant to you. They perform functions like preventing the same ad from continuously reappearing and ensuring that ads are properly displayed."
                    ),
                ],
            ),
            legal_section(
                "s3",
                rx.Var.create("3. Your Choices"),
                [
                    rx.el.p(
                        "You can manage your cookie preferences at any time by clicking the 'Change cookie settings' link in the footer of our website. Please note that disabling certain cookies may impact the functionality of our services."
                    )
                ],
            ),
        ],
    )