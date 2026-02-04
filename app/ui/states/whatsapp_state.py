import reflex as rx
import sqlmodel
import logging
import json
import re
from app.core.models import (
    WhatsAppTemplate,
    TemplateStatusEnum,
    TemplateCategoryEnum,
    ActionPlan,
    ActionKindEnum,
)
from app.ui.states.auth_state import AuthState

logger = logging.getLogger(__name__)


class WhatsAppState(rx.State):
    templates: list[WhatsAppTemplate] = []
    new_template_name: str = ""
    new_template_body: str = ""
    new_template_language: str = "en"
    new_template_category: str = "utility"
    is_create_modal_open: bool = False
    is_edit_modal_open: bool = False
    editing_template_id: int = 0
    editing_template_name: str = ""
    editing_template_body: str = ""
    editing_template_language: str = "en"
    editing_template_category: str = "utility"
    editing_template_status: str = "draft"
    preview_template_body: str = ""
    preview_variables: dict[str, str] = {}

    @rx.event
    async def load_templates(self):
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        with rx.session() as session:
            self.templates = session.exec(
                sqlmodel.select(WhatsAppTemplate)
                .where(WhatsAppTemplate.workspace_id == auth_state.user.tenant_id)
                .order_by(sqlmodel.desc(WhatsAppTemplate.created_at))
            ).all()

    @rx.event
    def set_new_template_name(self, name: str):
        self.new_template_name = name

    @rx.event
    def set_new_template_body(self, body: str):
        self.new_template_body = body
        self._extract_variables_preview(body)

    @rx.event
    def set_new_template_language(self, language: str):
        self.new_template_language = language

    @rx.event
    def set_new_template_category(self, category: str):
        self.new_template_category = category

    @rx.event
    def toggle_create_modal(self):
        self.is_create_modal_open = not self.is_create_modal_open
        if not self.is_create_modal_open:
            self.new_template_name = ""
            self.new_template_body = ""
            self.new_template_language = "en"
            self.new_template_category = "utility"
            self.preview_variables = {}

    @rx.event
    async def create_template(self):
        if not self.new_template_name.strip():
            return rx.toast("Template name is required.", duration=3000)
        if not self.new_template_body.strip():
            return rx.toast("Template body is required.", duration=3000)
        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return
        try:
            # Extract variables from template body
            variables = self._extract_variables(self.new_template_body)

            with rx.session() as session:
                new_template = WhatsAppTemplate(
                    workspace_id=auth_state.user.tenant_id,
                    name=self.new_template_name,
                    body=self.new_template_body,
                    language=self.new_template_language,
                    category=TemplateCategoryEnum(self.new_template_category),
                    variables_json=json.dumps(variables),
                    status=TemplateStatusEnum.DRAFT,
                )
                session.add(new_template)
                session.commit()
            await self.load_templates()
            self.toggle_create_modal()
            return rx.toast("Template created successfully!", duration=3000)
        except Exception as e:
            logger.exception(f"Error creating template: {e}")
            return rx.toast(f"Error creating template: {str(e)}", duration=3000)

    @rx.event
    async def open_edit_modal(self, template_id: int):
        with rx.session() as session:
            template = session.get(WhatsAppTemplate, template_id)
            if template:
                self.editing_template_id = template.id
                self.editing_template_name = template.name
                self.editing_template_body = template.body
                self.editing_template_language = template.language
                self.editing_template_category = template.category
                self.editing_template_status = template.status
                self.is_edit_modal_open = True
                self._extract_variables_preview(template.body)

    @rx.event
    def close_edit_modal(self):
        self.is_edit_modal_open = False
        self.editing_template_id = 0
        self.editing_template_name = ""
        self.editing_template_body = ""
        self.editing_template_language = "en"
        self.editing_template_category = "utility"
        self.editing_template_status = "draft"
        self.preview_variables = {}

    @rx.event
    def set_editing_template_name(self, name: str):
        self.editing_template_name = name

    @rx.event
    def set_editing_template_body(self, body: str):
        self.editing_template_body = body
        self._extract_variables_preview(body)

    @rx.event
    def set_editing_template_language(self, language: str):
        self.editing_template_language = language

    @rx.event
    def set_editing_template_category(self, category: str):
        self.editing_template_category = category

    @rx.event
    def set_editing_template_status(self, status: str):
        self.editing_template_status = status

    @rx.event
    async def update_template(self):
        if not self.editing_template_name.strip():
            return rx.toast("Template name is required.", duration=3000)
        if not self.editing_template_body.strip():
            return rx.toast("Template body is required.", duration=3000)
        try:
            variables = self._extract_variables(self.editing_template_body)
            with rx.session() as session:
                template = session.get(WhatsAppTemplate, self.editing_template_id)
                if template:
                    template.name = self.editing_template_name
                    template.body = self.editing_template_body
                    template.language = self.editing_template_language
                    template.category = TemplateCategoryEnum(
                        self.editing_template_category
                    )
                    template.status = TemplateStatusEnum(self.editing_template_status)
                    template.variables_json = json.dumps(variables)
                    session.add(template)
                    session.commit()
            await self.load_templates()
            self.close_edit_modal()
            return rx.toast("Template updated successfully!", duration=3000)
        except Exception as e:
            logger.exception(f"Error updating template: {e}")
            return rx.toast(f"Error updating template: {str(e)}", duration=3000)

    @rx.event
    async def delete_template(self, template_id: int):
        try:
            with rx.session() as session:
                template = session.get(WhatsAppTemplate, template_id)
                if template:
                    session.delete(template)
                    session.commit()
            await self.load_templates()
            return rx.toast("Template deleted.", duration=3000)
        except Exception as e:
            logger.exception(f"Error deleting template {template_id}: {e}")
            return rx.toast(
                "Cannot delete template. It may be in use by action plans.",
                duration=5000,
            )

    @rx.event
    def set_preview_variable(self, var_name: str, value: str):
        self.preview_variables[var_name] = value

    def _extract_variables(self, body: str) -> list[str]:
        """Extract variable placeholders from template body like {{variable_name}}"""
        pattern = r"\{\{(\w+)\}\}"
        matches = re.findall(pattern, body)
        return list(set(matches))

    def _extract_variables_preview(self, body: str):
        """Extract variables and setup preview dict"""
        variables = self._extract_variables(body)
        # Initialize preview variables if not already set
        for var in variables:
            if var not in self.preview_variables:
                self.preview_variables[var] = ""

    def get_preview_text(self) -> str:
        """Get template body with variables replaced by preview values"""
        body = self.editing_template_body or self.new_template_body
        result = body
        for var_name, var_value in self.preview_variables.items():
            result = result.replace(f"{{{{{var_name}}}}}", var_value or f"[{var_name}]")
        return result
