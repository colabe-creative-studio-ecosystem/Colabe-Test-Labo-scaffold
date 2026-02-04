import reflex as rx
from app.ui.states.action_plan_state import ActionPlanState
from app.core.models import WhatsAppTemplate


def template_picker_button() -> rx.Component:
    """Button to open the template picker"""
    return rx.el.button(
        rx.icon("message-circle", size=18, class_name="mr-2"),
        "Add WhatsApp Action",
        on_click=ActionPlanState.open_template_picker,
        class_name="px-4 py-2 bg-gradient-to-r from-[#00D68F] to-[#00E5FF] rounded-lg text-white font-medium hover:opacity-90 transition-opacity flex items-center justify-center",
    )


def template_picker_modal() -> rx.Component:
    """Modal for selecting a WhatsApp template"""
    return rx.cond(
        ActionPlanState.is_picker_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Select WhatsApp Template",
                            class_name="text-xl font-bold text-[#E8F0FF] mb-2",
                        ),
                        rx.el.button(
                            rx.icon("x", size=20),
                            on_click=ActionPlanState.close_template_picker,
                            class_name="text-[#A9B3C1] hover:text-[#E8F0FF]",
                        ),
                        class_name="flex justify-between items-start mb-4",
                    ),
                    rx.cond(
                        ActionPlanState.templates.length() > 0,
                        rx.el.div(
                            rx.foreach(
                                ActionPlanState.templates, template_picker_card
                            ),
                            class_name="grid grid-cols-1 gap-3 max-h-96 overflow-y-auto",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "No approved templates available.",
                                class_name="text-[#A9B3C1] text-center py-8",
                            ),
                            rx.el.p(
                                "Create and approve templates in the WhatsApp Templates page first.",
                                class_name="text-[#A9B3C1] text-center text-sm",
                            ),
                        ),
                    ),
                    class_name="bg-[#0F1629] rounded-lg p-6 max-w-2xl w-full max-h-[80vh] overflow-hidden",
                ),
                on_click=lambda e: e.stop_propagation(),
                class_name="relative",
            ),
            on_click=ActionPlanState.close_template_picker,
            class_name="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4",
        ),
    )


def template_picker_card(template: WhatsAppTemplate) -> rx.Component:
    """Card for a template in the picker"""
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h4(
                    template.name,
                    class_name="text-md font-semibold text-[#E8F0FF] mb-1",
                ),
                rx.el.div(
                    rx.el.span(
                        template.category,
                        class_name="px-2 py-1 rounded text-xs font-medium bg-[#6366F1] bg-opacity-20 text-[#6366F1]",
                    ),
                    rx.el.span(
                        template.language,
                        class_name="px-2 py-1 rounded text-xs font-medium bg-[#A9B3C1] bg-opacity-20 text-[#A9B3C1]",
                    ),
                    class_name="flex gap-2 mb-2",
                ),
            ),
            rx.el.p(
                template.body,
                class_name="text-sm text-[#A9B3C1] mb-3 line-clamp-2",
            ),
            rx.el.button(
                "Use Template",
                on_click=lambda: ActionPlanState.select_template(template.id),
                class_name="px-3 py-1.5 bg-gradient-to-r from-[#00D68F] to-[#00E5FF] rounded text-white text-sm font-medium hover:opacity-90 transition-opacity",
            ),
            class_name="p-4 bg-[#0B0F1A] border border-[#1E293B] rounded-lg hover:border-[#6366F1] transition-colors cursor-pointer",
        ),
    )


def variable_composer_modal() -> rx.Component:
    """Modal for composing variables for the selected template"""
    return rx.cond(
        ActionPlanState.is_composer_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Configure Action Plan",
                            class_name="text-xl font-bold text-[#E8F0FF] mb-2",
                        ),
                        rx.el.button(
                            rx.icon("x", size=20),
                            on_click=ActionPlanState.close_composer,
                            class_name="text-[#A9B3C1] hover:text-[#E8F0FF]",
                        ),
                        class_name="flex justify-between items-start mb-4",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.label(
                                "Action Name",
                                class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                            ),
                            rx.el.input(
                                placeholder="e.g., Send Welcome Message",
                                value=ActionPlanState.current_action_name,
                                on_change=ActionPlanState.set_action_name,
                                class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Template Variables",
                                class_name="text-md font-semibold text-[#E8F0FF] mb-3",
                            ),
                            rx.cond(
                                ActionPlanState.selected_template_variables.length()
                                > 0,
                                rx.el.div(
                                    rx.foreach(
                                        ActionPlanState.selected_template_variables.items(),
                                        variable_input_field,
                                    ),
                                    class_name="space-y-3 mb-4",
                                ),
                                rx.el.p(
                                    "This template has no variables.",
                                    class_name="text-[#A9B3C1] text-sm mb-4",
                                ),
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Preview",
                                class_name="text-md font-semibold text-[#E8F0FF] mb-2",
                            ),
                            rx.el.div(
                                rx.el.p(
                                    ActionPlanState.get_template_preview(),
                                    class_name="text-sm text-[#E8F0FF]",
                                ),
                                class_name="p-3 bg-[#0B0F1A] border border-[#1E293B] rounded-lg mb-4 min-h-[80px]",
                            ),
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                type="button",
                                on_click=ActionPlanState.close_composer,
                                class_name="px-4 py-2 bg-[#1E293B] rounded-lg text-[#E8F0FF] font-medium hover:bg-[#334155] transition-colors",
                            ),
                            rx.el.button(
                                "Create Action",
                                type="submit",
                                class_name="px-4 py-2 bg-gradient-to-r from-[#00D68F] to-[#00E5FF] rounded-lg text-white font-medium hover:opacity-90 transition-opacity",
                            ),
                            class_name="flex justify-end gap-3",
                        ),
                    ),
                    class_name="bg-[#0F1629] rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto",
                ),
                on_click=lambda e: e.stop_propagation(),
                class_name="relative",
            ),
            on_click=ActionPlanState.close_composer,
            class_name="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4",
        ),
    )


def variable_input_field(var_item: tuple) -> rx.Component:
    """Input field for a single template variable"""
    var_name, var_value = var_item
    return rx.el.div(
        rx.el.label(
            var_name,
            class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
        ),
        rx.el.input(
            placeholder=f"Enter {var_name}",
            value=var_value,
            on_change=lambda val, name=var_name: ActionPlanState.set_variable_value(name, val),
            class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
        ),
    )


def action_plan_list(project_id: int) -> rx.Component:
    """Component to display action plans for a project"""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Action Plans",
                class_name="text-lg font-semibold text-[#E8F0FF] mb-3",
            ),
            template_picker_button(),
            class_name="flex justify-between items-center mb-4",
        ),
        rx.cond(
            ActionPlanState.action_plans.length() > 0,
            rx.el.div(
                rx.foreach(ActionPlanState.action_plans, action_plan_card),
                class_name="space-y-3",
            ),
            rx.el.div(
                rx.el.p(
                    "No action plans configured yet.",
                    class_name="text-[#A9B3C1] text-center py-4",
                ),
            ),
        ),
        template_picker_modal(),
        variable_composer_modal(),
    )


def action_plan_card(action: rx.Var) -> rx.Component:
    """Card displaying a single action plan"""
    return rx.el.div(
        rx.el.div(
            rx.el.h4(
                action.name,
                class_name="text-md font-semibold text-[#E8F0FF] mb-1",
            ),
            rx.el.div(
                rx.el.span(
                    action.kind,
                    class_name="px-2 py-1 rounded text-xs font-medium bg-[#00D68F] bg-opacity-20 text-[#00D68F]",
                ),
                class_name="flex gap-2",
            ),
        ),
        class_name="p-4 bg-[#0B0F1A] border border-[#1E293B] rounded-lg",
    )
