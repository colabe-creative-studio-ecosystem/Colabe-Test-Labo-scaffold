import reflex as rx
from app.ui.states.auth_state import AuthState


class LegalState(AuthState):
    org_legal_name: str = "Colabe creative Studio, S.L."
    org_address: str = "C/ de Pallars, 193, 08005 Barcelona, Spain"
    org_country: str = "Spain"
    org_vat: str = "ESB01234567"
    org_email: str = "legal@colabe.ai"
    dpo_email: str = "dpo@colabe.ai"
    governing_law: str = "Spain"
    venue: str = "Barcelona"
    last_updated: str = "2024-07-25"