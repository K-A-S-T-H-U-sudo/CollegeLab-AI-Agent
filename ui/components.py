"""
Reusable UI Components for CollegeLab AI Agent.
Includes Stat Cards, Status Badges, Progress Gauges, Console Terminal, and Comparison Tables.
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional, Callable
from ui.theme import COLORS, FONTS


class StatCard(tk.Frame):
    """A card displaying a key metric with title, value, and status."""

    def __init__(self, parent, title: str, value: str = "---", subtext: str = "", status: str = "Healthy", **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1, **kwargs)
        
        self.pack_propagate(False)
        
        # Header container
        top_frame = tk.Frame(self, bg=COLORS["bg_card"])
        top_frame.pack(fill="x", padx=12, pady=(10, 4))
        
        self.lbl_title = tk.Label(top_frame, text=title.upper(), font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"])
        self.lbl_title.pack(side="left")

        self.lbl_status = tk.Label(top_frame, text=f"● {status}", font=FONTS["caption"], fg=self._get_status_color(status), bg=COLORS["bg_card"])
        self.lbl_status.pack(side="right")

        # Metric Value
        self.lbl_value = tk.Label(self, text=value, font=FONTS["metric_number"], fg=COLORS["text_primary"], bg=COLORS["bg_card"])
        self.lbl_value.pack(anchor="w", padx=12, pady=(2, 2))

        # Subtext
        self.lbl_subtext = tk.Label(self, text=subtext, font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        self.lbl_subtext.pack(anchor="w", padx=12, pady=(0, 8))

    def update_data(self, value: str, subtext: str = "", status: str = "Healthy"):
        self.lbl_value.config(text=value)
        if subtext:
            self.lbl_subtext.config(text=subtext)
        self.lbl_status.config(text=f"● {status}", fg=self._get_status_color(status))

    def _get_status_color(self, status: str) -> str:
        s = status.lower()
        if "health" in s or "pass" in s or "ok" in s:
            return COLORS["success"]
        elif "warn" in s or "mod" in s:
            return COLORS["warning"]
        elif "crit" in s or "fail" in s or "high" in s:
            return COLORS["danger"]
        return COLORS["text_secondary"]


class StatusBadge(tk.Label):
    """Pill badge showing state (🟢 PASS / 🟡 WARN / 🔴 FAIL)."""

    def __init__(self, parent, text: str = "PASS", state: str = "pass", **kwargs):
        color_map = {
            "pass": (COLORS["success_bg"], COLORS["success"]),
            "warn": (COLORS["warning_bg"], COLORS["warning"]),
            "fail": (COLORS["danger_bg"], COLORS["danger"]),
            "neutral": (COLORS["bg_card_alt"], COLORS["text_secondary"])
        }
        bg, fg = color_map.get(state.lower(), color_map["neutral"])
        super().__init__(
            parent,
            text=f" {text} ",
            font=FONTS["caption"],
            bg=bg,
            fg=fg,
            bd=0,
            padx=6,
            pady=2,
            **kwargs
        )


class MetricBar(tk.Frame):
    """Custom canvas-based progress bar with dynamic color grading."""

    def __init__(self, parent, label: str, value: float = 0.0, max_val: float = 100.0, unit: str = "%", height: int = 12, **kwargs):
        super().__init__(parent, bg=COLORS["bg_card"], **kwargs)
        self.max_val = max_val
        self.unit = unit
        self.height = height

        # Top label row
        header = tk.Frame(self, bg=COLORS["bg_card"])
        header.pack(fill="x", pady=(0, 4))
        
        self.lbl_name = tk.Label(header, text=label, font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"])
        self.lbl_name.pack(side="left")

        self.lbl_val = tk.Label(header, text=f"{value:.1f}{unit}", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card"])
        self.lbl_val.pack(side="right")

        # Canvas track
        self.canvas = tk.Canvas(self, height=height, bg=COLORS["bg_card_alt"], bd=0, highlightthickness=0)
        self.canvas.pack(fill="x")
        self.bind("<Configure>", lambda e: self.set_value(self.current_val))
        self.current_val = value
        self.set_value(value)

    def set_value(self, val: float):
        self.current_val = val
        self.lbl_val.config(text=f"{val:.1f}{self.unit}")
        
        # Color based on value
        pct = (val / self.max_val) * 100.0
        if pct < 60:
            fill_color = COLORS["success"]
        elif pct < 85:
            fill_color = COLORS["warning"]
        else:
            fill_color = COLORS["danger"]

        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        if width > 1:
            bar_width = int((val / self.max_val) * width)
            # Rounded capsule or rect
            self.canvas.create_rectangle(0, 0, bar_width, self.height, fill=fill_color, outline="")


class ConsoleWidget(tk.Frame):
    """Terminal console with colored syntax and auto-scrolling."""

    def __init__(self, parent, height: int = 8, **kwargs):
        super().__init__(parent, bg=COLORS["console_bg"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1, **kwargs)
        
        self.text = tk.Text(
            self,
            height=height,
            bg=COLORS["console_bg"],
            fg=COLORS["console_fg"],
            font=FONTS["mono"],
            insertbackground=COLORS["primary"],
            wrap="word",
            bd=0,
            padx=10,
            pady=10
        )
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # Tags
        self.text.tag_config("INFO", foreground=COLORS["primary"])
        self.text.tag_config("SUCCESS", foreground=COLORS["success"])
        self.text.tag_config("WARNING", foreground=COLORS["warning"])
        self.text.tag_config("DANGER", foreground=COLORS["danger"])
        self.text.tag_config("MUTED", foreground=COLORS["text_muted"])
        self.text.tag_config("BOLD", font=FONTS["mono_bold"])

    def log(self, message: str, tag: str = "INFO"):
        self.text.config(state="normal")
        self.text.insert("end", f"{message}\n", (tag,))
        self.text.see("end")
        self.text.config(state="disabled")

    def clear(self):
        self.text.config(state="normal")
        self.text.delete("1.0", "end")
        self.text.config(state="disabled")
