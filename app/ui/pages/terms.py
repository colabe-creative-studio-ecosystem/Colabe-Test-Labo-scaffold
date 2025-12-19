import reflex as rx
from app.ui.components.footer import footer
from app.ui.styles import page_style, header_style


def terms_content() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Terms and Conditions",
                    class_name="text-3xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Last updated: January 2025", class_name="text-text-secondary mt-2"
                ),
            ),
            class_name="container mx-auto px-6 py-8 border-b border-white/10",
        ),
        rx.el.div(
            rx.el.article(
                section_title("1. Introduction"),
                rx.el.p(
                    "Welcome to Colabe Test Labo. These Terms and Conditions govern your use of our website and services operated by Colabe Solutions Limited."
                ),
                section_title("2. Services"),
                rx.el.p(
                    "We provide a test automation and quality assurance platform. By accessing our services, you agree to comply with these terms."
                ),
                section_title("3. User Accounts"),
                rx.el.p(
                    "You are responsible for safeguarding the password that you use to access the service and for any activities or actions under your password."
                ),
                section_title("4. Payment Terms"),
                rx.el.p(
                    "Certain aspects of the service may be provided for a fee or other charge. If you elect to use paid aspects of the service, you agree to the pricing and payment terms."
                ),
                section_title("5. Intellectual Property"),
                rx.el.p(
                    "The service and its original content, features, and functionality are and will remain the exclusive property of Colabe Solutions Limited and its licensors."
                ),
                section_title("6. Limitation of Liability"),
                rx.el.p(
                    "In no event shall Colabe Solutions Limited, nor its directors, employees, partners, agents, suppliers, or affiliates, be liable for any indirect, incidental, special, consequential or punitive damages."
                ),
                section_title("7. Termination"),
                rx.el.p(
                    "We may terminate or suspend your account immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms."
                ),
                section_title("8. Governing Law"),
                rx.el.p(
                    "These Terms shall be governed and construed in accordance with the laws of Spain, without regard to its conflict of law provisions."
                ),
                section_title("9. Contact Information"),
                rx.el.p(
                    "If you have any questions about these Terms, please contact us at Colabe@mail.com."
                ),
                class_name="prose prose-invert max-w-none space-y-6 text-gray-300",
            ),
            class_name="container mx-auto px-6 py-12 flex-1",
        ),
        class_name="flex flex-col min-h-screen colabe-bg",
    )


def section_title(title: str) -> rx.Component:
    return rx.el.h2(title, class_name="text-xl font-bold text-text-primary mt-8 mb-4")


def terms_page() -> rx.Component:
    return rx.el.div(terms_content(), footer())