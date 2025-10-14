import reflex as rx
from app.ui.states.legal_state import LegalState
from app.ui.pages.legal import legal_page_layout, legal_doc_view


def terms_page() -> rx.Component:
    return legal_page_layout(
        legal_doc_view(
            LegalState.terms_and_conditions["title"],
            LegalState.terms_and_conditions["sections"],
            LegalState.terms_and_conditions["disclaimer"],
        )
    )