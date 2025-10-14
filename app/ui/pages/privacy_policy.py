import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.components.legal_components import (
    legal_page_layout,
    legal_section,
    subprocessor_table,
    retention_table,
)


def privacy_policy_page() -> rx.Component:
    return legal_page_layout(
        title=LegalState.content["privacy_policy_title"],
        last_updated=LegalState.last_updated,
        toc_items=LegalState.privacy_toc,
        pdf_name="privacy_policy.pdf",
        children=[
            legal_section(
                "s1",
                LegalState.content["s1_title"],
                [
                    rx.el.p(
                        LegalState.content["s1_p1"],
                        rx.el.strong(LegalState.org_legal_name),
                        ", ",
                        LegalState.content["s1_p2"],
                        " ",
                        rx.el.strong(LegalState.org_vat),
                        ", ",
                        LegalState.content["s1_p3"],
                        " ",
                        rx.el.strong(LegalState.org_address),
                        ". ",
                        LegalState.content["s1_p4"],
                        " ",
                        rx.el.a(
                            LegalState.org_email,
                            href=f"mailto:{LegalState.org_email}",
                            class_name="text-accent-cyan hover:underline",
                        ),
                        ". ",
                        LegalState.content["s1_p5"],
                        " ",
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
                "s2",
                LegalState.content["s2_title"],
                [rx.el.p(LegalState.content["s2_p1"])],
            ),
            legal_section(
                "s3",
                LegalState.content["s3_title"],
                [rx.el.p(LegalState.content["s3_p1"])],
            ),
            legal_section(
                "s4",
                LegalState.content["s4_title"],
                [rx.el.p(LegalState.content["s4_p1"]), subprocessor_table()],
            ),
            legal_section(
                "s5",
                LegalState.content["s5_title"],
                [rx.el.p(LegalState.content["s5_p1"])],
            ),
            legal_section(
                "s6",
                LegalState.content["s6_title"],
                [rx.el.p(LegalState.content["s6_p1"]), retention_table()],
            ),
            legal_section(
                "s7",
                LegalState.content["s7_title"],
                [
                    rx.el.p(
                        LegalState.content["s7_p1"],
                        rx.el.a(
                            "/privacy-center",
                            href="/privacy-center",
                            class_name="text-accent-cyan hover:underline",
                        ),
                        ".",
                    )
                ],
            ),
            legal_section(
                "s8",
                LegalState.content["s8_title"],
                [
                    rx.el.p(
                        LegalState.content["s8_p1"],
                        rx.el.a(
                            "/legal/cookies",
                            href="/legal/cookies",
                            class_name="text-accent-cyan hover:underline",
                        ),
                        ".",
                    )
                ],
            ),
            legal_section(
                "s9",
                LegalState.content["s9_title"],
                [rx.el.p(LegalState.content["s9_p1"])],
            ),
            legal_section(
                "s10",
                LegalState.content["s10_title"],
                [rx.el.p(LegalState.content["s10_p1"])],
            ),
            legal_section(
                "s11",
                LegalState.content["s11_title"],
                [rx.el.p(LegalState.content["s11_p1"])],
            ),
            legal_section(
                "s12",
                LegalState.content["s12_title"],
                [rx.el.p(LegalState.content["s12_p1"])],
            ),
        ],
    )