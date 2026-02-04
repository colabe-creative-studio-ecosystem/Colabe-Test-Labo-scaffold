"""Outbound messaging monitoring dashboard page."""
import reflex as rx
from app.ui.components.footer import footer
from app.ui.components.sidebar import sidebar
from app.ui.states.auth_state import AuthState
from app.ui.states.outbound_messaging_state import (
    OutboundMessagingState,
    OutboundMessageDisplay,
)
from app.ui.styles import page_style, page_content_style, header_style


def circuit_breaker_widget() -> rx.Component:
    """Widget showing circuit breaker status."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Circuit Breaker Status",
                class_name="text-lg font-semibold text-[#E8F0FF] mb-4",
            ),
            rx.cond(
                OutboundMessagingState.circuit_breaker,
                rx.el.div(
                    # State indicator
                    rx.el.div(
                        rx.el.span(
                            "State: ",
                            class_name="text-[#A9B3C1]",
                        ),
                        rx.cond(
                            OutboundMessagingState.circuit_breaker.state == "closed",
                            rx.el.span(
                                "CLOSED ✓",
                                class_name="text-green-400 font-bold",
                            ),
                            rx.cond(
                                OutboundMessagingState.circuit_breaker.state == "open",
                                rx.el.span(
                                    "OPEN ⚠",
                                    class_name="text-red-400 font-bold",
                                ),
                                rx.el.span(
                                    "HALF_OPEN ⟳",
                                    class_name="text-yellow-400 font-bold",
                                ),
                            ),
                        ),
                        class_name="mb-2",
                    ),
                    # Failure count
                    rx.el.div(
                        rx.el.span(
                            "Failures in window: ",
                            class_name="text-[#A9B3C1]",
                        ),
                        rx.el.span(
                            OutboundMessagingState.circuit_breaker.failure_count,
                            class_name="text-[#E8F0FF] font-semibold",
                        ),
                        class_name="mb-2",
                    ),
                    # Last failure
                    rx.cond(
                        OutboundMessagingState.circuit_breaker.last_failure_at,
                        rx.el.div(
                            rx.el.span(
                                "Last failure: ",
                                class_name="text-[#A9B3C1]",
                            ),
                            rx.el.span(
                                OutboundMessagingState.circuit_breaker.last_failure_at,
                                class_name="text-[#E8F0FF]",
                            ),
                            class_name="mb-2",
                        ),
                    ),
                    # Reset button (only show if open)
                    rx.cond(
                        OutboundMessagingState.circuit_breaker.state == "open",
                        rx.el.button(
                            "Reset Circuit Breaker",
                            on_click=OutboundMessagingState.reset_circuit_breaker,
                            class_name="mt-4 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-semibold transition-colors",
                        ),
                    ),
                ),
                rx.el.p(
                    "No circuit breaker data available",
                    class_name="text-[#A9B3C1]",
                ),
            ),
        ),
        class_name="glass-panel p-6 rounded-lg border border-[#2A3441]",
    )


def quiet_hours_widget() -> rx.Component:
    """Widget for configuring quiet hours."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Quiet Hours Configuration",
                class_name="text-lg font-semibold text-[#E8F0FF] mb-4",
            ),
            rx.el.form(
                # Enabled toggle
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=OutboundMessagingState.quiet_hours_enabled,
                            on_change=OutboundMessagingState.set_quiet_hours_enabled,
                            class_name="mr-2",
                        ),
                        "Enable Quiet Hours",
                        class_name="text-[#E8F0FF] flex items-center",
                    ),
                    class_name="mb-4",
                ),
                # Start hour
                rx.el.div(
                    rx.el.label(
                        "Start Hour (24h format)",
                        class_name="block text-[#A9B3C1] mb-2",
                    ),
                    rx.el.input(
                        type="number",
                        min="0",
                        max="23",
                        value=OutboundMessagingState.quiet_hours_start,
                        on_change=OutboundMessagingState.set_quiet_hours_start,
                        class_name="w-full px-3 py-2 bg-[#1A2332] border border-[#2A3441] rounded-lg text-[#E8F0FF]",
                    ),
                    class_name="mb-4",
                ),
                # End hour
                rx.el.div(
                    rx.el.label(
                        "End Hour (24h format)",
                        class_name="block text-[#A9B3C1] mb-2",
                    ),
                    rx.el.input(
                        type="number",
                        min="0",
                        max="23",
                        value=OutboundMessagingState.quiet_hours_end,
                        on_change=OutboundMessagingState.set_quiet_hours_end,
                        class_name="w-full px-3 py-2 bg-[#1A2332] border border-[#2A3441] rounded-lg text-[#E8F0FF]",
                    ),
                    class_name="mb-4",
                ),
                # Timezone
                rx.el.div(
                    rx.el.label(
                        "Timezone",
                        class_name="block text-[#A9B3C1] mb-2",
                    ),
                    rx.el.input(
                        type="text",
                        value=OutboundMessagingState.quiet_hours_timezone,
                        on_change=OutboundMessagingState.set_quiet_hours_timezone,
                        placeholder="UTC",
                        class_name="w-full px-3 py-2 bg-[#1A2332] border border-[#2A3441] rounded-lg text-[#E8F0FF]",
                    ),
                    class_name="mb-4",
                ),
                # Save button
                rx.el.button(
                    "Save Configuration",
                    on_click=OutboundMessagingState.update_quiet_hours,
                    type="button",
                    class_name="px-4 py-2 bg-[#0066FF] hover:bg-[#0052CC] text-white rounded-lg font-semibold transition-colors",
                ),
            ),
        ),
        class_name="glass-panel p-6 rounded-lg border border-[#2A3441]",
    )


def statistics_cards() -> rx.Component:
    """Statistics cards showing today's metrics."""
    return rx.el.div(
        # Sent messages
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "✓",
                        class_name="text-3xl",
                    ),
                    class_name="text-green-400 mb-2",
                ),
                rx.el.div(
                    OutboundMessagingState.total_sent_today,
                    class_name="text-3xl font-bold text-[#E8F0FF] mb-1",
                ),
                rx.el.div(
                    "Messages Sent Today",
                    class_name="text-[#A9B3C1] text-sm",
                ),
            ),
            class_name="glass-panel p-6 rounded-lg border border-[#2A3441] text-center",
        ),
        # Failed messages
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "✗",
                        class_name="text-3xl",
                    ),
                    class_name="text-red-400 mb-2",
                ),
                rx.el.div(
                    OutboundMessagingState.total_failed_today,
                    class_name="text-3xl font-bold text-[#E8F0FF] mb-1",
                ),
                rx.el.div(
                    "Messages Failed Today",
                    class_name="text-[#A9B3C1] text-sm",
                ),
            ),
            class_name="glass-panel p-6 rounded-lg border border-[#2A3441] text-center",
        ),
        # Blocked messages
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "⊝",
                        class_name="text-3xl",
                    ),
                    class_name="text-yellow-400 mb-2",
                ),
                rx.el.div(
                    OutboundMessagingState.total_blocked_today,
                    class_name="text-3xl font-bold text-[#E8F0FF] mb-1",
                ),
                rx.el.div(
                    "Messages Blocked Today",
                    class_name="text-[#A9B3C1] text-sm",
                ),
            ),
            class_name="glass-panel p-6 rounded-lg border border-[#2A3441] text-center",
        ),
        class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6",
    )


def message_log_table() -> rx.Component:
    """Table showing recent outbound messages."""
    return rx.el.div(
        rx.el.div(
            rx.el.h3(
                "Recent Outbound Messages",
                class_name="text-lg font-semibold text-[#E8F0FF] mb-4",
            ),
            # Status filter buttons
            rx.el.div(
                rx.el.button(
                    "All",
                    on_click=lambda: OutboundMessagingState.change_status_filter("all"),
                    class_name="px-3 py-1 mr-2 rounded-lg transition-colors "
                    + rx.cond(
                        OutboundMessagingState.show_status_filter == "all",
                        "bg-[#0066FF] text-white",
                        "bg-[#1A2332] text-[#A9B3C1] hover:bg-[#2A3441]",
                    ),
                ),
                rx.el.button(
                    "Sent",
                    on_click=lambda: OutboundMessagingState.change_status_filter("sent"),
                    class_name="px-3 py-1 mr-2 rounded-lg transition-colors "
                    + rx.cond(
                        OutboundMessagingState.show_status_filter == "sent",
                        "bg-[#0066FF] text-white",
                        "bg-[#1A2332] text-[#A9B3C1] hover:bg-[#2A3441]",
                    ),
                ),
                rx.el.button(
                    "Failed",
                    on_click=lambda: OutboundMessagingState.change_status_filter("failed"),
                    class_name="px-3 py-1 mr-2 rounded-lg transition-colors "
                    + rx.cond(
                        OutboundMessagingState.show_status_filter == "failed",
                        "bg-[#0066FF] text-white",
                        "bg-[#1A2332] text-[#A9B3C1] hover:bg-[#2A3441]",
                    ),
                ),
                rx.el.button(
                    "Blocked",
                    on_click=lambda: OutboundMessagingState.change_status_filter(
                        "blocked"
                    ),
                    class_name="px-3 py-1 mr-2 rounded-lg transition-colors "
                    + rx.cond(
                        OutboundMessagingState.show_status_filter == "blocked",
                        "bg-[#0066FF] text-white",
                        "bg-[#1A2332] text-[#A9B3C1] hover:bg-[#2A3441]",
                    ),
                ),
                class_name="mb-4",
            ),
            # Table
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "Timestamp",
                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Recipient",
                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Type",
                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Status",
                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Details",
                                class_name="px-6 py-3 text-left text-xs font-medium text-[#A9B3C1] uppercase tracking-wider",
                            ),
                        ),
                        class_name="bg-[#1A2332]",
                    ),
                    rx.el.tbody(
                        rx.foreach(
                            OutboundMessagingState.recent_messages,
                            lambda msg: rx.el.tr(
                                rx.el.td(
                                    msg.created_at,
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]",
                                ),
                                rx.el.td(
                                    msg.recipient_email,
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]",
                                ),
                                rx.el.td(
                                    msg.message_type,
                                    class_name="px-6 py-4 whitespace-nowrap text-sm text-[#E8F0FF]",
                                ),
                                rx.el.td(
                                    rx.el.span(
                                        msg.status,
                                        class_name=rx.cond(
                                            msg.status == "sent",
                                            "px-2 py-1 text-xs font-semibold rounded-full bg-green-900/30 text-green-400",
                                            rx.cond(
                                                msg.status == "failed",
                                                "px-2 py-1 text-xs font-semibold rounded-full bg-red-900/30 text-red-400",
                                                rx.cond(
                                                    msg.status == "blocked",
                                                    "px-2 py-1 text-xs font-semibold rounded-full bg-yellow-900/30 text-yellow-400",
                                                    "px-2 py-1 text-xs font-semibold rounded-full bg-blue-900/30 text-blue-400",
                                                ),
                                            ),
                                        ),
                                    ),
                                    class_name="px-6 py-4 whitespace-nowrap text-sm",
                                ),
                                rx.el.td(
                                    rx.cond(
                                        msg.failure_reason,
                                        msg.failure_reason,
                                        "-",
                                    ),
                                    class_name="px-6 py-4 text-sm text-[#A9B3C1]",
                                ),
                                class_name="border-t border-[#2A3441]",
                            ),
                        ),
                    ),
                    class_name="min-w-full divide-y divide-[#2A3441]",
                ),
                class_name="overflow-x-auto",
            ),
        ),
        class_name="glass-panel p-6 rounded-lg border border-[#2A3441]",
    )


def outbound_messaging_page() -> rx.Component:
    """Main outbound messaging monitoring page."""
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    rx.el.main(
                        rx.el.header(
                            rx.el.div(
                                rx.el.h1(
                                    "Outbound Messaging",
                                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                                ),
                                rx.el.p(
                                    "Monitor and configure outbound messaging guardrails",
                                    class_name="text-[#A9B3C1]",
                                ),
                            ),
                            class_name=header_style,
                        ),
                        # Alert messages
                        rx.cond(
                            OutboundMessagingState.success_message != "",
                            rx.el.div(
                                OutboundMessagingState.success_message,
                                class_name="mb-4 p-4 bg-green-900/30 border border-green-700 text-green-400 rounded-lg",
                            ),
                        ),
                        rx.cond(
                            OutboundMessagingState.error_message != "",
                            rx.el.div(
                                OutboundMessagingState.error_message,
                                class_name="mb-4 p-4 bg-red-900/30 border border-red-700 text-red-400 rounded-lg",
                            ),
                        ),
                        # Statistics cards
                        statistics_cards(),
                        # Configuration widgets
                        rx.el.div(
                            circuit_breaker_widget(),
                            quiet_hours_widget(),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6",
                        ),
                        # Message log table
                        message_log_table(),
                        class_name=page_content_style,
                        on_mount=OutboundMessagingState.load_dashboard,
                    ),
                    footer(),
                    class_name=page_style,
                ),
            ),
            rx.redirect("/login"),
        ),
    )
