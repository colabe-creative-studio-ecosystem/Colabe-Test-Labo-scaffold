import reflex as rx
from app.ui.components.footer import footer
from app.ui.states.diff_state import DiffState
from app.ui.states.auth_state import AuthState
from app.ui.components.sidebar import sidebar, user_dropdown
from app.ui.styles import page_style, page_content_style, header_style, card_style
from app.core.models import AutofixPatch
from app.ui.states.diff_state import PatchDisplay


def diffs_page() -> rx.Component:
    return rx.el.div(
        rx.cond(
            AuthState.is_logged_in,
            rx.el.div(
                sidebar(),
                rx.el.div(
                    diffs_content(), footer(), class_name="flex-1 flex flex-col min-w-0"
                ),
                class_name=page_style,
            ),
            rx.el.div(
                rx.el.p("Loading...", class_name="text-[#E8F0FF]"),
                class_name="flex items-center justify-center min-h-screen colabe-bg",
            ),
        )
    )


def diffs_content() -> rx.Component:
    return rx.el.main(
        rx.el.header(
            rx.el.div(
                rx.el.h1(
                    "Autofix Diffs",
                    class_name="text-2xl font-bold text-[#E8F0FF] title-gradient",
                ),
                rx.el.p(
                    "Review generated patches for security findings.",
                    class_name="text-[#A9B3C1]",
                ),
            ),
            user_dropdown(),
            class_name=header_style,
        ),
        rx.el.div(
            rx.cond(
                DiffState.patches.length() > 0,
                rx.el.div(
                    rx.foreach(DiffState.patches, patch_card), class_name="space-y-6"
                ),
                rx.el.div(
                    rx.icon(
                        "git-compare",
                        size=48,
                        class_name="text-[#A9B3C1] opacity-50 mb-4",
                    ),
                    rx.el.p("No patches generated yet.", class_name="text-[#A9B3C1]"),
                    class_name="flex flex-col items-center justify-center py-20 bg-[#0E1520]/50 rounded-xl border border-dashed border-white/10",
                ),
            ),
            class_name="p-8 flex-1 max-w-5xl mx-auto w-full",
        ),
        class_name=page_content_style,
    )


def patch_card(patch: PatchDisplay) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.el.h3(
                    "Patch for Finding",
                    class_name="text-sm text-[#A9B3C1] uppercase tracking-wider",
                ),
                rx.el.p(
                    rx.cond(
                        patch.run,
                        rx.cond(
                            patch.run.finding,
                            patch.run.finding.description,
                            "Unknown Finding",
                        ),
                        "Unknown Run",
                    ),
                    class_name="text-lg font-bold text-[#E8F0FF] mt-1",
                ),
                rx.el.p(
                    rx.cond(
                        patch.run,
                        rx.cond(patch.run.finding, patch.run.finding.file_path, ""),
                        "",
                    ),
                    class_name="text-sm text-[#00E5FF] mt-1 font-mono",
                ),
            ),
            rx.el.span(patch.created_at, class_name="text-sm text-[#A9B3C1]"),
            class_name="flex justify-between items-start mb-4",
        ),
        rx.el.div(
            rx.el.pre(
                rx.el.code(patch.diff),
                class_name="font-mono text-sm text-[#E8F0FF] overflow-x-auto whitespace-pre",
            ),
            class_name="bg-[#0A0F14] p-4 rounded-lg border border-white/10 overflow-hidden",
        ),
        **card_style("magenta"),
    )