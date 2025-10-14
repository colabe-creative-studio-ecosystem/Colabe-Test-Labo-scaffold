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
    accent_var = f"var(--accent-{accent_color})"
    return {
        "bg": colors["bg_elevated"],
        "p": "6",
        "rounded": "xl",
        "border": "1px",
        "border_color": f"hsl(var(--accent-{accent_color}-hsl) / 0.2)",
        "box_shadow": f"0 0 20px -5px hsl(var(--accent-{accent_color}-hsl) / 0.3)",
        "transition": "all 200ms cubic-bezier(0.2, 0.8, 0.2, 1)",
        "_hover": {
            "box_shadow": f"0 0 30px -5px hsl(var(--accent-{accent_color}-hsl) / 0.4)",
            "transform": "translateY(-2px)",
        },
    }


page_style = "flex min-h-screen colabe-bg font-['Inter'] text-text-primary"
page_content_style = "flex-1 flex flex-col"
header_style = "flex items-center justify-between p-4 border-b border-white/10"
sidebar_style = "hidden md:flex flex-col w-64 bg-bg-base border-r border-white/10"
sidebar_button_style = "flex items-center space-x-3 text-text-secondary hover:text-text-primary hover:bg-white/5 px-3 py-2 rounded-lg transition-colors duration-200"