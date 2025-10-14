import reflex as rx
import os
import json
import datetime
from typing import TypedDict, Literal
from app.ui.states.auth_state import AuthState


class Subprocessor(TypedDict):
    name: str
    purpose: str
    region: str
    dpa_url: str


class RetentionItem(TypedDict):
    data_type: str
    period: str


class TocItem(TypedDict):
    id: str
    title: str


DSRStatus = Literal["received", "verifying", "in_progress", "completed", "rejected"]


class LegalState(AuthState):
    lang: str = rx.Cookie("en", name="colabe_lang")
    content: dict[str, str] = {}
    last_updated: str = "2024-07-26"
    current_year: int = datetime.date.today().year
    org_legal_name: str = "Colabe Creative Studio, S.L."
    org_address: str = "C/ de Pallars, 193, 08005 Barcelona"
    org_country: str = "Spain"
    org_vat: str = "ESB01234567"
    org_email: str = "legal@colabe.ai"
    dpo_email: str = "dpo@colabe.ai"
    governing_law: str = "Spain"
    venue: str = "Barcelona"
    contact_form_url: str = "/contact"
    subprocessors: list[Subprocessor] = []
    subprocessors_last_updated: str = "2024-07-01"
    retention_schedule: list[RetentionItem] = []
    privacy_toc: list[TocItem] = []
    terms_toc: list[TocItem] = []
    cookies_toc: list[TocItem] = []
    show_consent_banner: bool = False
    show_preferences_modal: bool = False
    consent_given: rx.Var[bool] = False
    consent_preferences: dict[str, bool] = {
        "necessary": True,
        "functional": False,
        "analytics": False,
        "marketing": False,
    }
    dsr_email: str = ""
    dsr_request_type: str = "export"
    dsr_status: DSRStatus = "received"
    dsr_verification_code: str = ""
    dsr_code_sent: bool = False
    dsr_error_message: str = ""

    def _load_legal_content(self):
        if self.lang == "es":
            self.content = {
                "privacy_policy_title": "Política de Privacidad",
                "s1_title": "1. Responsable del Tratamiento y Contacto",
                "s1_p1": "El responsable del tratamiento de sus datos personales es ",
                "s1_p2": "con NIF",
                "s1_p3": "con domicilio en",
                "s1_p4": "Puede contactarnos en",
                "s1_p5": "o a nuestro Delegado de Protección de Datos en",
                "s2_title": "2. Qué Datos Tratamos",
                "s2_p1": "Recopilamos datos de cuenta (nombre, email), metadatos de organización, metadatos de proyectos/repositorios, telemetría de ejecuciones, metadatos de artefactos (nombres de archivo, tamaños, tipos), identificadores de facturación (no PAN), interacciones de soporte y registros de consentimiento.",
                "s3_title": "3. Finalidades y Bases Legales",
                "s3_p1": "Tratamos sus datos para: ejecutar el contrato (proveer el servicio, facturación), por interés legítimo (seguridad, prevención de fraude, análisis de producto), con su consentimiento (marketing, cookies opcionales), y por obligación legal (registros fiscales).",
                "s4_title": "4. Destinatarios / Encargados del Tratamiento",
                "s4_p1": "Utilizamos los siguientes sub-encargados del tratamiento para prestar nuestros servicios:",
                "s5_title": "5. Transferencias Internacionales y Residencia de Datos",
                "s5_p1": "La residencia de datos por defecto es la UE. Permitimos fijar el almacenamiento en regiones específicas. Las transferencias se basan en Cláusulas Contractuales Tipo.",
                "s6_title": "6. Plazos de Conservación",
                "s6_p1": "Conservamos sus datos según el siguiente calendario:",
                "s7_title": "7. Sus Derechos (GDPR + CCPA/CPRA)",
                "s7_p1": "Tiene derecho de acceso, rectificación, supresión, portabilidad, limitación y oposición. Puede ejercerlos a través de nuestro ",
                "s8_title": "8. Cookies y Tecnologías Similares",
                "s8_p1": "Usamos cookies (Necesarias, Funcionales, Analíticas, Marketing). Vea nuestra ",
                "s9_title": "9. Medidas de Seguridad",
                "s9_p1": "Implementamos cifrado en tránsito/reposo, RBAC, logs de auditoría, gestión de vulnerabilidades y un plan de respuesta a incidentes.",
                "s10_title": "10. Menores",
                "s10_p1": "Nuestro servicio no está dirigido a menores de 16 años y no tratamos sus datos a sabiendas.",
                "s11_title": "11. Cambios a esta Noticia",
                "s11_p1": "Esta política se versiona con una fecha de 'Última Actualización' y un resumen de cambios.",
                "s12_title": "12. Cómo Contactar a la Autoridad de Control",
                "s12_p1": "Si reside en la UE, puede presentar una reclamación ante la Agencia Española de Protección de Datos (AEPD).",
                "terms_title": "Términos y Condiciones",
                "t_s1_title": "1. Descripción del Servicio",
                "t_s1_p1": "Proporcionamos una plataforma de testeo de IA sin garantía de que las apps objetivo queden libres de errores.",
                "t_s2_title": "2. Cuenta, Inquilinos y Roles",
                "t_s2_p1": "Los roles de Propietario/Admin/Desarrollador/Espectador tienen distintas responsabilidades.",
                "t_s3_title": "3. Uso Aceptable",
                "t_s3_p1": "Prohibido escanear objetivos sin autorización, contenido ilegal, interferencia con sistemas de terceros. Se aplican límites de uso.",
                "t_s4_title": "4. Planes, Precios y Monedas",
                "t_s4_p1": "Suscripciones (Gratis/Pro/Empresa), monedero de 'coins', retenciones/finalizaciones, política de reembolsos y opción de Recarga Automática.",
                "t_s5_title": "5. Autofix y PRs",
                "t_s5_p1": "Las correcciones automáticas son solo propuestas. El cliente revisa y fusiona. No se editan secretos ni infraestructura.",
                "t_s6_title": "6. Propiedad Intelectual",
                "t_s6_p1": "Su contenido es suyo, nuestros servicios son nuestros. Nos concede una licencia sobre el feedback. Licencias de SDK aplicables.",
                "t_s7_title": "7. Niveles de Servicio y Mantenimiento",
                "t_s7_p1": "Referencias a SLOs, ventanas de mantenimiento y página de estado.",
                "t_s8_title": "8. Garantías y Exenciones",
                "t_s8_p1": "El servicio se proporciona 'TAL CUAL'. Las funcionalidades beta no tienen garantías. La precisión no está garantizada.",
                "t_s9_title": "9. Responsabilidad e Indemnización",
                "t_s9_p1": "Responsabilidad limitada a las cantidades pagadas en los 12 meses anteriores. Exclusión de daños indirectos.",
                "t_s10_title": "10. Terminación y Suspensión",
                "t_s10_p1": "Por causa justificada (incumplimiento, impago). Derechos de exportación. Plazos de eliminación de datos.",
                "t_s11_title": "11. Ley Aplicable y Jurisdicción",
                "t_s11_p1": "Estos términos se rigen por la legislación de ",
                "t_s11_p2": ". Cualquier disputa se resolverá en los tribunales de ",
                "t_s12_title": "12. Cambios en los Términos",
                "t_s12_p1": "Notificación y fecha de entrada en vigor de los cambios.",
                "t_s13_title": "13. Contacto",
                "t_s13_p1": "Puede contactarnos a través de nuestro formulario de contacto o por correo electrónico.",
            }
        else:
            self.content = {
                "privacy_policy_title": "Privacy Policy",
                "s1_title": "1. Controller & Contact",
                "s1_p1": "The data controller responsible for your personal data is ",
                "s1_p2": "with VAT number",
                "s1_p3": "located at",
                "s1_p4": "You can contact us at",
                "s1_p5": "or our Data Protection Officer at",
                "s2_title": "2. What Data We Process",
                "s2_p1": "We process account data (name, email), org/tenant metadata, project/repo metadata, run telemetry, artifacts metadata (filenames, sizes, types), billing identifiers (non-PAN), support interactions, and consent logs.",
                "s3_title": "3. Purposes & Legal Bases",
                "s3_p1": "We process data for Contract (provide service, billing), Legitimate Interests (security, fraud prevention, product analytics), Consent (marketing, optional cookies), and Legal obligation (tax records).",
                "s4_title": "4. Recipients / Processors",
                "s4_p1": "We use the following subprocessors to deliver our services:",
                "s5_title": "5. International Transfers & Data Residency",
                "s5_p1": "EU default residency; regional storage pinning; SCCs for transfers. We list regions for data storage.",
                "s6_title": "6. Retention",
                "s6_p1": "We retain data according to the following schedule:",
                "s7_title": "7. Your Rights (GDPR + CCPA/CPRA)",
                "s7_p1": "You have rights to Access/Rectify/Delete/Portability/Restrict/Object, and opt-out of marketing. Submit requests via our ",
                "s8_title": "8. Cookies & Similar Technologies",
                "s8_p1": "We use cookies (Strictly Necessary, Functional, Analytics, Marketing). See our ",
                "s9_title": "9. Security Measures",
                "s9_p1": "We use encryption in transit/at rest, RBAC, audit logs, vulnerability management, and have an incident response plan.",
                "s10_title": "10. Children",
                "s10_p1": "Not directed to children under 16; we do not knowingly process their data.",
                "s11_title": "11. Changes to This Notice",
                "s11_p1": "This notice is versioned with 'Last Updated' and a change log snippet.",
                "s12_title": "12. How to Contact Supervisory Authority",
                "s12_p1": "If in the EU, you can contact the Spanish Data Protection Agency (AEPD).",
                "terms_title": "Terms & Conditions",
                "t_s1_title": "1. Service Description",
                "t_s1_p1": "AI testing, analysis, autofix proposals; no guarantee of bug-free target apps.",
                "t_s2_title": "2. Account, Tenants & Roles",
                "t_s2_p1": "Owner/Admin/Developer/Viewer roles and responsibilities.",
                "t_s3_title": "3. Acceptable Use",
                "t_s3_p1": "No scanning targets without authorization; no illegal content; no interference with third-party systems; rate limits; fair use.",
                "t_s4_title": "4. Plans, Pricing & Coins",
                "t_s4_p1": "Subscriptions (Free/Pro/Enterprise), coins wallet, holds/finalize, refunds policy, Auto Top-Up opt-in.",
                "t_s5_title": "5. Autofix & PRs",
                "t_s5_p1": "Proposals only; customer reviews/merges; guardrails; no editing secrets/infra.",
                "t_s6_title": "6. Intellectual Property",
                "t_s6_p1": "Your content vs. our services; feedback license; SDK licenses.",
                "t_s7_title": "7. Service Levels & Maintenance",
                "t_s7_p1": "SLO references, maintenance windows; status page.",
                "t_s8_title": "8. Warranties & Disclaimers",
                "t_s8_p1": "'AS IS'; beta features disclaimers; accuracy not guaranteed.",
                "t_s9_title": "9. Liability & Indemnity",
                "t_s9_p1": "Cap at amounts paid in prior 12 months; exclusion of indirect damages; your indemnity for unauthorized scanning.",
                "t_s10_title": "10. Termination & Suspension",
                "t_s10_p1": "For cause (AUP breach, non-payment); export rights; data deletion timeline.",
                "t_s11_title": "11. Governing Law & Venue",
                "t_s11_p1": "These terms are governed by the laws of ",
                "t_s11_p2": ". Any dispute will be resolved in the courts of ",
                "t_s12_title": "12. Changes to Terms",
                "t_s12_p1": "Notice and effective date of changes.",
                "t_s13_title": "13. Contact",
                "t_s13_p1": "You can reach us via our contact form or email.",
            }

    def _load_dynamic_vars(self):
        subprocessors_json = os.environ.get(
            "SUBPROCESSORS_JSON",
            '[{"name": "Amazon Web Services", "purpose": "Cloud Hosting", "region": "EU (Ireland)", "dpa_url": "#"}, {"name": "Stripe", "purpose": "Payment Processing", "region": "USA", "dpa_url": "#"}]',
        )
        self.subprocessors = json.loads(subprocessors_json)
        self.retention_schedule = [
            {"data_type": "Account Data", "period": "Life of contract + 6 years"},
            {"data_type": "Artifacts (Free)", "period": "7 days"},
            {"data_type": "Artifacts (Pro)", "period": "30 days"},
            {"data_type": "Audit Logs", "period": "2 years"},
            {"data_type": "Consent Logs", "period": "2 years"},
        ]

    def _load_tocs(self):
        self.privacy_toc = [
            {"id": f"s{i}", "title": self.content.get(f"s{i}_title", "")}
            for i in range(1, 13)
        ]
        self.terms_toc = [
            {"id": f"s{i}", "title": self.content.get(f"t_s{i}_title", "")}
            for i in range(1, 14)
        ]
        self.cookies_toc = [
            {"id": "s1", "title": "What are cookies?"},
            {"id": "s2", "title": "Cookie Categories"},
            {"id": "s3", "title": "Your Choices"},
        ]

    @rx.event
    def on_load_legal(self):
        self._load_legal_content()
        self._load_dynamic_vars()
        self._load_tocs()
        if self.user:
            self.dsr_email = self.user.email
        return LegalState.check_consent

    @rx.event
    def set_lang(self, lang: str):
        self.lang = lang
        self._load_legal_content()
        self._load_tocs()
        return rx.console_log(f"Language changed to {lang}")

    @rx.event
    def check_consent(self):
        return rx.call_script(
            "localStorage.getItem('colabe_consent')",
            callback=LegalState.handle_consent_result,
        )

    @rx.event
    def handle_consent_result(self, result: list[str]):
        if result[0]:
            self.consent_given = True
            preferences = json.loads(result[0])
            self.consent_preferences = preferences
        else:
            self.consent_given = False
            self.show_consent_banner = True

    @rx.event
    def update_consent(self, category: str, value: bool):
        self.consent_preferences[category] = value

    @rx.event
    def save_consent(self):
        consent_json = json.dumps(self.consent_preferences)
        self.show_consent_banner = False
        self.show_preferences_modal = False
        self.consent_given = True
        yield rx.console_log(f"privacy.consent.updated: {consent_json}")
        yield rx.call_script(
            f"localStorage.setItem('colabe_consent', '{consent_json}')"
        )

    @rx.event
    def accept_all_cookies(self):
        for key in self.consent_preferences:
            self.consent_preferences[key] = True
        return LegalState.save_consent()

    @rx.event
    def reject_non_essential_cookies(self):
        for key in self.consent_preferences:
            if key != "necessary":
                self.consent_preferences[key] = False
        return LegalState.save_consent()

    @rx.event
    def show_cookie_preferences(self):
        self.show_preferences_modal = True

    @rx.event
    def hide_cookie_preferences(self):
        self.show_preferences_modal = False

    @rx.event
    def submit_dsr_request(self, form_data: dict):
        if not self.is_logged_in:
            self.dsr_email = form_data.get("email", "")
            if not self.dsr_email:
                self.dsr_error_message = "Email is required."
                return
            self.dsr_code_sent = True
            self.dsr_error_message = ""
            yield rx.console_log(f"DSR: Sending verification code to {self.dsr_email}")
        else:
            self.dsr_email = self.user.email
            self.dsr_request_type = form_data.get("request_type", "export")
            self.dsr_status = "received"
            yield rx.console_log(
                f"privacy.request.created: type={self.dsr_request_type}, tenant_id={self.user.tenant_id}"
            )
            return LegalState.process_dsr

    @rx.event
    def verify_dsr_code(self, form_data: dict):
        code = form_data.get("code", "")
        if code == "123456":
            self.dsr_status = "received"
            self.dsr_error_message = ""
            yield rx.console_log(
                f"privacy.request.created: type={self.dsr_request_type}, email={self.dsr_email}"
            )
            return LegalState.process_dsr
        else:
            self.dsr_error_message = "Invalid verification code."

    @rx.event(background=True)
    async def process_dsr(self):
        import asyncio

        async with self:
            self.dsr_status = "in_progress"
            yield rx.console_log(f"privacy.request.updated: status=in_progress")
        await asyncio.sleep(3)
        async with self:
            self.dsr_status = "completed"
            yield rx.console_log(f"privacy.request.completed: status=completed")

    @rx.event
    def generate_pdf(self, doc_name: str):
        content = f"This is a placeholder PDF for {doc_name} generated on {datetime.datetime.now()}"
        return rx.download(data=content.encode(), filename=doc_name)