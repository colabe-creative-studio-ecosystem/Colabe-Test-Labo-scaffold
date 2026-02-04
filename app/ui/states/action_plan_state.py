import reflex as rx
from app.core.models import WhatsAppTemplate, ActionPlan, ActionKindEnum
import json
import logging

logger = logging.getLogger(__name__)


class ActionPlanState(rx.State):
    """State for managing action plans with template selection"""

    action_plans: list[ActionPlan] = []
    templates: list[WhatsAppTemplate] = []
    selected_template_id: int = 0
    selected_template_variables: dict[str, str] = {}
    is_picker_open: bool = False
    is_composer_open: bool = False
    current_action_name: str = ""

    @rx.event
    async def load_action_plans(self, project_id: int):
        """Load action plans for a specific project"""
        with rx.session() as session:
            import sqlmodel

            self.action_plans = session.exec(
                sqlmodel.select(ActionPlan)
                .where(ActionPlan.project_id == project_id)
                .order_by(sqlmodel.desc(ActionPlan.created_at))
            ).all()

    @rx.event
    async def load_templates_for_picker(self):
        """Load available WhatsApp templates"""
        from app.ui.states.auth_state import AuthState

        auth_state = await self.get_state(AuthState)
        if not auth_state.user:
            return

        with rx.session() as session:
            import sqlmodel

            self.templates = session.exec(
                sqlmodel.select(WhatsAppTemplate)
                .where(WhatsAppTemplate.workspace_id == auth_state.user.tenant_id)
                .where(WhatsAppTemplate.status == "approved")
                .order_by(sqlmodel.desc(WhatsAppTemplate.created_at))
            ).all()

    @rx.event
    def open_template_picker(self):
        """Open the template picker modal"""
        self.is_picker_open = True
        return self.load_templates_for_picker()

    @rx.event
    def close_template_picker(self):
        """Close the template picker modal"""
        self.is_picker_open = False

    @rx.event
    def select_template(self, template_id: int):
        """Select a template and open the composer"""
        self.selected_template_id = template_id
        # Load template to extract variables
        with rx.session() as session:
            template = session.get(WhatsAppTemplate, template_id)
            if template:
                variables = json.loads(template.variables_json)
                # Initialize variable values
                self.selected_template_variables = {var: "" for var in variables}
        self.is_picker_open = False
        self.is_composer_open = True

    @rx.event
    def set_action_name(self, name: str):
        self.current_action_name = name

    @rx.event
    def set_variable_value(self, var_name: str, value: str):
        """Set the value for a template variable"""
        self.selected_template_variables[var_name] = value

    @rx.event
    def close_composer(self):
        """Close the variable composer"""
        self.is_composer_open = False
        self.selected_template_id = 0
        self.selected_template_variables = {}
        self.current_action_name = ""

    @rx.event
    async def create_action_plan(self, project_id: int):
        """Create an action plan with the configured template"""
        if not self.current_action_name.strip():
            return rx.toast("Action name is required", duration=3000)

        if not self.selected_template_id:
            return rx.toast("Please select a template", duration=3000)

        try:
            config = {
                "variables": self.selected_template_variables,
                "type": "whatsapp_template",
            }

            with rx.session() as session:
                new_action = ActionPlan(
                    project_id=project_id,
                    name=self.current_action_name,
                    kind=ActionKindEnum.ACTION_SEND_TEMPLATE,
                    template_id=self.selected_template_id,
                    config_json=json.dumps(config),
                )
                session.add(new_action)
                session.commit()

            await self.load_action_plans(project_id)
            self.close_composer()
            return rx.toast("Action plan created successfully!", duration=3000)
        except Exception as e:
            logger.exception(f"Error creating action plan: {e}")
            return rx.toast(f"Error creating action plan: {str(e)}", duration=3000)

    def get_template_preview(self) -> str:
        """Get preview of template with variable substitution"""
        if not self.selected_template_id:
            return ""

        with rx.session() as session:
            template = session.get(WhatsAppTemplate, self.selected_template_id)
            if template:
                body = template.body
                for var_name, var_value in self.selected_template_variables.items():
                    body = body.replace(
                        f"{{{{{var_name}}}}}", var_value or f"[{var_name}]"
                    )
                return body
        return ""
