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
    return {
        "bg": "bg_elevated",
        "p": "6",
        "rounded": "2xl",
        "border": "1px",
        "border_color": f"var(--{accent_color})/0.3",
        "box_shadow": f"0 0 40px -10px var(--{accent_color})",
        "transition": "all 0.2s ease-in-out",
        "_hover": {
            "box_shadow": f"0 0 60px -15px var(--{accent_color})",
            "transform": "translateY(-2px)",
        },
    }


page_style = "flex min-h-screen colabe-bg font-['Inter'] text-text-primary"
page_content_style = "flex-1 flex flex-col"
header_style = "flex items-center justify-between p-4 border-b border-white/10"
sidebar_style = "hidden md:flex flex-col w-64 bg-bg-elevated border-r border-white/10"
sidebar_button_style = "flex items-center space-x-3 text-text-secondary hover:text-text-primary hover:bg-white/5 px-3 py-2 rounded-lg transition-colors"