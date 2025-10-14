import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.pages.legal import legal_page_layout, legal_doc_view


def privacy_policy_page() -> rx.Component:
    return legal_page_layout(
        legal_doc_view(
            LegalState.privacy_policy["title"],
            LegalState.privacy_policy["sections"],
            LegalState.privacy_policy["disclaimer"],
        )
    )