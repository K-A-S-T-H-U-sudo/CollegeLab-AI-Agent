"""
Dashboard View for CollegeLab AI Agent.
Displays real startup computer specifications, College Lab identity banner,
real-time resource utilization, detected issue categories, and primary diagnostic triggers.
"""

import platform
import socket
import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any, Optional
from config import lab_config, APP_TITLE, APP_SHORT_NAME, APP_SUBTITLE, APP_VERSION
from ui.theme import COLORS, FONTS
from ui.components import StatCard, StatusBadge, MetricBar


class DashboardView(tk.Frame):
    """Main dashboard overview tab."""

    def __init__(
        self,
        parent,
        on_trigger_scan: Callable[[str], None],
        on_view_reasoning: Callable[[], None],
        on_view_history: Callable[[], None],
        on_open_settings: Callable[[], None],
        **kwargs
    ):
        super().__init__(parent, bg=COLORS["bg_root"], **kwargs)
        self.on_trigger_scan = on_trigger_scan
        self.on_view_reasoning = on_view_reasoning
        self.on_view_history = on_view_history
        self.on_open_settings = on_open_settings

        self._build_ui()

    def _build_ui(self):
        # Scrollable container for dashboard
        canvas = tk.Canvas(self, bg=COLORS["bg_root"], bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS["bg_root"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = scrollable_frame

        # ==========================================
        # 1. COLLEGE LAB IDENTITY HEADER
        # ==========================================
        lab_frame = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        lab_frame.pack(fill="x", padx=20, pady=(15, 10))

        lab_top = tk.Frame(lab_frame, bg=COLORS["bg_card"])
        lab_top.pack(fill="x", padx=16, pady=(12, 10))

        # Title & Subtitle
        title_box = tk.Frame(lab_top, bg=COLORS["bg_card"])
        title_box.pack(side="left")

        lbl_app = tk.Label(title_box, text=APP_SHORT_NAME, font=FONTS["app_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"])
        lbl_app.pack(anchor="w")

        lbl_sub = tk.Label(title_box, text="Intelligent Computer Fault Diagnosis & Resolution Agent", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"])
        lbl_sub.pack(anchor="w")

        # Edit button on right
        lab_right = tk.Frame(lab_top, bg=COLORS["bg_card"])
        lab_right.pack(side="right")

        self.btn_lab_config = ttk.Button(lab_right, text="Configure Identity", style="Secondary.TButton", command=self.on_open_settings)
        self.btn_lab_config.pack(side="right")

        # Lab Identity Details Row
        lab_details = tk.Frame(lab_frame, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        lab_details.pack(fill="x", padx=16, pady=(0, 12))

        self.lbl_college_name = tk.Label(lab_details, text=f"College: {lab_config.college_name}", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"])
        self.lbl_college_name.pack(side="left", padx=12, pady=8)

        self.lbl_lab_name = tk.Label(lab_details, text=f"Lab: {lab_config.lab_name}", font=FONTS["body"], fg=COLORS["text_secondary"], bg=COLORS["bg_card_alt"])
        self.lbl_lab_name.pack(side="left", padx=12, pady=8)

        self.lbl_comp_id = tk.Label(lab_details, text=f"Computer ID: {lab_config.computer_id}", font=FONTS["body_bold"], fg=COLORS["primary"], bg=COLORS["bg_card_alt"])
        self.lbl_comp_id.pack(side="left", padx=12, pady=8)

        self.lbl_room = tk.Label(lab_details, text=f"Room: {lab_config.room}", font=FONTS["body"], fg=COLORS["text_secondary"], bg=COLORS["bg_card_alt"])
        self.lbl_room.pack(side="left", padx=12, pady=8)

        self.lbl_last_scan = tk.Label(lab_details, text="Last Scan: Pending", font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_card_alt"])
        self.lbl_last_scan.pack(side="right", padx=12, pady=8)

        # ==========================================
        # 2. CURRENT SYSTEM STATUS BANNER
        # ==========================================
        self.status_banner = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["success_border"], highlightthickness=1)
        self.status_banner.pack(fill="x", padx=20, pady=(0, 10))

        sb_inner = tk.Frame(self.status_banner, bg=COLORS["bg_card"])
        sb_inner.pack(fill="x", padx=16, pady=12)

        self.lbl_status_icon = tk.Label(sb_inner, text="[✔ Passed]", font=FONTS["body_bold"], fg=COLORS["success"], bg=COLORS["bg_card"])
        self.lbl_status_icon.pack(side="left", padx=(0, 10))

        status_text_box = tk.Frame(sb_inner, bg=COLORS["bg_card"])
        status_text_box.pack(side="left", fill="x", expand=True)

        self.lbl_status_heading = tk.Label(status_text_box, text="Current Status: Healthy (All Subsystems Nominal)", font=FONTS["section_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"])
        self.lbl_status_heading.pack(anchor="w")

        self.lbl_status_desc = tk.Label(status_text_box, text="Supported diagnostics completed successfully. No supported faults detected.", font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"])
        self.lbl_status_desc.pack(anchor="w", pady=(2, 0))

        # Scan trigger buttons
        btn_box = tk.Frame(sb_inner, bg=COLORS["bg_card"])
        btn_box.pack(side="right")

        self.btn_quick = ttk.Button(btn_box, text="Run Quick Scan", style="Primary.TButton", command=lambda: self.on_trigger_scan("quick"))
        self.btn_quick.pack(side="left", padx=4)

        self.btn_full = ttk.Button(btn_box, text="Full Diagnostic", style="Secondary.TButton", command=lambda: self.on_trigger_scan("full"))
        self.btn_full.pack(side="left", padx=4)

        # ==========================================
        # 3. COMPUTER OVERVIEW (Section 10)
        # ==========================================
        overview_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        overview_card.pack(fill="x", padx=20, pady=(0, 10))

        oc_inner = tk.Frame(overview_card, bg=COLORS["bg_card"])
        oc_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(oc_inner, text="COMPUTER OVERVIEW", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        self.spec_table = tk.Frame(oc_inner, bg=COLORS["bg_card"])
        self.spec_table.pack(fill="x")
        self.spec_labels: Dict[str, tk.Label] = {}

        specs = [
            ("Computer Name", socket.gethostname()),
            ("Operating System", f"{platform.system()} {platform.release()} (Build {platform.version()[:15]})"),
            ("CPU", platform.processor() or "Multi-Core System CPU"),
            ("Memory (RAM)", "Detecting physical memory..."),
            ("Storage", "Detecting storage partitions..."),
            ("Network", "Detecting network interface...")
        ]

        for i, (k, v) in enumerate(specs):
            row_bg = COLORS["bg_card"] if i % 2 == 0 else COLORS["bg_card_alt"]
            rf = tk.Frame(self.spec_table, bg=row_bg)
            rf.pack(fill="x", pady=1)

            lbl_k = tk.Label(rf, text=k, font=FONTS["body_bold"], fg=COLORS["text_secondary"], bg=row_bg, width=18, anchor="w")
            lbl_k.pack(side="left", padx=8, pady=4)

            lbl_v = tk.Label(rf, text=v, font=FONTS["body"], fg=COLORS["text_primary"], bg=row_bg, anchor="w")
            lbl_v.pack(side="left", fill="x", expand=True, padx=8, pady=4)
            self.spec_labels[k] = lbl_v

        # ==========================================
        # 4. DETECTED ISSUES SECTION (Section 10)
        # Only show actual issues! Avoid unnecessary decorative cards.
        # ==========================================
        self.issues_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        self.issues_card.pack(fill="x", padx=20, pady=(0, 15))

        self.ic_inner = tk.Frame(self.issues_card, bg=COLORS["bg_card"])
        self.ic_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(self.ic_inner, text="DETECTED ISSUES", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        # Dynamic Issue Container
        self.issue_items_frame = tk.Frame(self.ic_inner, bg=COLORS["bg_card"])
        self.issue_items_frame.pack(fill="x")

        self.lbl_no_issues = tk.Label(
            self.issue_items_frame,
            text="No supported hardware, network, or system faults detected on this computer.",
            font=FONTS["body"],
            fg=COLORS["success"],
            bg=COLORS["bg_card"]
        )
        self.lbl_no_issues.pack(anchor="w", pady=4)

    def update_computer_specs(self, sys_data: Dict[str, Any], dev_data: Dict[str, Any], net_data: Dict[str, Any]):
        """Populates the Computer Information table with real collected values."""
        # CPU
        cpu_name = dev_data.get("cpu", {}).get("name") if dev_data else None
        if not cpu_name or cpu_name == "Unknown Processor":
            cpu_name = platform.processor() or "Multi-Core System CPU"
        cores = dev_data.get("cpu", {}).get("logical_cores") if dev_data else 4
        self.spec_labels["CPU Model"].config(text=f"{cpu_name} ({cores} Logical Cores)")

        # RAM
        ram_total = sys_data.get("ram", {}).get("total_gb") if sys_data else None
        if ram_total:
            ram_free = sys_data.get("ram", {}).get("available_gb", 0)
            self.spec_labels["RAM Memory"].config(text=f"{ram_total} GB Total ({ram_free} GB Free)")

        # Storage
        disk_total = sys_data.get("disk", {}).get("aggregate_total_gb") if sys_data else None
        if disk_total:
            disk_free = sys_data.get("disk", {}).get("aggregate_free_gb", 0)
            self.spec_labels["Storage"].config(text=f"{disk_total} GB Total ({disk_free} GB Free)")

        # Network Adapters
        adapters = net_data.get("adapters", []) if net_data else []
        active_nics = [a.get("name") for a in adapters if a.get("is_up") and not a.get("is_loopback")]
        if active_nics:
            self.spec_labels["Network Adapters"].config(text=f"{len(adapters)} detected ({', '.join(active_nics[:2])})")
        else:
            self.spec_labels["Network Adapters"].config(text=f"{len(adapters)} adapter(s) found")

        # IP Information
        ip_info = net_data.get("ip_configuration", {}) if net_data else {}
        ip = ip_info.get("primary_ip") or "None"
        gw = ip_info.get("gateway") or "None"
        self.spec_labels["IP Information"].config(text=f"IPv4: {ip} | Gateway: {gw}")

    def update_metrics_display(self, raw: Dict[str, Any]):
        """Updates top stat cards with fresh diagnostic data."""
        # CPU
        sys_data = raw.get("system", {})
        if sys_data:
            cpu_pct = sys_data.get("cpu", {}).get("percent", 0.0)
            cpu_st = sys_data.get("cpu_status", "Healthy")
            self.card_cpu.update_data(f"{cpu_pct:.1f}%", f"{sys_data.get('cpu', {}).get('logical_cores', 1)} Cores Active", status=cpu_st)
    def update_computer_specs(self, sys_data: Dict[str, Any], dev_data: Dict[str, Any], net_data: Dict[str, Any]):
        """Populates the Computer Overview table with real collected values."""
        # CPU
        cpu_name = dev_data.get("cpu", {}).get("name") if dev_data else None
        if not cpu_name or cpu_name == "Unknown Processor":
            cpu_name = platform.processor() or "Multi-Core System CPU"
        cores = dev_data.get("cpu", {}).get("logical_cores") if dev_data else 4
        if "CPU" in self.spec_labels:
            self.spec_labels["CPU"].config(text=f"{cpu_name} ({cores} Logical Processors)")

        # RAM
        ram_total = sys_data.get("ram", {}).get("total_gb") if sys_data else None
        if ram_total and "Memory (RAM)" in self.spec_labels:
            ram_free = sys_data.get("ram", {}).get("available_gb", 0)
            self.spec_labels["Memory (RAM)"].config(text=f"{ram_total} GB Total ({ram_free} GB Available)")

        # Storage
        disk_total = sys_data.get("disk", {}).get("aggregate_total_gb") if sys_data else None
        if disk_total and "Storage" in self.spec_labels:
            disk_free = sys_data.get("disk", {}).get("aggregate_free_gb", 0)
            self.spec_labels["Storage"].config(text=f"{disk_total} GB Aggregate ({disk_free} GB Free)")

        # Network
        adapters = net_data.get("adapters", []) if net_data else []
        active_nics = [a.get("name") for a in adapters if a.get("is_up") and not a.get("is_loopback")]
        ip_info = net_data.get("ip_configuration", {}) if net_data else {}
        primary_ip = ip_info.get("primary_ip") or "None"
        nic_name = active_nics[0] if active_nics else "Ethernet/Wi-Fi"
        if "Network" in self.spec_labels:
            self.spec_labels["Network"].config(text=f"{nic_name} (IPv4: {primary_ip})")

    def update_metrics_display(self, raw: Dict[str, Any]):
        """Updates real metrics across views."""
        pass

    def update_lab_header(self):
        """Refreshes lab header from config."""
        self.lbl_college_name.config(text=f"College: {lab_config.college_name}")
        self.lbl_lab_name.config(text=f"Lab: {lab_config.lab_name}")
        self.lbl_comp_id.config(text=f"Computer ID: {lab_config.computer_id}")
        self.lbl_room.config(text=f"Room: {lab_config.room}")

    def update_diagnosis_summary(self, report):
        """Updates Current Status banner and Detected Issues list."""
        self.update_lab_header()
        self.lbl_last_scan.config(text=f"Last Scan: {report.timestamp}")

        # Update Current Status Banner
        if report.overall_status == "Healthy":
            self.status_banner.config(highlightbackground=COLORS["success_border"])
            self.lbl_status_icon.config(text="[✔ Passed]", fg=COLORS["success"])
            self.lbl_status_heading.config(text="Current Status: Healthy (All Subsystems Nominal)", fg=COLORS["text_primary"])
            self.lbl_status_desc.config(text=report.test_result_summary or "Supported diagnostics completed successfully. No supported faults detected.")
        elif report.overall_status == "Warning":
            self.status_banner.config(highlightbackground=COLORS["warning_border"])
            self.lbl_status_icon.config(text="[⚠ Attention Required]", fg=COLORS["warning"])
            self.lbl_status_heading.config(text=f"Current Status: Attention Required — {report.primary_fault}", fg=COLORS["text_primary"])
            self.lbl_status_desc.config(text=f"Confidence: {report.confidence} | Recommended: {report.recommended_action}")
        else:
            self.status_banner.config(highlightbackground=COLORS["danger_border"])
            self.lbl_status_icon.config(text="[✖ Critical Fault]", fg=COLORS["danger"])
            self.lbl_status_heading.config(text=f"Current Status: Critical — {report.primary_fault}", fg=COLORS["text_primary"])
            self.lbl_status_desc.config(text=f"Confidence: {report.confidence} | Recommended: {report.recommended_action}")

        # Update Detected Issues Container
        for child in self.issue_items_frame.winfo_children():
            child.destroy()

        if report.overall_status == "Healthy":
            lbl = tk.Label(
                self.issue_items_frame,
                text="✔ No supported hardware, network, or system faults detected on this computer.\n   All supported checks passed within normal operating thresholds.",
                font=FONTS["body"],
                fg=COLORS["success"],
                bg=COLORS["bg_card"],
                justify="left"
            )
            lbl.pack(anchor="w", pady=4)
        else:
            # Show the detected issue card
            issue_box = tk.Frame(self.issue_items_frame, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
            issue_box.pack(fill="x", pady=4)

            ib_inner = tk.Frame(issue_box, bg=COLORS["bg_card_alt"])
            ib_inner.pack(fill="x", padx=14, pady=10)

            # Title
            t_row = tk.Frame(ib_inner, bg=COLORS["bg_card_alt"])
            t_row.pack(fill="x")

            title_col = COLORS["danger"] if report.overall_status == "Critical" else COLORS["warning"]
            tk.Label(t_row, text=report.primary_fault or "Fault Detected", font=FONTS["card_title"], fg=title_col, bg=COLORS["bg_card_alt"]).pack(side="left")
            tk.Label(t_row, text=f"Category: {report.category} | Confidence: {report.confidence}", font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_card_alt"]).pack(side="right")

            # Explanation
            if report.what_it_means:
                tk.Label(ib_inner, text=f"Impact: {report.what_it_means}", font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card_alt"], wraplength=700, justify="left").pack(anchor="w", pady=(4, 2))

            if report.confidence_reason:
                tk.Label(ib_inner, text=f"Reason: {report.confidence_reason}", font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_card_alt"], wraplength=700, justify="left").pack(anchor="w", pady=(0, 6))

            # Action Row
            act_row = tk.Frame(ib_inner, bg=COLORS["bg_card_alt"])
            act_row.pack(fill="x", pady=(4, 0))

            tk.Label(act_row, text=f"Action: {report.recommended_action}", font=FONTS["body_small"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"], wraplength=550, justify="left").pack(side="left")

            btn_details = ttk.Button(act_row, text="View Reasoning", style="Secondary.TButton", command=self.on_view_reasoning)
            btn_details.pack(side="right", padx=(8, 0))

