import reflex as rx
from app.ui.states.who_we_are_state import WhoWeAreState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style


def who_we_are_page() -> rx.Component:
    return rx.el.div(
        sidebar(),
        rx.el.main(
            rx.el.header(
                rx.el.h1(
                    "Who We Are",
                    class_name="text-3xl font-bold text-text-primary title-gradient",
                ),
                class_name=header_style,
            ),
            rx.el.div(
                mission_section(),
                ecosystem_map_section(),
                what_we_solve_section(),
                security_section(),
                contact_section(),
                class_name="p-8 space-y-12",
            ),
            class_name=page_content_style,
        ),
        ecosystem_modal(),
        class_name=page_style,
    )


def mission_section() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Our Mission", class_name="text-2xl font-semibold mb-4"),
        rx.el.p(
            "To provide a seamless, intelligent, and automated testing ecosystem that empowers development teams to ship higher-quality software, faster. We believe in proactive quality, developer-centric tooling, and a zero-defect mindset.",
            class_name="text-text-secondary max-w-3xl",
        ),
        **card_style("cyan"),
    )


def ecosystem_map_section() -> rx.Component:
    return rx.el.section(
        rx.el.h2("The Colabe Ecosystem", class_name="text-2xl font-semibold mb-6"),
        rx.el.div(
            rx.foreach(
                WhoWeAreState.ecosystem_nodes, lambda node: ecosystem_node_card(node)
            ),
            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
        ),
    )


def ecosystem_node_card(node: dict) -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.icon(node["icon"], size=24, class_name=f"text-accent-{node['color']}"),
            rx.el.h3(node["name"], class_name="text-lg font-semibold"),
            class_name="flex items-center gap-3",
        ),
        rx.el.p(
            node["description"], class_name="text-sm text-left text-text-secondary mt-2"
        ),
        on_click=lambda: WhoWeAreState.open_modal(node),
        **card_style(node["color"]),
    )


def ecosystem_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.content(
            rx.radix.primitives.dialog.title(
                WhoWeAreState.modal_content["name"],
                class_name="text-2xl font-bold title-gradient",
            ),
            rx.radix.primitives.dialog.description(
                WhoWeAreState.modal_content["description"],
                class_name="text-text-secondary mt-2",
            ),
            rx.el.div(
                rx.el.a(
                    WhoWeAreState.modal_content["cta_text"],
                    href=WhoWeAreState.modal_content["cta_link"],
                    class_name="px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
                ),
                rx.radix.primitives.dialog.close(
                    rx.el.button(
                        "Close",
                        class_name="px-4 py-2 bg-bg-base text-text-secondary font-semibold rounded-lg hover:bg-white/10",
                    )
                ),
                class_name="flex justify-end gap-4 mt-6",
            ),
            style={
                "background_color": "var(--bg-elevated)",
                "border_color": "var(--accent-cyan)/0.3",
            },
        ),
        open=WhoWeAreState.is_modal_open,
        on_open_change=WhoWeAreState.close_modal,
    )


def what_we_solve_section() -> rx.Component:
    return rx.el.section(
        rx.el.h2("What Test Labo Solves", class_name="text-2xl font-semibold mb-4"),
        rx.el.p(
            "Test Labo addresses the core challenges of modern software testing: fragmented tooling, slow feedback cycles, and the high cost of fixing bugs late in the development process. By providing a unified platform for cross-stack testing, intelligent autofixes, and proactive budget enforcement, we help teams shift quality left and maintain velocity without compromising on standards.",
            class_name="text-text-secondary max-w-3xl",
        ),
        **card_style("magenta"),
    )


def security_section() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Security & Compliance", class_name="text-2xl font-semibold mb-4"),
        rx.el.p(
            "We are committed to the highest standards of security. Our platform features strict data residency controls, end-to-end encryption, fine-grained RBAC, and regular third-party audits. We provide SBOMs for all scans and maintain a transparent incident response posture.",
            class_name="text-text-secondary",
        ),
        rx.el.a(
            "View Security Details",
            href="/security",
            class_name="mt-4 inline-block text-accent-cyan hover:underline",
        ),
        **card_style("gold"),
    )


def contact_section() -> rx.Component:
    return rx.el.section(
        rx.el.h2("Contact Us", class_name="text-2xl font-semibold mb-4"),
        rx.el.p(
            "Have questions or need support? Reach out to us at ",
            rx.el.a(
                "contact@colabe.ai",
                href="mailto:contact@colabe.ai",
                class_name="text-accent-cyan hover:underline",
            ),
            ".",
            class_name="text-text-secondary",
        ),
        **card_style("cyan"),
    )