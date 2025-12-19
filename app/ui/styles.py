import reflex as rx

colors = {
    "bg_base": "#0A0F14",
    "bg_elevated": "#0E1520",
    "text_primary": "#E8F0FF",
    "text_secondary": "#A9B3C1",
    "accent_cyan": "#00E5FF",
    "accent_magenta": "#FF3CF7",
    "accent_yellow": "#FFE600",
    "accent_gold": "#D8B76E",
    "success": "#00D68F",
    "warning": "#FFB020",
    "danger": "#FF3B3B",
}


def card_style(accent_color: str) -> dict:
    color_hex = colors.get(f"accent_{accent_color}", "#00E5FF")
    r, g, b = tuple((int(color_hex.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4)))
    return {
        "class_name": f"bg-[#0E1520] p-6 rounded-2xl border transition-all duration-200 ease-in-out hover:-translate-y-0.5 shadow-[0_0_40px_-10px_var(--{accent_color})] hover:shadow-[0_0_60px_-15px_var(--{accent_color})]",
        "style": {"borderColor": f"rgba({r}, {g}, {b}, 0.3)"},
    }


page_style = "flex min-h-screen colabe-bg font-['Inter'] text-[#E8F0FF]"
page_content_style = "flex-1 flex flex-col"
header_style = "flex items-center justify-between p-4 border-b border-white/10"
sidebar_style = "hidden md:flex flex-col w-64 bg-[#0E1520] border-r border-white/10"
sidebar_button_style = "flex items-center space-x-3 text-[#A9B3C1] hover:text-[#E8F0FF] hover:bg-white/5 px-3 py-2 rounded-lg transition-colors"