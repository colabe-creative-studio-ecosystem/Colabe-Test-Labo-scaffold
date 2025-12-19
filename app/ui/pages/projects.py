import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.project_state import ProjectState
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.core.models import Project


def projects_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    projects_page_content(),
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


def projects_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Projects",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Manage your test automation projects and configurations.",
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
                    "New Project",
                    on_click=ProjectState.toggle_create_modal,
                    class_name="flex items-center px-4 py-2 bg-[#00E5FF] text-[#0A0F14] font-semibold rounded-lg hover:opacity-90 transition-opacity",
                ),
                class_name="mb-8 flex justify-end",
            ),
            rx.cond(
                ProjectState.projects.length() > 0,
                rx.el.div(
                    rx.foreach(ProjectState.projects, project_card),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                ),
                empty_projects_state(),
            ),
            class_name="p-8 flex-1",
        ),
        create_project_modal(),
        class_name=page_content_style,
    )


def project_card(project: Project) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("folder-kanban", size=24, class_name="text-[#D8B76E]"),
                class_name="p-3 rounded-lg bg-[#0A0F14] border border-white/5",
            ),
            rx.el.button(
                rx.icon("trash-2", size=18),
                on_click=ProjectState.delete_project(project.id),
                class_name="text-gray-500 hover:text-[#FF3B3B] transition-colors p-2",
            ),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.h3(
            project.name, class_name="text-xl font-bold text-[#E8F0FF] mb-2 truncate"
        ),
        rx.el.div(
            rx.el.p(
                "Created on",
                class_name="text-xs text-[#A9B3C1] uppercase tracking-wider",
            ),
            rx.el.p(
                project.created_at.to_string(),
                class_name="text-sm text-[#E8F0FF] font-medium",
            ),
            class_name="mt-4 pt-4 border-t border-white/5",
        ),
        rx.el.div(
            rx.el.a(
                "View Details",
                rx.icon("arrow-right", size=16, class_name="ml-2"),
                href="#",
                class_name="flex items-center text-sm font-semibold text-[#00E5FF] hover:underline",
            ),
            class_name="mt-4 flex justify-end",
        ),
        **card_style("cyan"),
    )


def empty_projects_state() -> rx.Component:
    return rx.el.div(
        rx.icon("folder-open", size=48, class_name="text-[#A9B3C1] opacity-50 mb-4"),
        rx.el.h3("No Projects Yet", class_name="text-xl font-semibold text-[#E8F0FF]"),
        rx.el.p(
            "Get started by creating your first project to organize your tests.",
            class_name="text-[#A9B3C1] mt-2 max-w-sm",
        ),
        rx.el.button(
            "Create Project",
            on_click=ProjectState.toggle_create_modal,
            class_name="mt-6 px-6 py-2 border border-[#00E5FF] text-[#00E5FF] rounded-lg hover:bg-[#00E5FF] hover:text-[#0A0F14] transition-all",
        ),
        class_name="flex flex-col items-center justify-center py-20 text-center rounded-2xl border-2 border-dashed border-white/10 bg-[#0E1520]/50",
    )


def create_project_modal() -> rx.Component:
    return rx.cond(
        ProjectState.is_create_modal_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2(
                        "Create New Project",
                        class_name="text-xl font-bold text-[#E8F0FF]",
                    ),
                    rx.el.button(
                        rx.icon("x", size=24),
                        on_click=ProjectState.toggle_create_modal,
                        class_name="text-[#A9B3C1] hover:text-[#E8F0FF]",
                    ),
                    class_name="flex justify-between items-center mb-6",
                ),
                rx.el.div(
                    rx.el.label(
                        "Project Name",
                        class_name="block text-sm font-medium text-[#A9B3C1] mb-2",
                    ),
                    rx.el.input(
                        placeholder="e.g., E-commerce Frontend",
                        on_change=ProjectState.set_new_project_name,
                        class_name="w-full px-4 py-3 bg-[#0A0F14] border border-white/10 rounded-lg text-[#E8F0FF] placeholder-gray-600 focus:outline-none focus:border-[#00E5FF] focus:ring-1 focus:ring-[#00E5FF] transition-all",
                        auto_focus=True,
                        default_value=ProjectState.new_project_name,
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=ProjectState.toggle_create_modal,
                        class_name="px-4 py-2 text-[#A9B3C1] hover:text-[#E8F0FF] font-medium mr-4 transition-colors",
                    ),
                    rx.el.button(
                        "Create Project",
                        on_click=ProjectState.create_project,
                        class_name="px-6 py-2 bg-[#00E5FF] text-[#0A0F14] font-bold rounded-lg hover:opacity-90 transition-opacity",
                    ),
                    class_name="flex justify-end items-center",
                ),
                class_name="bg-[#0E1520] p-8 rounded-2xl shadow-2xl border border-white/10 w-full max-w-md relative z-50",
            ),
            class_name="fixed inset-0 z-40 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4",
        ),
    )