"""
Theme and Styling System for CollegeLab AI Agent UI.
Applies a clean, professional, enterprise Windows IT diagnostic utility aesthetic:
- Restrained color semantics (Green = pass/healthy, Yellow = warning/attention, Red = failed/critical, Neutral = info)
- Zero neon, zero glowing effects, zero futuristic decorative elements.
- Clear desktop typography using standard Windows Segoe UI.
"""

import tkinter as tk
from tkinter import ttk

# Professional Enterprise IT Color Palette
COLORS = {
    # Layout Backgrounds
    "bg_root": "#0f172a",          # Deep slate workspace background
    "bg_sidebar": "#1e293b",       # Solid slate left navigation sidebar
    "sidebar_item": "#1e293b",     # Normal sidebar button background
    "sidebar_hover": "#334155",    # Subtle hover background
    "sidebar_active": "#2563eb",   # Enterprise blue active tab indicator
    "sidebar_text": "#94a3b8",     # Muted slate nav text
    "sidebar_text_active": "#ffffff", # Pure white active nav text

    # Cards and Surfaces
    "bg_card": "#1e293b",          # Solid container surface
    "bg_card_alt": "#0f172a",      # Sub-panel / inner container surface
    "border": "#334155",           # Crisp 1px structural border
    "border_focus": "#2563eb",     # Focused border

    # Text Hierarchy
    "text_primary": "#f8fafc",     # High-contrast readable white
    "text_secondary": "#94a3b8",   # Clean slate secondary text
    "text_muted": "#64748b",       # Dim label / caption text

    # Standard Actions (Solid, non-neon enterprise blue)
    "primary": "#2563eb",          # Solid Royal Blue primary action
    "primary_hover": "#1d4ed8",    # Darker blue on hover
    "primary_active": "#1e40af",   # Deep blue pressed state

    # Restrained Status Semantics
    "success": "#16a34a",          # Solid Forest Green (Passed / Healthy)
    "success_bg": "#14532d",       # Dark green pill container
    "success_border": "#15803d",

    "warning": "#d97706",          # Solid Amber / Ochre (Attention / Warning)
    "warning_bg": "#78350f",       # Dark amber pill container
    "warning_border": "#b45309",

    "danger": "#dc2626",           # Solid Crimson Red (Critical / Failed)
    "danger_bg": "#7f1d1d",        # Dark red pill container
    "danger_border": "#b91c1c",

    "neutral": "#64748b",          # Slate gray neutral
    "neutral_bg": "#334155",

    # Console & Log Terminal
    "console_bg": "#090d16",       # Deep black/slate terminal background
    "console_fg": "#e2e8f0"        # Clean terminal output text
}

# Clean Desktop Typography
FONTS = {
    "app_title": ("Segoe UI", 13, "bold"),
    "title_hero": ("Segoe UI", 13, "bold"),
    "section_title": ("Segoe UI", 12, "bold"),
    "title_section": ("Segoe UI", 12, "bold"),
    "card_title": ("Segoe UI", 10, "bold"),
    "title_card": ("Segoe UI", 10, "bold"),
    "nav_item": ("Segoe UI", 10),
    "nav_item_active": ("Segoe UI", 10, "bold"),
    "body": ("Segoe UI", 9),
    "body_bold": ("Segoe UI", 9, "bold"),
    "body_small": ("Segoe UI", 8),
    "caption": ("Segoe UI", 8),
    "mono": ("Consolas", 9),
    "mono_bold": ("Consolas", 9, "bold"),
    "metric_number": ("Segoe UI", 16, "bold"),
    "badge": ("Segoe UI", 8, "bold")
}


def apply_theme(root: tk.Tk):
    """Configures global ttk style tokens to match the professional enterprise theme."""
    style = ttk.Style(root)

    try:
        style.theme_use("clam")
    except Exception:
        pass

    root.configure(bg=COLORS["bg_root"])

    # Configure General TTK Widgets
    style.configure("TFrame", background=COLORS["bg_root"])
    style.configure("Card.TFrame", background=COLORS["bg_card"], relief="solid", borderwidth=1)

    style.configure("TLabel", background=COLORS["bg_root"], foreground=COLORS["text_primary"], font=FONTS["body"])
    style.configure("Card.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_primary"], font=FONTS["body"])
    style.configure("CardTitle.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_primary"], font=FONTS["card_title"])
    style.configure("CardMuted.TLabel", background=COLORS["bg_card"], foreground=COLORS["text_secondary"], font=FONTS["body_small"])

    # Buttons
    style.configure(
        "Primary.TButton",
        background=COLORS["primary"],
        foreground="#ffffff",
        font=FONTS["body_bold"],
        borderwidth=0,
        focuscolor="none",
        padding=(10, 5)
    )
    style.map(
        "Primary.TButton",
        background=[("active", COLORS["primary_hover"]), ("pressed", COLORS["primary_active"])],
        foreground=[("active", "#ffffff")]
    )

    style.configure(
        "Secondary.TButton",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        font=FONTS["body"],
        borderwidth=1,
        bordercolor=COLORS["border"],
        focuscolor="none",
        padding=(8, 4)
    )
    style.map(
        "Secondary.TButton",
        background=[("active", COLORS["border"]), ("pressed", COLORS["bg_card_alt"])],
        foreground=[("active", "#ffffff")]
    )

    style.configure(
        "Success.TButton",
        background=COLORS["success"],
        foreground="#ffffff",
        font=FONTS["body_bold"],
        borderwidth=0,
        focuscolor="none",
        padding=(10, 5)
    )
    style.map(
        "Success.TButton",
        background=[("active", "#15803d")]
    )

    style.configure(
        "Danger.TButton",
        background=COLORS["danger"],
        foreground="#ffffff",
        font=FONTS["body_bold"],
        borderwidth=0,
        padding=(10, 5)
    )

    # Progress bar
    style.configure(
        "TProgressbar",
        thickness=6,
        troughcolor=COLORS["bg_card_alt"],
        background=COLORS["primary"],
        darkcolor=COLORS["primary"],
        lightcolor=COLORS["primary"],
        bordercolor=COLORS["border"]
    )

    # Treeview (Data Tables)
    style.configure(
        "Treeview",
        background=COLORS["bg_card"],
        foreground=COLORS["text_primary"],
        fieldbackground=COLORS["bg_card"],
        rowheight=24,
        font=FONTS["body_small"],
        borderwidth=0
    )
    style.configure(
        "Treeview.Heading",
        background=COLORS["border"],
        foreground=COLORS["text_primary"],
        font=FONTS["body_bold"],
        relief="flat",
        borderwidth=1
    )
    style.map(
        "Treeview",
        background=[("selected", COLORS["sidebar_hover"])],
        foreground=[("selected", "#ffffff")]
    )
    style.map(
        "Treeview.Heading",
        background=[("active", COLORS["sidebar_active"])],
        foreground=[("active", "#ffffff")]
    )

    # Scrollbars
    style.configure("Vertical.TScrollbar", troughcolor=COLORS["bg_card"], background=COLORS["border"])

