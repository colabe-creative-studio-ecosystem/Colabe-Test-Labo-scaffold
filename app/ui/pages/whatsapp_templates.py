import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.whatsapp_state import WhatsAppState
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.core.models import WhatsAppTemplate


def whatsapp_templates_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    whatsapp_templates_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def whatsapp_templates_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "WhatsApp Templates",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Manage your WhatsApp message templates for outbound communication.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                rx.el.button(
                    rx.icon("plus", size=18, class_name="mr-2"),
                    "Create Template",
                    on_click=WhatsAppState.toggle_create_modal,
                    class_name="px-4 py-2 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-lg text-white font-medium hover:opacity-90 transition-opacity flex items-center justify-center",
                ),
                class_name="mb-6",
            ),
            rx.cond(
                WhatsAppState.templates.length() > 0,
                rx.el.div(
                    rx.foreach(WhatsAppState.templates, template_card),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.icon("message-circle", size=48, class_name="text-[#6366F1] mb-4"),
                        rx.el.h3(
                            "No templates yet",
                            class_name="text-lg font-semibold text-[#E8F0FF] mb-2",
                        ),
                        rx.el.p(
                            "Create your first WhatsApp template to get started.",
                            class_name="text-[#A9B3C1] mb-4",
                        ),
                        rx.el.button(
                            rx.icon("plus", size=18, class_name="mr-2"),
                            "Create Template",
                            on_click=WhatsAppState.toggle_create_modal,
                            class_name="px-4 py-2 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-lg text-white font-medium hover:opacity-90 transition-opacity flex items-center justify-center",
                        ),
                        class_name="text-center py-12",
                    ),
                    class_name=card_style,
                ),
            ),
            create_template_modal(),
            edit_template_modal(),
            class_name=page_content_style,
        ),
    )


def template_card(template: WhatsAppTemplate) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    template.name,
                    class_name="text-lg font-semibold text-[#E8F0FF] mb-2",
                ),
                rx.el.div(
                    status_badge(template.status),
                    category_badge(template.category),
                    class_name="flex gap-2 mb-3",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    template.body,
                    class_name="text-sm text-[#A9B3C1] mb-3 line-clamp-3",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("globe", size=14, class_name="text-[#A9B3C1] mr-1"),
                    rx.el.span(
                        template.language,
                        class_name="text-xs text-[#A9B3C1]",
                    ),
                    class_name="flex items-center",
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("edit", size=16),
                        on_click=lambda: WhatsAppState.open_edit_modal(template.id),
                        class_name="p-2 hover:bg-[#1A1F36] rounded transition-colors",
                    ),
                    rx.el.button(
                        rx.icon("trash-2", size=16),
                        on_click=lambda: WhatsAppState.delete_template(template.id),
                        class_name="p-2 hover:bg-[#DC2626] hover:bg-opacity-20 rounded transition-colors text-[#DC2626]",
                    ),
                    class_name="flex gap-1",
                ),
                class_name="flex justify-between items-center",
            ),
        ),
        class_name=card_style,
    )


def status_badge(status: str) -> rx.Component:
    color_map = {
        "draft": "bg-[#A9B3C1] bg-opacity-20 text-[#A9B3C1]",
        "pending_approval": "bg-[#F59E0B] bg-opacity-20 text-[#F59E0B]",
        "approved": "bg-[#10B981] bg-opacity-20 text-[#10B981]",
        "rejected": "bg-[#DC2626] bg-opacity-20 text-[#DC2626]",
    }
    return rx.el.span(
        status.replace("_", " ").title(),
        class_name=f"px-2 py-1 rounded text-xs font-medium {rx.cond(status == 'draft', color_map.get('draft', ''), rx.cond(status == 'pending_approval', color_map.get('pending_approval', ''), rx.cond(status == 'approved', color_map.get('approved', ''), color_map.get('rejected', ''))))}",
    )


def category_badge(category: str) -> rx.Component:
    return rx.el.span(
        category.title(),
        class_name="px-2 py-1 rounded text-xs font-medium bg-[#6366F1] bg-opacity-20 text-[#6366F1]",
    )


def create_template_modal() -> rx.Component:
    return rx.cond(
        WhatsAppState.is_create_modal_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Create WhatsApp Template",
                            class_name="text-xl font-bold text-[#E8F0FF] mb-2",
                        ),
                        rx.el.button(
                            rx.icon("x", size=20),
                            on_click=WhatsAppState.toggle_create_modal,
                            class_name="text-[#A9B3C1] hover:text-[#E8F0FF]",
                        ),
                        class_name="flex justify-between items-start mb-4",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.label(
                                "Template Name",
                                class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                            ),
                            rx.el.input(
                                placeholder="e.g., Welcome Message",
                                value=WhatsAppState.new_template_name,
                                on_change=WhatsAppState.set_new_template_name,
                                class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Template Body",
                                class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                            ),
                            rx.el.textarea(
                                placeholder="Use {{variable_name}} for variables, e.g., Hello {{customer_name}}, your order {{order_id}} is ready!",
                                value=WhatsAppState.new_template_body,
                                on_change=WhatsAppState.set_new_template_body,
                                rows=4,
                                class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Language",
                                    class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                                ),
                                rx.el.input(
                                    placeholder="en",
                                    value=WhatsAppState.new_template_language,
                                    on_change=WhatsAppState.set_new_template_language,
                                    class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                                ),
                                class_name="flex-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Category",
                                    class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                                ),
                                rx.el.select(
                                    rx.el.option("utility", value="utility"),
                                    rx.el.option("marketing", value="marketing"),
                                    rx.el.option("authentication", value="authentication"),
                                    value=WhatsAppState.new_template_category,
                                    on_change=WhatsAppState.set_new_template_category,
                                    class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                                ),
                                class_name="flex-1",
                            ),
                            class_name="flex gap-4 mb-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                type="button",
                                on_click=WhatsAppState.toggle_create_modal,
                                class_name="px-4 py-2 bg-[#1E293B] rounded-lg text-[#E8F0FF] font-medium hover:bg-[#334155] transition-colors",
                            ),
                            rx.el.button(
                                "Create Template",
                                type="submit",
                                on_click=WhatsAppState.create_template,
                                class_name="px-4 py-2 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-lg text-white font-medium hover:opacity-90 transition-opacity",
                            ),
                            class_name="flex justify-end gap-3",
                        ),
                        on_submit=lambda _: WhatsAppState.create_template(),
                    ),
                    class_name="bg-[#0F1629] rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto",
                ),
                on_click=lambda e: e.stop_propagation(),
                class_name="relative",
            ),
            on_click=WhatsAppState.toggle_create_modal,
            class_name="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4",
        ),
    )


def edit_template_modal() -> rx.Component:
    return rx.cond(
        WhatsAppState.is_edit_modal_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Edit WhatsApp Template",
                            class_name="text-xl font-bold text-[#E8F0FF] mb-2",
                        ),
                        rx.el.button(
                            rx.icon("x", size=20),
                            on_click=WhatsAppState.close_edit_modal,
                            class_name="text-[#A9B3C1] hover:text-[#E8F0FF]",
                        ),
                        class_name="flex justify-between items-start mb-4",
                    ),
                    rx.el.form(
                        rx.el.div(
                            rx.el.label(
                                "Template Name",
                                class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                            ),
                            rx.el.input(
                                value=WhatsAppState.editing_template_name,
                                on_change=WhatsAppState.set_editing_template_name,
                                class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Template Body",
                                class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                            ),
                            rx.el.textarea(
                                value=WhatsAppState.editing_template_body,
                                on_change=WhatsAppState.set_editing_template_body,
                                rows=4,
                                class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Language",
                                    class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                                ),
                                rx.el.input(
                                    value=WhatsAppState.editing_template_language,
                                    on_change=WhatsAppState.set_editing_template_language,
                                    class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                                ),
                                class_name="flex-1",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Category",
                                    class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                                ),
                                rx.el.select(
                                    rx.el.option("utility", value="utility"),
                                    rx.el.option("marketing", value="marketing"),
                                    rx.el.option("authentication", value="authentication"),
                                    value=WhatsAppState.editing_template_category,
                                    on_change=WhatsAppState.set_editing_template_category,
                                    class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                                ),
                                class_name="flex-1",
                            ),
                            class_name="flex gap-4 mb-4",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Status",
                                class_name="block text-sm font-medium text-[#E8F0FF] mb-2",
                            ),
                            rx.el.select(
                                rx.el.option("Draft", value="draft"),
                                rx.el.option("Pending Approval", value="pending_approval"),
                                rx.el.option("Approved", value="approved"),
                                rx.el.option("Rejected", value="rejected"),
                                value=WhatsAppState.editing_template_status,
                                on_change=WhatsAppState.set_editing_template_status,
                                class_name="w-full px-3 py-2 bg-[#0B0F1A] border border-[#1E293B] rounded-lg text-[#E8F0FF] focus:outline-none focus:ring-2 focus:ring-[#6366F1]",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.button(
                                "Cancel",
                                type="button",
                                on_click=WhatsAppState.close_edit_modal,
                                class_name="px-4 py-2 bg-[#1E293B] rounded-lg text-[#E8F0FF] font-medium hover:bg-[#334155] transition-colors",
                            ),
                            rx.el.button(
                                "Update Template",
                                type="submit",
                                on_click=WhatsAppState.update_template,
                                class_name="px-4 py-2 bg-gradient-to-r from-[#6366F1] to-[#8B5CF6] rounded-lg text-white font-medium hover:opacity-90 transition-opacity",
                            ),
                            class_name="flex justify-end gap-3",
                        ),
                        on_submit=lambda _: WhatsAppState.update_template(),
                    ),
                    class_name="bg-[#0F1629] rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto",
                ),
                on_click=lambda e: e.stop_propagation(),
                class_name="relative",
            ),
            on_click=WhatsAppState.close_edit_modal,
            class_name="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4",
        ),
    )
