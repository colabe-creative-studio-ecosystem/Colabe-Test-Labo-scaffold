import reflex as rx
from app.ui.states.support_state import SupportState
from app.ui.pages.index import sidebar
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.core.models import (
    Ticket,
    Runbook,
    SLAPolicy,
    TicketStatus,
    TicketSeverity,
    TicketMessage,
    TicketAuthorType,
)


def support_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            SupportState.is_logged_in,
            rx.el.div(sidebar(), support_page_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=SupportState.on_support_page_load,
    )


def support_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Support Center",
                    class_name="text-2xl font-bold text-text-primary title-gradient",
                ),
                rx.el.p(
                    "Manage tickets, view SLAs, and access runbooks.",
                    class_name="text-text-secondary",
                ),
            ),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                tab_button("My Tickets", "tickets", "ticket"),
                tab_button("New Ticket", "new", "circle_plus"),
                tab_button("Runbooks", "runbooks", "notebook-text"),
                tab_button("SLAs", "slas", "timer"),
                class_name="flex border-b border-white/10 px-8",
            ),
            rx.el.div(
                rx.match(
                    SupportState.active_tab,
                    ("tickets", tickets_list()),
                    ("new", new_ticket_form()),
                    ("runbooks", runbooks_list()),
                    ("slas", slas_list()),
                    rx.el.div("Select a tab"),
                ),
                class_name="p-8",
            ),
            class_name="flex-grow",
        ),
        class_name=page_content_style,
    )


def tab_button(text: str, tab_name: str, icon: str) -> rx.Component:
    return rx.el.button(
        rx.icon(icon, size=16, class_name="mr-2"),
        text,
        on_click=SupportState.set_active_tab(tab_name),
        class_name=rx.cond(
            SupportState.active_tab == tab_name,
            "px-4 py-3 font-semibold text-accent-cyan border-b-2 border-accent-cyan flex items-center",
            "px-4 py-3 font-semibold text-text-secondary flex items-center",
        ),
    )


def tickets_list() -> rx.Component:
    return rx.el.div(
        rx.el.h2("My Tickets", class_name="text-xl font-semibold text-text-primary"),
        rx.el.div(
            rx.foreach(SupportState.tickets, render_ticket_item),
            class_name="mt-4 space-y-3",
        ),
        class_name="w-full",
    )


def render_ticket_item(ticket: Ticket) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.p(f"#{ticket.id}", class_name="text-text-secondary"),
            rx.el.p(ticket.subject, class_name="font-semibold text-text-primary"),
            class_name="flex-grow",
        ),
        rx.el.div(
            status_badge(ticket.status),
            rx.el.p(
                ticket.opened_at.to_string(), class_name="text-sm text-text-secondary"
            ),
            class_name="flex items-center space-x-4",
        ),
        href=f"/support/tickets/{ticket.id}",
        class_name="flex items-center justify-between p-4 rounded-lg bg-bg-elevated hover:bg-white/5",
    )


def status_badge(status: rx.Var[TicketStatus]) -> rx.Component:
    color_map = {
        "new": "cyan",
        "triaged": "blue",
        "in_progress": "yellow",
        "waiting_on_customer": "purple",
        "resolved": "green",
        "closed": "gray",
    }
    return rx.el.span(
        status.to_string().replace("_", " ").capitalize(),
        class_name=f"px-2 py-1 text-xs font-medium rounded-full bg-{rx.match(status, *[(s, c) for s, c in color_map.items()], 'gray')}-500/20 text-{rx.match(status, *[(s, c) for s, c in color_map.items()], 'gray')}-300",
    )


def new_ticket_form() -> rx.Component:
    return rx.el.form(
        rx.el.h2(
            "Create New Ticket",
            class_name="text-xl font-semibold text-text-primary mb-4",
        ),
        rx.el.div(
            rx.el.label("Subject", class_name="text-sm font-medium"),
            rx.el.input(
                name="subject",
                placeholder="e.g., Build pipeline failing",
                class_name="w-full mt-1 p-2 rounded-md bg-bg-base border border-white/20",
            ),
            class_name="space-y-1",
        ),
        rx.el.div(
            rx.el.label("Severity", class_name="text-sm font-medium"),
            rx.el.select(
                rx.foreach(SupportState.severities, lambda s: rx.el.option(s, value=s)),
                name="severity",
                default_value=TicketSeverity.SEV4.value,
                class_name="w-full mt-1 p-2 rounded-md bg-bg-base border border-white/20",
            ),
            class_name="space-y-1",
        ),
        rx.el.div(
            rx.el.label("Description", class_name="text-sm font-medium"),
            rx.el.textarea(
                name="body",
                placeholder="Please provide a detailed description of the issue.",
                rows=6,
                class_name="w-full mt-1 p-2 rounded-md bg-bg-base border border-white/20",
            ),
            class_name="space-y-1",
        ),
        rx.el.button(
            "Submit Ticket",
            type="submit",
            class_name="mt-4 px-4 py-2 bg-accent-cyan text-bg-base font-semibold rounded-lg hover:opacity-90",
        ),
        on_submit=SupportState.create_ticket,
        class_name="max-w-2xl space-y-4",
    )


def runbooks_list() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Runbooks", class_name="text-xl font-semibold text-text-primary"),
        rx.el.div(
            rx.foreach(SupportState.runbooks, render_runbook_item),
            class_name="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4",
        ),
    )


def render_runbook_item(runbook: Runbook) -> rx.Component:
    return rx.el.div(
        rx.el.h3(runbook.title, class_name="font-semibold text-text-primary"),
        rx.el.p(
            f"Severity: {runbook.severity_scope.to_string()}",
            class_name="text-sm text-text-secondary",
        ),
        rx.el.div(
            rx.markdown(runbook.steps_mdx),
            class_name="mt-2 text-sm prose prose-invert prose-sm",
        ),
        **card_style("magenta"),
    )


def slas_list() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Service Level Agreements (SLAs)",
            class_name="text-xl font-semibold text-text-primary",
        ),
        rx.el.div(
            rx.foreach(SupportState.sla_policies, render_sla_item),
            class_name="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4",
        ),
    )


def render_sla_item(sla: SLAPolicy) -> rx.Component:
    return rx.el.div(
        rx.el.h3(sla.name, class_name="font-semibold text-text-primary"),
        rx.el.div(
            rx.el.p("Plan:", class_name="text-text-secondary"),
            rx.el.p(sla.plan),
            rx.el.p("Severity:", class_name="text-text-secondary"),
            rx.el.p(sla.severity),
            rx.el.p("First Response:", class_name="text-text-secondary"),
            rx.el.p(f"{sla.first_response_target_min} min"),
            rx.el.p("Resolution:", class_name="text-text-secondary"),
            rx.el.p(f"{sla.resolution_target_min / 60} hours"),
            class_name="mt-2 grid grid-cols-2 gap-x-4 gap-y-1 text-sm",
        ),
        **card_style("gold"),
    )


def support_ticket_detail_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            SupportState.is_logged_in,
            rx.el.div(sidebar(), ticket_detail_content(), class_name=page_style),
            rx.el.div(
                rx.el.p("Loading..."),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        ),
        on_mount=SupportState.on_ticket_detail_load,
    )


def ticket_detail_content() -> rx.Component:
    return rx.el.main(
        rx.el.a(
            rx.icon("arrow-left", class_name="mr-2"),
            "Back to all tickets",
            href="/support",
            class_name="flex items-center text-text-secondary hover:text-text-primary mb-4 p-8",
        ),
        rx.cond(
            SupportState.selected_ticket,
            rx.el.div(
                rx.el.header(
                    rx.el.div(
                        rx.el.h1(
                            SupportState.selected_ticket.subject,
                            class_name="text-2xl font-bold text-text-primary",
                        ),
                        rx.el.p(
                            f"Ticket #{SupportState.selected_ticket.id} opened on {SupportState.selected_ticket.opened_at.to_string()}",
                            class_name="text-text-secondary",
                        ),
                    ),
                    rx.el.div(
                        status_badge(SupportState.selected_ticket.status),
                        rx.cond(
                            SupportState.selected_ticket.status != "closed",
                            rx.el.div(
                                rx.el.button(
                                    "Resolve",
                                    on_click=lambda: SupportState.update_ticket_status(
                                        SupportState.selected_ticket.id, "resolved"
                                    ),
                                    class_name="px-3 py-1 bg-green-500/20 text-green-300 rounded-md text-sm",
                                ),
                                rx.el.button(
                                    "Close",
                                    on_click=lambda: SupportState.update_ticket_status(
                                        SupportState.selected_ticket.id, "closed"
                                    ),
                                    class_name="px-3 py-1 bg-gray-500/20 text-gray-300 rounded-md text-sm",
                                ),
                                class_name="flex items-center gap-2 mt-2",
                            ),
                        ),
                        class_name="flex flex-col items-end",
                    ),
                    class_name="flex items-start justify-between px-8",
                ),
                rx.el.div(
                    rx.foreach(SupportState.selected_ticket.messages, render_message),
                    class_name="space-y-6 p-8",
                ),
            ),
            rx.el.div("Ticket not found or you don't have access.", class_name="p-8"),
        ),
        class_name=page_content_style,
    )


def render_message(message: TicketMessage) -> rx.Component:
    is_agent = message.author_type == TicketAuthorType.AGENT
    return rx.el.div(
        rx.el.div(
            rx.image(
                src=rx.cond(
                    is_agent,
                    "https://api.dicebear.com/9.x/notionists/svg?seed=Agent",
                    f"https://api.dicebear.com/9.x/initials/svg?seed={SupportState.user.username}",
                ),
                class_name="h-8 w-8 rounded-full",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        rx.cond(is_agent, "Support Agent", SupportState.user.username),
                        class_name="font-semibold",
                    ),
                    rx.el.p(
                        message.created_at.to_string(),
                        class_name="text-xs text-text-secondary",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.div(
                    rx.markdown(message.body_markdown),
                    class_name="prose prose-invert prose-sm mt-1",
                ),
                class_name=rx.cond(
                    is_agent,
                    "p-3 rounded-lg bg-bg-elevated",
                    "p-3 rounded-lg bg-accent-cyan/10",
                ),
            ),
            class_name="flex items-start gap-3",
        ),
        class_name="w-full",
    )