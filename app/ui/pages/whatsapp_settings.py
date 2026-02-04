"""
WhatsApp Connector Settings Page
"""
import reflex as rx
from app.ui.components.footer import footer
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.states.auth_state import AuthState
from app.ui.states.whatsapp_connector_state import WhatsAppConnectorState
from app.ui.styles import page_style, page_content_style, header_style, card_style


def whatsapp_settings_page() -> rx.Component:
    """Main WhatsApp settings page"""
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    whatsapp_settings_content(),
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


def whatsapp_settings_content() -> rx.Component:
    """Main content for WhatsApp settings page"""
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "WhatsApp Connector Settings",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Configure your WhatsApp Business API integration",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                connection_settings_card(),
                health_status_card(),
                class_name="grid grid-cols-1 lg:grid-cols-3 gap-8",
            ),
            class_name="p-8 flex-1",
        ),
        class_name=page_content_style,
    )


def connection_settings_card() -> rx.Component:
    """Card for connection settings form"""
    return rx.el.div(
        rx.el.h2(
            "Connection Settings",
            class_name="text-xl font-semibold text-[#E8F0FF] mb-6",
        ),
        rx.el.form(
            # Phone Number ID
            form_field(
                label="Phone Number ID",
                name="phone_number_id",
                placeholder="Enter your WhatsApp Phone Number ID",
                value=WhatsAppConnectorState.phone_number_id,
                on_change=WhatsAppConnectorState.set_phone_number_id,
                error=WhatsAppConnectorState.validation_errors.get("phone_number_id"),
                help_text="Numeric identifier for your WhatsApp phone number",
            ),
            
            # Business Account ID
            form_field(
                label="Business Account ID",
                name="business_account_id",
                placeholder="Enter your WhatsApp Business Account ID",
                value=WhatsAppConnectorState.business_account_id,
                on_change=WhatsAppConnectorState.set_business_account_id,
                error=WhatsAppConnectorState.validation_errors.get("business_account_id"),
                help_text="Numeric identifier for your WhatsApp Business Account",
            ),
            
            # Webhook Verify Token
            form_field(
                label="Webhook Verify Token",
                name="webhook_verify_token",
                placeholder="Enter webhook verification token",
                value=WhatsAppConnectorState.webhook_verify_token,
                on_change=WhatsAppConnectorState.set_webhook_verify_token,
                error=WhatsAppConnectorState.validation_errors.get("webhook_verify_token"),
                help_text="Token for webhook verification (min 8 characters)",
            ),
            
            # Access Token (encrypted)
            access_token_field(),
            
            # Environment Toggle
            environment_toggle(),
            
            # Action Buttons
            rx.el.div(
                rx.el.button(
                    rx.cond(WhatsAppConnectorState.is_testing, "Testing...", "Test Connection"),
                    type="button",
                    on_click=WhatsAppConnectorState.test_connection,
                    disabled=WhatsAppConnectorState.is_testing | WhatsAppConnectorState.is_saving,
                    class_name="px-6 py-2 bg-[#FF3CF7] text-[#0A0F14] font-bold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed",
                ),
                rx.el.button(
                    rx.cond(WhatsAppConnectorState.is_saving, "Saving...", "Save Settings"),
                    type="submit",
                    disabled=WhatsAppConnectorState.is_saving | WhatsAppConnectorState.is_testing,
                    class_name="px-6 py-2 bg-[#00E5FF] text-[#0A0F14] font-bold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed",
                ),
                class_name="flex gap-4 pt-4",
            ),
            on_submit=WhatsAppConnectorState.save_settings,
        ),
        **card_style("cyan"),
        class_name="lg:col-span-2",
    )


def form_field(
    label: str,
    name: str,
    placeholder: str,
    value: rx.Var,
    on_change: callable,
    error: rx.Var = None,
    help_text: str = "",
    input_type: str = "text",
) -> rx.Component:
    """Reusable form field component"""
    return rx.el.div(
        rx.el.label(
            label,
            class_name="block text-sm font-medium text-[#A9B3C1] mb-2",
        ),
        rx.el.input(
            name=name,
            type=input_type,
            placeholder=placeholder,
            value=value,
            on_change=on_change,
            class_name=rx.cond(
                error,
                "w-full px-4 py-3 bg-[#0A0F14] border border-red-500 rounded-lg text-[#E8F0FF] focus:outline-none focus:border-red-400 focus:ring-1 focus:ring-red-400 transition-all",
                "w-full px-4 py-3 bg-[#0A0F14] border border-white/10 rounded-lg text-[#E8F0FF] focus:outline-none focus:border-[#00E5FF] focus:ring-1 focus:ring-[#00E5FF] transition-all",
            ),
        ),
        rx.cond(
            error,
            rx.el.p(error, class_name="mt-1 text-xs text-red-400"),
            rx.cond(
                help_text != "",
                rx.el.p(help_text, class_name="mt-1 text-xs text-[#A9B3C1]"),
            ),
        ),
        class_name="mb-6",
    )


def access_token_field() -> rx.Component:
    """Access token field with visibility toggle"""
    return rx.el.div(
        rx.el.label(
            "Access Token (Encrypted)",
            class_name="block text-sm font-medium text-[#A9B3C1] mb-2",
        ),
        rx.el.div(
            rx.el.input(
                name="access_token",
                type=rx.cond(
                    WhatsAppConnectorState.show_access_token,
                    "text",
                    "password",
                ),
                placeholder="Enter your WhatsApp access token",
                value=WhatsAppConnectorState.access_token,
                on_change=WhatsAppConnectorState.set_access_token,
                class_name=rx.cond(
                    WhatsAppConnectorState.validation_errors.get("access_token"),
                    "w-full px-4 py-3 bg-[#0A0F14] border border-red-500 rounded-lg text-[#E8F0FF] focus:outline-none focus:border-red-400 focus:ring-1 focus:ring-red-400 transition-all pr-12",
                    "w-full px-4 py-3 bg-[#0A0F14] border border-white/10 rounded-lg text-[#E8F0FF] focus:outline-none focus:border-[#00E5FF] focus:ring-1 focus:ring-[#00E5FF] transition-all pr-12",
                ),
            ),
            rx.el.button(
                rx.icon(
                    rx.cond(WhatsAppConnectorState.show_access_token, "eye-off", "eye"),
                    size=20,
                ),
                type="button",
                on_click=WhatsAppConnectorState.toggle_access_token_visibility,
                class_name="absolute right-3 top-1/2 -translate-y-1/2 text-[#A9B3C1] hover:text-[#E8F0FF] transition-colors",
            ),
            class_name="relative",
        ),
        rx.cond(
            WhatsAppConnectorState.validation_errors.get("access_token"),
            rx.el.p(
                WhatsAppConnectorState.validation_errors.get("access_token"),
                class_name="mt-1 text-xs text-red-400",
            ),
            rx.el.p(
                "Token will be encrypted when saved",
                class_name="mt-1 text-xs text-[#A9B3C1]",
            ),
        ),
        class_name="mb-6",
    )


def environment_toggle() -> rx.Component:
    """Environment selection toggle"""
    return rx.el.div(
        rx.el.label(
            "Environment",
            class_name="block text-sm font-medium text-[#A9B3C1] mb-3",
        ),
        rx.el.div(
            environment_option("simulation", "Simulation", "Test mode without real API calls"),
            environment_option("sandbox", "Sandbox", "Meta's sandbox environment"),
            environment_option("live", "Live", "Production WhatsApp Business API"),
            class_name="space-y-3",
        ),
        class_name="mb-8",
    )


def environment_option(value: str, label: str, description: str) -> rx.Component:
    """Single environment option"""
    return rx.el.label(
        rx.el.input(
            type="radio",
            name="environment",
            value=value,
            checked=WhatsAppConnectorState.environment == value,
            on_change=lambda _: WhatsAppConnectorState.set_environment(value),
            class_name="w-4 h-4 text-[#00E5FF] bg-[#0A0F14] border-white/10 focus:ring-[#00E5FF] focus:ring-2",
        ),
        rx.el.div(
            rx.el.span(label, class_name="block text-sm font-medium text-[#E8F0FF]"),
            rx.el.span(description, class_name="block text-xs text-[#A9B3C1]"),
            class_name="ml-3",
        ),
        class_name="flex items-start p-3 rounded-lg bg-[#0A0F14]/50 border border-white/5 hover:border-white/10 transition-colors cursor-pointer",
    )


def health_status_card() -> rx.Component:
    """Card showing health and connection status"""
    return rx.el.div(
        rx.el.h2(
            "Connection Health",
            class_name="text-xl font-semibold text-[#E8F0FF] mb-6",
        ),
        
        # Connection Status
        rx.el.div(
            rx.el.div(
                rx.icon("plug-2", size=20, class_name="text-[#00E5FF]"),
                class_name="p-3 rounded-lg bg-[#0A0F14] border border-white/5",
            ),
            rx.el.div(
                rx.el.p("Status", class_name="text-sm text-[#A9B3C1]"),
                rx.el.p(
                    rx.cond(
                        WhatsAppConnectorState.is_connected,
                        "Connected",
                        "Not Connected",
                    ),
                    class_name=rx.cond(
                        WhatsAppConnectorState.is_connected,
                        "text-lg font-semibold text-green-400",
                        "text-lg font-semibold text-yellow-400",
                    ),
                ),
                class_name="ml-3",
            ),
            class_name="flex items-center mb-6 p-4 rounded-lg bg-[#0A0F14]/50 border border-white/5",
        ),
        
        # Last Health Check
        rx.el.div(
            rx.el.div(
                rx.icon("activity", size=20, class_name="text-[#FF3CF7]"),
                class_name="p-3 rounded-lg bg-[#0A0F14] border border-white/5",
            ),
            rx.el.div(
                rx.el.p("Last Health Check", class_name="text-sm text-[#A9B3C1]"),
                rx.el.p(
                    WhatsAppConnectorState.last_health_check or "Never",
                    class_name="text-sm font-medium text-[#E8F0FF]",
                ),
                class_name="ml-3",
            ),
            class_name="flex items-start mb-6 p-4 rounded-lg bg-[#0A0F14]/50 border border-white/5",
        ),
        
        # Health Check Status
        rx.el.div(
            rx.el.p("Health Status", class_name="text-sm text-[#A9B3C1] mb-2"),
            rx.el.p(
                WhatsAppConnectorState.health_check_status,
                class_name="text-sm text-[#E8F0FF]",
            ),
            class_name="mb-6 p-4 rounded-lg bg-[#0A0F14]/50 border border-white/5",
        ),
        
        # Last Webhook Received
        rx.el.div(
            rx.el.div(
                rx.icon("webhook", size=20, class_name="text-[#00E5FF]"),
                class_name="p-3 rounded-lg bg-[#0A0F14] border border-white/5",
            ),
            rx.el.div(
                rx.el.p("Last Webhook", class_name="text-sm text-[#A9B3C1]"),
                rx.el.p(
                    WhatsAppConnectorState.last_webhook_received or "Never",
                    class_name="text-sm font-medium text-[#E8F0FF]",
                ),
                class_name="ml-3",
            ),
            class_name="flex items-start p-4 rounded-lg bg-[#0A0F14]/50 border border-white/5",
        ),
        
        **card_style("magenta"),
        class_name="lg:col-span-1",
    )
