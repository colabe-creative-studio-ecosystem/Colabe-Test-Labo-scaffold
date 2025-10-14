import reflex as rx
from app.ui.states.auth_state import AuthState
from app.core.settings import settings
from datetime import datetime
import json
from typing import Literal, TypedDict

EN = "en"
ES = "es"
Language = Literal["en", "es"]


class LegalSection(TypedDict):
    id: str
    title: str
    content: str


class LegalDocument(TypedDict):
    title: str
    last_updated: str
    disclaimer: str
    sections: list[LegalSection]


PRIVACY_POLICY = {
    EN: {
        "title": "Privacy Policy",
        "last_updated": "2024-10-26",
        "disclaimer": "This template is for convenience and is not legal advice.",
        "sections": [
            {
                "id": "controller",
                "title": "Controller & Contact",
                "content": "The data controller is {ORG_LEGAL_NAME}, located at {ORG_ADDRESS_LINE1}, {ORG_CITY}, {ORG_POSTAL_CODE}, {ORG_COUNTRY}. You can contact us at {ORG_EMAIL} or via our contact form at {CONTACT_FORM_URL}. Our Data Protection Officer can be reached at {DPO_EMAIL}.",
            },
            {
                "id": "data_processed",
                "title": "What Data We Process",
                "content": "We process account data, organization metadata, project metadata, run telemetry, artifact metadata, billing identifiers, support interactions, and consent logs.",
            },
            {
                "id": "purposes",
                "title": "Purposes & Legal Bases",
                "content": "Data is processed for service provision (Contract), security and analytics (Legitimate Interest), marketing (Consent), and tax records (Legal Obligation).",
            },
            {
                "id": "recipients",
                "title": "Recipients / Processors",
                "content": "We use third-party subprocessors to provide our service. Here is a list of our current subprocessors:",
            },
            {
                "id": "transfers",
                "title": "International Transfers",
                "content": "Our default data residency is in the EU. We use Standard Contractual Clauses for data transfers outside the EU.",
            },
            {
                "id": "retention",
                "title": "Data Retention",
                "content": "We retain data based on its type: Account data (life of contract + 6y), Artifacts (plan-dependent), Audit/Consent logs (2y).",
            },
            {
                "id": "rights",
                "title": "Your Rights",
                "content": "You have the right to access, rectify, delete, and port your data. Submit requests via our /privacy-center.",
            },
            {
                "id": "cookies",
                "title": "Cookies & Technologies",
                "content": "We use necessary, functional, analytics, and marketing cookies. Manage preferences at /legal/cookies.",
            },
            {
                "id": "security",
                "title": "Security Measures",
                "content": "We implement encryption, RBAC, audit logs, and vulnerability management.",
            },
            {
                "id": "children",
                "title": "Children's Privacy",
                "content": "Our service is not directed to children under 16.",
            },
            {
                "id": "changes",
                "title": "Changes to This Notice",
                "content": "This policy may be updated. Last updated on {last_updated}.",
            },
            {
                "id": "supervisory",
                "title": "Supervisory Authority",
                "content": "If you are in the EU, you can contact the Spanish Data Protection Agency (AEPD).",
            },
        ],
    },
    ES: {
        "title": "Política de Privacidad",
        "last_updated": "2024-10-26",
        "disclaimer": "Esta plantilla es para su conveniencia y no constituye asesoramiento legal.",
        "sections": [
            {
                "id": "controller",
                "title": "Responsable y Contacto",
                "content": "El responsable del tratamiento es {ORG_LEGAL_NAME}, con domicilio en {ORG_ADDRESS_LINE1}, {ORG_CITY}, {ORG_POSTAL_CODE}, {ORG_COUNTRY}. Puede contactarnos en {ORG_EMAIL} o a través de nuestro formulario de contacto en {CONTACT_FORM_URL}. Nuestro Delegado de Protección de Datos está disponible en {DPO_EMAIL}.",
            },
            {
                "id": "data_processed",
                "title": "Qué Datos Tratamos",
                "content": "Tratamos datos de cuenta, metadatos de organización, metadatos de proyecto, telemetría de ejecución, metadatos de artefactos, identificadores de facturación, interacciones de soporte y registros de consentimiento.",
            },
            {
                "id": "purposes",
                "title": "Fines y Bases Legales",
                "content": "Los datos se tratan para la prestación del servicio (Contrato), seguridad y análisis (Interés Legítimo), marketing (Consentimiento) y registros fiscales (Obligación Legal).",
            },
            {
                "id": "recipients",
                "title": "Destinatarios / Encargados",
                "content": "Utilizamos subencargados de terceros para prestar nuestro servicio. Aquí hay una lista de nuestros subencargados actuales:",
            },
            {
                "id": "transfers",
                "title": "Transferencias Internacionales",
                "content": "Nuestra residencia de datos por defecto es en la UE. Usamos Cláusulas Contractuales Tipo para transferencias de datos fuera de la UE.",
            },
            {
                "id": "retention",
                "title": "Retención de Datos",
                "content": "Retenemos los datos según su tipo: Datos de cuenta (vida del contrato + 6 años), Artefactos (dependiente del plan), Registros de auditoría/consentimiento (2 años).",
            },
            {
                "id": "rights",
                "title": "Tus Derechos",
                "content": "Tienes derecho a acceder, rectificar, suprimir y portar tus datos. Envía solicitudes a través de nuestro /privacy-center.",
            },
            {
                "id": "cookies",
                "title": "Cookies y Tecnologías",
                "content": "Usamos cookies necesarias, funcionales, de análisis y de marketing. Gestiona tus preferencias en /legal/cookies.",
            },
            {
                "id": "security",
                "title": "Medidas de Seguridad",
                "content": "Implementamos cifrado, RBAC, registros de auditoría y gestión de vulnerabilidades.",
            },
            {
                "id": "children",
                "title": "Privacidad de Menores",
                "content": "Nuestro servicio no está dirigido a menores de 16 años.",
            },
            {
                "id": "changes",
                "title": "Cambios a este Aviso",
                "content": "Esta política puede ser actualizada. Última actualización el {last_updated}.",
            },
            {
                "id": "supervisory",
                "title": "Autoridad de Supervisión",
                "content": "Si se encuentra en la UE, puede contactar a la Agencia Española de Protección de Datos (AEPD).",
            },
        ],
    },
}
TERMS_CONDITIONS = {
    EN: {
        "title": "Terms & Conditions",
        "last_updated": "2024-10-26",
        "disclaimer": "This template is for convenience and is not legal advice.",
        "sections": [
            {
                "id": "service",
                "title": "Service Description",
                "content": "Colabe provides AI testing and analysis. No guarantee of bug-free target apps.",
            },
            {
                "id": "accounts",
                "title": "Account, Tenants & Roles",
                "content": "Roles include Owner, Admin, Developer, Viewer with different responsibilities.",
            },
            {
                "id": "aup",
                "title": "Acceptable Use",
                "content": "Do not scan targets without authorization. No illegal content or interference.",
            },
            {
                "id": "pricing",
                "title": "Plans, Pricing & Coins",
                "content": "We offer Free, Pro, and Enterprise plans with a coin-based wallet system.",
            },
            {
                "id": "autofix",
                "title": "Autofix & PRs",
                "content": "Autofix provides proposals only. Customer is responsible for reviewing and merging.",
            },
            {
                "id": "ip",
                "title": "Intellectual Property",
                "content": "You own your content; we own our services. We get a license to use feedback.",
            },
            {
                "id": "sla",
                "title": "Service Levels & Maintenance",
                "content": "SLOs and maintenance windows are outlined on our status page.",
            },
            {
                "id": "disclaimer",
                "title": "Warranties & Disclaimers",
                "content": "Service is provided 'AS IS'. Beta features may have issues.",
            },
            {
                "id": "liability",
                "title": "Liability & Indemnity",
                "content": "Our liability is capped at amounts paid in the prior 12 months.",
            },
            {
                "id": "termination",
                "title": "Termination & Suspension",
                "content": "We may terminate accounts for AUP breach or non-payment.",
            },
            {
                "id": "law",
                "title": "Governing Law & Venue",
                "content": "Governing law is {GOVERNING_LAW}, venue in {VENUE_CITY}.",
            },
            {
                "id": "changes",
                "title": "Changes to Terms",
                "content": "We will notify you of material changes to these terms.",
            },
            {
                "id": "contact",
                "title": "Contact",
                "content": "Contact us at {ORG_EMAIL}.",
            },
        ],
    },
    ES: {
        "title": "Términos y Condiciones",
        "last_updated": "2024-10-26",
        "disclaimer": "Esta plantilla es para su conveniencia y no constituye asesoramiento legal.",
        "sections": [
            {
                "id": "service",
                "title": "Descripción del Servicio",
                "content": "Colabe proporciona pruebas y análisis con IA. No se garantiza que las aplicaciones de destino estén libres de errores.",
            },
            {
                "id": "accounts",
                "title": "Cuenta, Inquilinos y Roles",
                "content": "Los roles incluyen Propietario, Administrador, Desarrollador, Espectador con diferentes responsabilidades.",
            },
            {
                "id": "aup",
                "title": "Uso Aceptable",
                "content": "No escanee objetivos sin autorización. No contenido ilegal ni interferencia.",
            },
            {
                "id": "pricing",
                "title": "Planes, Precios y Monedas",
                "content": "Ofrecemos planes Free, Pro y Enterprise con un sistema de billetera basado en monedas.",
            },
            {
                "id": "autofix",
                "title": "Autofix y PRs",
                "content": "Autofix solo proporciona propuestas. El cliente es responsable de revisar y fusionar.",
            },
            {
                "id": "ip",
                "title": "Propiedad Intelectual",
                "content": "Usted es dueño de su contenido; nosotros somos dueños de nuestros servicios. Obtenemos una licencia para usar los comentarios.",
            },
            {
                "id": "sla",
                "title": "Niveles de Servicio y Mantenimiento",
                "content": "Los SLO y las ventanas de mantenimiento se describen en nuestra página de estado.",
            },
            {
                "id": "disclaimer",
                "title": "Garantías y Exenciones de Responsabilidad",
                "content": "El servicio se proporciona 'TAL CUAL'. Las características beta pueden tener problemas.",
            },
            {
                "id": "liability",
                "title": "Responsabilidad e Indemnización",
                "content": "Nuestra responsabilidad está limitada a las cantidades pagadas en los 12 meses anteriores.",
            },
            {
                "id": "termination",
                "title": "Terminación y Suspensión",
                "content": "Podemos cancelar cuentas por incumplimiento de AUP o falta de pago.",
            },
            {
                "id": "law",
                "title": "Ley Aplicable y Jurisdicción",
                "content": "La ley aplicable es {GOVERNING_LAW}, jurisdicción en {VENUE_CITY}.",
            },
            {
                "id": "changes",
                "title": "Cambios en los Términos",
                "content": "Le notificaremos los cambios materiales en estos términos.",
            },
            {
                "id": "contact",
                "title": "Contacto",
                "content": "Contáctenos en {ORG_EMAIL}.",
            },
        ],
    },
}


class LegalState(AuthState):
    lang: Language = "en"

    @rx.event
    def set_lang(self, lang: Language):
        self.lang = lang

    def _get_org_vars(self) -> dict:
        return {
            "ORG_LEGAL_NAME": settings.ORG_LEGAL_NAME,
            "ORG_ADDRESS_LINE1": settings.ORG_ADDRESS_LINE1,
            "ORG_CITY": settings.ORG_CITY,
            "ORG_POSTAL_CODE": settings.ORG_POSTAL_CODE,
            "ORG_COUNTRY": settings.ORG_COUNTRY,
            "ORG_EMAIL": settings.ORG_EMAIL,
            "DPO_EMAIL": settings.DPO_EMAIL or settings.ORG_EMAIL,
            "CONTACT_FORM_URL": settings.CONTACT_FORM_URL,
            "GOVERNING_LAW": settings.GOVERNING_LAW,
            "VENUE_CITY": settings.VENUE_CITY,
        }

    def _format_content(self, content_template: dict) -> LegalDocument:
        org_vars = self._get_org_vars()
        formatted_sections = []
        for section in content_template["sections"]:
            formatted_content = section["content"].format(
                **org_vars, last_updated=content_template["last_updated"]
            )
            formatted_sections.append(
                {
                    "id": section["id"],
                    "title": section["title"],
                    "content": formatted_content,
                }
            )
        return {
            "title": content_template["title"],
            "last_updated": content_template["last_updated"],
            "disclaimer": content_template["disclaimer"],
            "sections": formatted_sections,
        }

    @rx.var
    def privacy_policy(self) -> LegalDocument:
        policy_template = PRIVACY_POLICY[self.lang]
        return self._format_content(policy_template)

    @rx.var
    def terms_and_conditions(self) -> LegalDocument:
        terms_template = TERMS_CONDITIONS[self.lang]
        return self._format_content(terms_template)

    @rx.var
    def subprocessors(self) -> list[dict[str, str]]:
        return settings.SUBPROCESSORS_JSON

    @rx.event
    def download_pdf(self, content: str):
        return rx.download(data=content, filename="document.txt")