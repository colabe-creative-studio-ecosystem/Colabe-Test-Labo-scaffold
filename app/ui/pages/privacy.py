import reflex as rx
from app.ui.components.footer import footer


def privacy_content() -> rx.Component:
    return rx.el.div(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Privacy Policy",
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
                section_title("1. Information Collection"),
                rx.el.p(
                    "We collect information you provide directly to us, such as when you create an account, update your profile, or use our interactive features."
                ),
                section_title("2. How We Use Information"),
                rx.el.p(
                    "We use the information we collect to provide, maintain, and improve our services, to process your transactions, and to communicate with you."
                ),
                section_title("3. Data Storage"),
                rx.el.p(
                    "Your data is securely stored on servers located within the European Union. We implement appropriate technical and organizational measures to protect your personal data."
                ),
                section_title("4. Cookies"),
                rx.el.p(
                    "We use cookies and similar tracking technologies to track the activity on our service and hold certain information."
                ),
                section_title("5. Third-Party Services"),
                rx.el.p(
                    "We may employ third-party companies and individuals to facilitate our Service, to provide the Service on our behalf, or to assist us in analyzing how our Service is used."
                ),
                section_title("6. User Rights (GDPR)"),
                rx.el.p(
                    "You have the right to access, update, or delete the information we have on you. Whenever made possible, you can access, update or request deletion of your Personal Data directly within your account settings section."
                ),
                section_title("7. Data Security"),
                rx.el.p(
                    "The security of your data is important to us, but remember that no method of transmission over the Internet, or method of electronic storage is 100% secure."
                ),
                section_title("8. Changes to Policy"),
                rx.el.p(
                    "We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page."
                ),
                section_title("9. Contact Information"),
                rx.el.p(
                    "If you have any questions about this Privacy Policy, please contact us at Colabe@mail.com."
                ),
                class_name="prose prose-invert max-w-none space-y-6 text-gray-300",
            ),
            class_name="container mx-auto px-6 py-12 flex-1",
        ),
        class_name="flex flex-col min-h-screen colabe-bg",
    )


def section_title(title: str) -> rx.Component:
    return rx.el.h2(title, class_name="text-xl font-bold text-[#E8F0FF] mt-8 mb-4")


def privacy_page() -> rx.Component:
    return rx.el.div(privacy_content(), footer())