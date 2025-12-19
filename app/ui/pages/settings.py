import reflex as rx
from app.ui.components.footer import footer
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.states.auth_state import AuthState
from app.ui.states.settings_state import SettingsState
from app.ui.styles import page_style, page_content_style, header_style, card_style


def settings_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    settings_content(),
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


def settings_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Settings",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Manage your account and tenant configuration.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.el.div(
                profile_settings_card(),
                tenant_settings_card(),
                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8",
            ),
            class_name="p-8 flex-1",
        ),
        class_name=page_content_style,
    )


def profile_settings_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "User Profile", class_name="text-xl font-semibold text-[#E8F0FF] mb-6"
        ),
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "Username",
                    class_name="block text-sm font-medium text-[#A9B3C1] mb-2",
                ),
                rx.el.input(
                    disabled=True,
                    class_name="w-full px-4 py-3 bg-[#0A0F14]/50 border border-white/5 rounded-lg text-[#A9B3C1] cursor-not-allowed",
                    default_value=SettingsState.username,
                    key=SettingsState.username,
                ),
                rx.el.p(
                    "Username cannot be changed.",
                    class_name="mt-1 text-xs text-[#A9B3C1]",
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.label(
                    "Email Address",
                    class_name="block text-sm font-medium text-[#A9B3C1] mb-2",
                ),
                rx.el.input(
                    name="email",
                    default_value=SettingsState.email,
                    type="email",
                    class_name="w-full px-4 py-3 bg-[#0A0F14] border border-white/10 rounded-lg text-[#E8F0FF] focus:outline-none focus:border-[#00E5FF] focus:ring-1 focus:ring-[#00E5FF] transition-all",
                ),
                class_name="mb-8",
            ),
            rx.el.button(
                rx.cond(SettingsState.is_saving, "Saving...", "Save Changes"),
                type="submit",
                disabled=SettingsState.is_saving,
                class_name="px-6 py-2 bg-[#00E5FF] text-[#0A0F14] font-bold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            on_submit=SettingsState.save_profile,
        ),
        **card_style("cyan"),
    )


def tenant_settings_card() -> rx.Component:
    return rx.el.div(
        rx.el.h2(
            "Tenant Settings", class_name="text-xl font-semibold text-[#E8F0FF] mb-6"
        ),
        rx.el.form(
            rx.el.div(
                rx.el.label(
                    "Organization Name",
                    class_name="block text-sm font-medium text-[#A9B3C1] mb-2",
                ),
                rx.el.input(
                    name="tenant_name",
                    default_value=SettingsState.tenant_name,
                    class_name="w-full px-4 py-3 bg-[#0A0F14] border border-white/10 rounded-lg text-[#E8F0FF] focus:outline-none focus:border-[#FF3CF7] focus:ring-1 focus:ring-[#FF3CF7] transition-all",
                ),
                class_name="mb-8",
            ),
            rx.el.button(
                rx.cond(SettingsState.is_saving, "Saving...", "Update Tenant"),
                type="submit",
                disabled=SettingsState.is_saving,
                class_name="px-6 py-2 bg-[#FF3CF7] text-[#0A0F14] font-bold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed",
            ),
            on_submit=SettingsState.save_tenant,
        ),
        **card_style("magenta"),
    )