import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.adapter_state import AdapterState, AdapterInfo
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style, card_style


def adapters_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    adapters_page_content(),
                    footer(),
                    class_name="flex-1 flex flex-col min-w-0 relative",
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def adapters_page_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Test Runner Adapters",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Configure and manage integrations with your testing frameworks.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            stats_section(),
            filter_bar(),
            rx.cond(
                AdapterState.filtered_adapters.length() > 0,
                rx.el.div(
                    rx.foreach(AdapterState.filtered_adapters, adapter_card),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6",
                ),
                empty_adapters_state(),
            ),
            class_name="p-8 flex-1",
        ),
        adapter_config_modal(),
        class_name=page_content_style,
    )


def stats_section() -> rx.Component:
    return rx.el.div(
        stat_card(
            "Total Adapters",
            AdapterState.stats["total"],
            "puzzle",
            "text-blue-400",
            "bg-blue-400/10",
            "border-blue-400/20",
        ),
        stat_card(
            "Connected",
            AdapterState.stats["connected"],
            "plug-2",
            "text-green-400",
            "bg-green-400/10",
            "border-green-400/20",
        ),
        stat_card(
            "Pending Setup",
            AdapterState.stats["pending"],
            "loader_circle",
            "text-yellow-400",
            "bg-yellow-400/10",
            "border-yellow-400/20",
        ),
        class_name="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8",
    )


def stat_card(
    label: str, value: int, icon: str, text_color: str, bg_color: str, border_color: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, size=24, class_name=text_color),
            class_name=f"p-3 rounded-lg {bg_color}",
        ),
        rx.el.div(
            rx.el.p(value, class_name=f"text-2xl font-bold {text_color}"),
            rx.el.p(label, class_name="text-sm text-[#A9B3C1]"),
            class_name="ml-4",
        ),
        class_name=f"flex items-center p-4 rounded-xl bg-[#0E1520] border {border_color}",
    )


def filter_bar() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("search", size=18, class_name="text-[#A9B3C1] ml-3"),
                rx.el.input(
                    placeholder="Search adapters...",
                    on_change=AdapterState.set_search_query,
                    class_name="w-full bg-transparent border-none text-[#E8F0FF] focus:ring-0 placeholder-[#A9B3C1]/50 px-3 py-2",
                ),
                class_name="flex items-center bg-[#0A0F14] border border-white/10 rounded-lg w-full md:w-64 focus-within:border-[#00E5FF] transition-colors",
            ),
            class_name="flex-1",
        ),
        rx.el.div(
            rx.el.button(
                "Connect All Visible",
                on_click=AdapterState.connect_all,
                class_name="hidden md:block px-4 py-2 bg-[#00E5FF]/10 text-[#00E5FF] border border-[#00E5FF]/20 rounded-lg hover:bg-[#00E5FF]/20 transition-colors text-sm font-medium mr-2",
            ),
            rx.el.select(
                rx.foreach(
                    AdapterState.unique_categories, lambda x: rx.el.option(x, value=x)
                ),
                on_change=AdapterState.set_selected_category,
                value=AdapterState.selected_category,
                class_name="bg-[#0A0F14] border border-white/10 text-[#E8F0FF] rounded-lg px-3 py-2 focus:outline-none focus:border-[#00E5FF]",
            ),
            rx.el.select(
                rx.foreach(
                    AdapterState.unique_languages, lambda x: rx.el.option(x, value=x)
                ),
                on_change=AdapterState.set_selected_language,
                value=AdapterState.selected_language,
                class_name="bg-[#0A0F14] border border-white/10 text-[#E8F0FF] rounded-lg px-3 py-2 focus:outline-none focus:border-[#00E5FF]",
            ),
            rx.el.select(
                rx.el.option("All Statuses", value="All"),
                rx.el.option("Connected", value="connected"),
                rx.el.option("Pending", value="pending"),
                rx.el.option("Disabled", value="disabled"),
                on_change=AdapterState.set_selected_status,
                value=AdapterState.selected_status,
                class_name="bg-[#0A0F14] border border-white/10 text-[#E8F0FF] rounded-lg px-3 py-2 focus:outline-none focus:border-[#00E5FF]",
            ),
            class_name="flex flex-wrap gap-2 md:gap-4",
        ),
        class_name="flex flex-col md:flex-row gap-4 mb-8 items-start md:items-center",
    )


def adapter_card(adapter: AdapterInfo) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(adapter.icon, size=24, class_name="text-[#00E5FF]"),
                class_name="p-3 rounded-lg bg-[#0A0F14] border border-white/5",
            ),
            status_indicator(adapter),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.h3(
            adapter.name, class_name="text-xl font-bold text-[#E8F0FF] mb-1 truncate"
        ),
        rx.el.div(
            rx.el.p(
                adapter.category,
                class_name="text-xs text-[#00E5FF] font-semibold uppercase tracking-wider mb-1",
            ),
            rx.el.p(adapter.language, class_name="text-sm text-[#A9B3C1]"),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.foreach(
                adapter.supported_test_types,
                lambda t: rx.el.span(
                    t,
                    class_name="px-2 py-1 text-xs rounded bg-white/5 text-[#A9B3C1] border border-white/5",
                ),
            ),
            class_name="flex flex-wrap gap-2 mb-6",
        ),
        rx.el.div(
            rx.el.button(
                "Configure",
                on_click=AdapterState.open_config(adapter),
                class_name="text-sm font-semibold text-[#00E5FF] hover:underline",
            ),
            rx.el.div(
                rx.el.label(
                    rx.el.input(
                        type="checkbox",
                        checked=adapter.status == "connected",
                        on_change=lambda _: AdapterState.toggle_status(adapter.id),
                        disabled=AdapterState.is_connecting[adapter.id],
                        class_name="sr-only peer",
                    ),
                    rx.el.div(
                        class_name="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[#00E5FF] cursor-pointer relative"
                    ),
                    class_name=rx.cond(
                        AdapterState.is_connecting[adapter.id],
                        "inline-flex items-center cursor-wait opacity-50",
                        "inline-flex items-center cursor-pointer",
                    ),
                ),
                class_name="flex items-center",
            ),
            class_name="flex justify-between items-center pt-4 border-t border-white/5",
        ),
        **card_style("cyan"),
    )


def status_indicator(adapter: AdapterInfo) -> rx.Component:
    return rx.el.div(
        rx.cond(
            AdapterState.is_connecting[adapter.id],
            rx.el.div(
                class_name="animate-spin h-4 w-4 border-2 border-[#00E5FF] border-t-transparent rounded-full"
            ),
            rx.el.span(
                class_name=rx.cond(
                    adapter.status == "connected",
                    "block h-2.5 w-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)]",
                    rx.cond(
                        adapter.status == "pending",
                        "block h-2.5 w-2.5 rounded-full bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.6)]",
                        "block h-2.5 w-2.5 rounded-full bg-gray-600",
                    ),
                )
            ),
        ),
        class_name="flex items-center justify-center p-2 rounded-full bg-[#0A0F14] border border-white/5 h-9 w-9",
    )


def empty_adapters_state() -> rx.Component:
    return rx.el.div(
        rx.icon("puzzle", size=48, class_name="text-[#A9B3C1] opacity-50 mb-4"),
        rx.el.h3(
            "No Adapters Found", class_name="text-xl font-semibold text-[#E8F0FF]"
        ),
        rx.el.p(
            "Try adjusting your filters or search query.",
            class_name="text-[#A9B3C1] mt-2",
        ),
        class_name="flex flex-col items-center justify-center py-20 text-center rounded-2xl border-2 border-dashed border-white/10 bg-[#0E1520]/50 col-span-full",
    )


def adapter_config_modal() -> rx.Component:
    return rx.cond(
        AdapterState.selected_adapter,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            rx.cond(
                                AdapterState.selected_adapter,
                                AdapterState.selected_adapter.name + " Configuration",
                                "Configuration",
                            ),
                            class_name="text-xl font-bold text-[#E8F0FF]",
                        ),
                        rx.el.button(
                            rx.icon("x", size=24),
                            on_click=AdapterState.close_config,
                            class_name="text-[#A9B3C1] hover:text-[#E8F0FF] transition-colors",
                        ),
                        class_name="flex justify-between items-center mb-6 border-b border-white/10 pb-4",
                    ),
                    rx.cond(
                        AdapterState.selected_adapter,
                        rx.el.div(
                            rx.el.div(
                                rx.el.p(
                                    AdapterState.selected_adapter.description,
                                    class_name="text-[#A9B3C1] mb-6",
                                ),
                                rx.el.div(
                                    rx.el.h3(
                                        "Integration Details",
                                        class_name="text-sm font-semibold text-[#E8F0FF] uppercase tracking-wider mb-4",
                                    ),
                                    config_detail_item(
                                        "Category",
                                        AdapterState.selected_adapter.category,
                                    ),
                                    config_detail_item(
                                        "Version", AdapterState.selected_adapter.version
                                    ),
                                    config_detail_item(
                                        "Documentation",
                                        rx.el.a(
                                            AdapterState.selected_adapter.docs_url,
                                            href=AdapterState.selected_adapter.docs_url,
                                            target="_blank",
                                            class_name="text-[#00E5FF] hover:underline flex items-center gap-1",
                                        ),
                                    ),
                                    class_name="space-y-3 mb-8",
                                ),
                                rx.el.div(
                                    rx.el.h3(
                                        "Execution Command Template",
                                        class_name="text-sm font-semibold text-[#E8F0FF] uppercase tracking-wider mb-2",
                                    ),
                                    rx.el.div(
                                        rx.el.code(
                                            AdapterState.selected_adapter.cli_command_template,
                                            class_name="font-mono text-sm text-[#00E5FF]",
                                        ),
                                        class_name="bg-[#0A0F14] p-4 rounded-lg border border-white/10 mb-6 font-mono overflow-x-auto",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.h3(
                                        "Required Environment Variables",
                                        class_name="text-sm font-semibold text-[#E8F0FF] uppercase tracking-wider mb-2",
                                    ),
                                    rx.el.div(
                                        rx.foreach(
                                            AdapterState.selected_adapter.env_vars,
                                            lambda v: rx.el.div(
                                                rx.el.span(
                                                    v,
                                                    class_name="px-2 py-1 bg-[#0A0F14] rounded border border-white/10 text-sm text-[#A9B3C1] font-mono",
                                                )
                                            ),
                                        ),
                                        class_name="flex flex-wrap gap-2 mb-6",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.h3(
                                        "Supported CI/CD Platforms",
                                        class_name="text-sm font-semibold text-[#E8F0FF] uppercase tracking-wider mb-2",
                                    ),
                                    rx.el.div(
                                        rx.foreach(
                                            AdapterState.selected_adapter.ci_platforms,
                                            lambda ci: rx.el.div(
                                                rx.icon(
                                                    "check",
                                                    size=14,
                                                    class_name="text-green-400 mr-2",
                                                ),
                                                rx.el.span(
                                                    ci,
                                                    class_name="text-sm text-[#E8F0FF]",
                                                ),
                                                class_name="flex items-center bg-[#0A0F14] px-3 py-2 rounded border border-white/10",
                                            ),
                                        ),
                                        class_name="flex flex-wrap gap-2",
                                    ),
                                ),
                            ),
                            class_name="space-y-6",
                        ),
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Close",
                            on_click=AdapterState.close_config,
                            class_name="px-4 py-2 bg-white/10 text-[#E8F0FF] hover:bg-white/20 font-medium rounded-lg transition-colors",
                        ),
                        class_name="mt-8 flex justify-end pt-4 border-t border-white/10",
                    ),
                ),
                class_name="bg-[#0E1520] p-8 rounded-2xl shadow-2xl border border-white/10 w-full max-w-2xl relative z-50 max-h-[90vh] overflow-y-auto",
            ),
            class_name="fixed inset-0 z-40 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4",
        ),
    )


def config_detail_item(label: str, value: rx.Component | str) -> rx.Component:
    return rx.el.div(
        rx.el.span(label, class_name="text-[#A9B3C1] w-32 shrink-0"),
        rx.el.span(value, class_name="text-[#E8F0FF] font-medium"),
        class_name="flex items-center",
    )