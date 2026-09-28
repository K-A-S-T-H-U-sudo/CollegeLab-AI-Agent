"""
Main Application Window for CollegeLab AI Agent.
Implements the Practical Desktop Application Layout (Section 10):
- LEFT SIDEBAR:
  - CollegeLab AI Agent Header
  - Navigation:
    1. Overview
    2. Diagnostics
    3. Network
    4. System Health
    5. Devices
    6. Repair Center
    7. History
    8. Settings
- MAIN AREA:
  - Header with section title and lab station badge
  - Dedicated View Container
  - Bottom Status Bar with real-time feedback
"""

import sys
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Dict, Any, Optional

from config import APP_TITLE, APP_SHORT_NAME, APP_SUBTITLE, APP_VERSION, lab_config
from agent import CollegeLabAgent
from ui.theme import COLORS, FONTS, apply_theme
from ui.views.dashboard_view import DashboardView
from ui.views.diagnostics_runner_view import DiagnosticsRunnerView
from ui.views.network_view import NetworkView
from ui.views.system_health_view import SystemHealthView
from ui.views.hardware_view import HardwareView
from ui.views.resolution_view import ResolutionView
from ui.views.history_view import HistoryView
from ui.views.reasoning_view import ReasoningView
from ui.dialogs import LabSettingsDialog


class CollegeLabApp(tk.Tk):
    """Primary Desktop IT Diagnostic Application for College Computer Laboratories."""

    def __init__(self):
        super().__init__()
        self.title(f"{APP_SHORT_NAME} - {APP_SUBTITLE}")
        self.geometry("1200x780")
        self.minsize(1060, 680)

        # Initialize AI Agent Orchestrator
        self.agent = CollegeLabAgent()
        self.is_scanning = False
        self.current_nav_key = "overview"

        # Apply Visual Theme
        apply_theme(self)

        # Build Primary Window Layout
        self._build_layout()

        # Kick off startup real system observation in the background
        self.after(300, self._startup_scan)

    def _build_layout(self):
        """Constructs Left Sidebar and Main Area container."""
        # Top-level container
        self.root_container = tk.Frame(self, bg=COLORS["bg_root"])
        self.root_container.pack(fill="both", expand=True)

        # 1. LEFT SIDEBAR (Section 10)
        self._build_sidebar(self.root_container)

        # 2. MAIN AREA (Section 10)
        self.main_area = tk.Frame(self.root_container, bg=COLORS["bg_root"])
        self.main_area.pack(side="left", fill="both", expand=True)

        self._build_main_header(self.main_area)
        self._build_view_container(self.main_area)
        self._build_status_bar(self.main_area)

    def _build_sidebar(self, parent):
        """Constructs the left navigation sidebar."""
        self.sidebar = tk.Frame(
            parent,
            bg=COLORS["bg_sidebar"],
            width=230,
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Sidebar Header Branding
        hdr_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        hdr_frame.pack(fill="x", padx=16, pady=(18, 14))

        lbl_app = tk.Label(
            hdr_frame,
            text=APP_SHORT_NAME,
            font=FONTS["app_title"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_sidebar"],
            anchor="w"
        )
        lbl_app.pack(fill="x")

        lbl_sub = tk.Label(
            hdr_frame,
            text="College Lab IT Diagnostics",
            font=FONTS["caption"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_sidebar"],
            anchor="w"
        )
        lbl_sub.pack(fill="x", pady=(2, 0))

        # Station Metadata Box
        self.station_box = tk.Frame(
            self.sidebar,
            bg=COLORS["bg_card_alt"],
            bd=1,
            relief="solid",
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        self.station_box.pack(fill="x", padx=14, pady=(0, 16))

        sb_inner = tk.Frame(self.station_box, bg=COLORS["bg_card_alt"])
        sb_inner.pack(fill="x", padx=10, pady=8)

        self.lbl_side_lab = tk.Label(
            sb_inner,
            text=f"LAB: {lab_config.lab_name}",
            font=FONTS["caption"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card_alt"],
            anchor="w"
        )
        self.lbl_side_lab.pack(fill="x")

        self.lbl_side_pc = tk.Label(
            sb_inner,
            text=f"STATION: {lab_config.computer_id}",
            font=FONTS["body_bold"],
            fg=COLORS["primary"],
            bg=COLORS["bg_card_alt"],
            anchor="w"
        )
        self.lbl_side_pc.pack(fill="x", pady=(2, 0))

        # Divider
        div = tk.Frame(self.sidebar, height=1, bg=COLORS["border"])
        div.pack(fill="x", padx=14, pady=(0, 10))

        # Sidebar Nav Items (Section 10 List)
        self.nav_items = [
            ("overview", "📊  Overview"),
            ("diagnostics", "⚡  Diagnostics"),
            ("network", "🌐  Network"),
            ("health", "📈  System Health"),
            ("devices", "💻  Devices"),
            ("repair", "🛠  Repair Center"),
            ("history", "📋  History"),
            ("reasoning", "🧠  AI Reasoning"),
            ("settings", "⚙  Settings"),
        ]

        self.nav_buttons = {}
        for key, text in self.nav_items:
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=FONTS["nav_item"],
                fg=COLORS["sidebar_text"],
                bg=COLORS["bg_sidebar"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["sidebar_text_active"],
                bd=0,
                anchor="w",
                padx=16,
                pady=9,
                cursor="hand2",
                command=lambda k=key: self._on_nav_selected(k)
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.nav_buttons[key] = btn

        # Bottom Quick Scan Action in Sidebar
        bottom_box = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"])
        bottom_box.pack(side="bottom", fill="x", padx=14, pady=16)

        btn_scan = ttk.Button(
            bottom_box,
            text="⚡ RUN QUICK SCAN",
            style="Primary.TButton",
            command=lambda: self.trigger_scan("quick", switch_view=False)
        )
        btn_scan.pack(fill="x", pady=(0, 8))

        lbl_ver = tk.Label(
            bottom_box,
            text=f"Agent Engine v{APP_VERSION}",
            font=FONTS["caption"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_sidebar"]
        )
        lbl_ver.pack()

    def _build_main_header(self, parent):
        """Top header of the main content area."""
        self.header_bar = tk.Frame(
            parent,
            bg=COLORS["bg_card"],
            height=46,
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        self.header_bar.pack(fill="x", side="top")

        hb_inner = tk.Frame(self.header_bar, bg=COLORS["bg_card"])
        hb_inner.pack(fill="x", padx=20, pady=8)

        self.lbl_main_title = tk.Label(
            hb_inner,
            text="Computer Overview",
            font=FONTS["section_title"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"]
        )
        self.lbl_main_title.pack(side="left")

        # Right-side Live Status and Station Badge
        right_frame = tk.Frame(hb_inner, bg=COLORS["bg_card"])
        right_frame.pack(side="right")

        self.lbl_live_status = tk.Label(
            right_frame,
            text="● Idle",
            font=FONTS["body_bold"],
            fg=COLORS["success"],
            bg=COLORS["bg_card"]
        )
        self.lbl_live_status.pack(side="left", padx=(0, 14))

        self.station_tag = tk.Label(
            right_frame,
            text=f"{lab_config.college_name} | {lab_config.lab_name} ({lab_config.computer_id})",
            font=FONTS["body_small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"]
        )
        self.station_tag.pack(side="left")

    def _build_view_container(self, parent):
        """Builds container and instantiates all sub-views."""
        self.view_container = tk.Frame(parent, bg=COLORS["bg_root"])
        self.view_container.pack(fill="both", expand=True)

        # 1. Overview
        self.view_dashboard = DashboardView(
            self.view_container,
            on_trigger_scan=self.trigger_scan,
            on_view_reasoning=lambda: self._on_nav_selected("reasoning"),
            on_view_history=lambda: self._on_nav_selected("history"),
            on_open_settings=self._open_settings_dialog
        )

        # 2. Diagnostics Runner
        self.view_runner = DiagnosticsRunnerView(
            self.view_container,
            on_trigger_scan=self.trigger_scan
        )
        self.view_runner.set_callbacks(
            on_attempt_fix=self.handle_attempt_fix,
            on_view_reasoning=lambda: self._on_nav_selected("reasoning")
        )

        # 3. Network View
        self.view_network = NetworkView(self.view_container)

        # 4. System Health View
        self.view_system_health = SystemHealthView(self.view_container)

        # 5. Devices View
        self.view_hardware = HardwareView(self.view_container)

        # 6. Repair Center View (Section 13)
        self.view_resolution = ResolutionView(
            self.view_container,
            on_execute_fix_and_verify=self.handle_execute_fix_and_verify
        )

        # 7. Audit History View
        self.view_history = HistoryView(self.view_container)

        # 8. AI Reasoning View
        self.view_reasoning = ReasoningView(
            self.view_container,
            on_attempt_fix=self.handle_attempt_fix
        )

        # Map views
        self.views = {
            "overview": (self.view_dashboard, "Computer Overview & System Health"),
            "diagnostics": (self.view_runner, "Multi-Stage Diagnostic Hierarchy"),
            "network": (self.view_network, "Network Adapters, IP Routing & Connectivity"),
            "health": (self.view_system_health, "System Resource Health & Workload"),
            "devices": (self.view_hardware, "Hardware Subsystems & Devices"),
            "repair": (self.view_resolution, "Repair Center - Safe Remediation & Verification"),
            "history": (self.view_history, "Local Diagnostic & Repair Audit Trail"),
            "reasoning": (self.view_reasoning, "Explainable AI Reasoning & Bayesian Derivation"),
        }

        # Show initial view (Overview)
        self._on_nav_selected("overview")

    def _build_status_bar(self, parent):
        """Bottom status bar with real-time feedback."""
        self.status_bar = tk.Frame(
            parent,
            bg=COLORS["bg_card_alt"],
            height=26,
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )
        self.status_bar.pack(fill="x", side="bottom")

        sb_inner = tk.Frame(self.status_bar, bg=COLORS["bg_card_alt"])
        sb_inner.pack(fill="x", padx=16, pady=3)

        self.lbl_status_msg = tk.Label(
            sb_inner,
            text="Supported diagnostics completed successfully.",
            font=FONTS["caption"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card_alt"]
        )
        self.lbl_status_msg.pack(side="left")

        self.lbl_status_activity = tk.Label(
            sb_inner,
            text="● Idle",
            font=FONTS["caption"],
            fg=COLORS["success"],
            bg=COLORS["bg_card_alt"]
        )
        self.lbl_status_activity.pack(side="right")

    def _on_nav_selected(self, key: str):
        """Switches active view and updates sidebar highlight."""
        if key == "settings":
            self._open_settings_dialog()
            return

        if key not in self.views:
            return

        self.current_nav_key = key

        # Update button styling
        for btn_key, btn in self.nav_buttons.items():
            if btn_key == key:
                btn.config(
                    bg=COLORS["sidebar_active"],
                    fg=COLORS["sidebar_text_active"],
                    font=FONTS["nav_item_active"]
                )
            else:
                btn.config(
                    bg=COLORS["bg_sidebar"],
                    fg=COLORS["sidebar_text"],
                    font=FONTS["nav_item"]
                )

        # Hide all views
        for v, _ in self.views.values():
            v.pack_forget()

        # Display selected view
        target_view, title_text = self.views[key]
        target_view.pack(fill="both", expand=True)
        self.lbl_main_title.config(text=title_text)

    def _startup_scan(self):
        """Runs initial perception upon application open to fill real computer metrics."""
        self.trigger_scan(scan_mode="quick", switch_view=False)

    def trigger_scan(self, scan_mode: str = "quick", switch_view: bool = True):
        """Launches diagnostic scan on a background thread to prevent UI freezing."""
        if self.is_scanning:
            messagebox.showinfo("Scan In Progress", "A diagnostic scan is already actively running.")
            return

        self.is_scanning = True
        self.lbl_live_status.config(text="● Scanning...", fg=COLORS["warning"])
        self.lbl_status_activity.config(text="● Scanning...", fg=COLORS["warning"])
        self.lbl_status_msg.config(text=f"Agent executing {scan_mode.upper()} diagnostic scan on local machine...")

        if switch_view:
            self._on_nav_selected("diagnostics")

        def worker():
            try:
                def progress(msg, pct):
                    self.after(0, lambda: self.view_runner.set_progress(msg, pct))

                # PERCEIVE
                raw = self.agent.perceive(scan_mode=scan_mode, progress_callback=progress)
                # REASON & DECIDE
                report = self.agent.decide()

                # Dispatch UI updates back to main Tk thread
                self.after(0, lambda: self._on_scan_completed(raw, report))
            except Exception as e:
                self.after(0, lambda: self._on_scan_error(str(e)))

        th = threading.Thread(target=worker, daemon=True)
        th.start()

    def _on_scan_completed(self, raw: Dict[str, Any], report):
        """Called on main thread when background scan finishes."""
        self.is_scanning = False
        self.lbl_live_status.config(text="● Idle", fg=COLORS["success"])
        self.lbl_status_activity.config(text="● Idle", fg=COLORS["success"])
        self.lbl_status_msg.config(text=f"Scan complete: {report.primary_fault} | Supported diagnostics completed successfully.")

        # Update Overview (Dashboard)
        self.view_dashboard.update_metrics_display(raw)
        self.view_dashboard.update_computer_specs(
            raw.get("system", {}),
            raw.get("device", {}),
            raw.get("network", {})
        )
        self.view_dashboard.update_diagnosis_summary(report)

        # Update Diagnostics Runner
        if "network" in raw:
            self.view_runner.update_stage_results(raw["network"])
        self.view_runner.log_diagnostic_summary(raw)
        self.view_runner.update_diagnosis_info(report)

        # Update Network View
        if "network" in raw:
            self.view_network.update_network_data(raw["network"])

        # Update System Health View
        if "system" in raw:
            self.view_system_health.update_system_data(raw["system"])

        # Update Devices View
        if "device" in raw:
            self.view_hardware.update_device_data(raw["device"])

        # Update AI Reasoning View
        self.view_reasoning.update_report(report)

        # Refresh History
        self.view_history.refresh_history()

    def _on_scan_error(self, err_msg: str):
        self.is_scanning = False
        self.lbl_live_status.config(text="● Error", fg=COLORS["danger"])
        self.lbl_status_activity.config(text="● Error", fg=COLORS["danger"])
        self.lbl_status_msg.config(text=f"Scan encountered an error: {err_msg}")
        messagebox.showerror("Diagnostic Error", f"Failed to complete diagnostic scan:\n{err_msg}")

    def handle_attempt_fix(self, action_key: str, action_title: str):
        """Switches to Safe Resolution tab and highlights proposed fix."""
        self._on_nav_selected("repair")
        self.view_resolution.select_action(action_key)

    def handle_execute_fix_and_verify(self, action_key: str, action_title: str):
        """Executes safe fix, re-runs diagnostics, and runs verification diff."""
        self.lbl_live_status.config(text="● Repairing...", fg=COLORS["warning"])
        self.lbl_status_activity.config(text="● Repairing...", fg=COLORS["warning"])
        self.lbl_status_msg.config(text=f"Executing safe fix: '{action_title}'...")

        def worker():
            try:
                # 1. ACT
                fix_res = self.agent.act(action_key)
                self.after(0, lambda: self.view_resolution.log_repair_execution(fix_res["logs"]))

                # 2. VERIFY
                verif_res = self.agent.verify(action_key, action_title)
                self.after(0, lambda: self._on_verification_completed(verif_res))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Repair Error", f"Exception during repair: {e}"))

        th = threading.Thread(target=worker, daemon=True)
        th.start()

    def _on_verification_completed(self, verif_res: Dict[str, Any]):
        """Called when post-repair empirical verification is complete."""
        self.lbl_live_status.config(text="● Idle", fg=COLORS["success"])
        self.lbl_status_activity.config(text="● Idle", fg=COLORS["success"])
        self.lbl_status_msg.config(text=f"Verification Complete: {verif_res['verdict']}")
        self.view_resolution.display_verification_result(verif_res)
        self.view_history.refresh_history()

        # Update Dashboard summary
        if self.agent.last_report:
            self.view_dashboard.update_diagnosis_summary(self.agent.last_report)
            self.view_dashboard.update_metrics_display(self.agent.current_raw_diagnostics)

    def _open_settings_dialog(self):
        """Opens lab metadata settings modal."""
        def on_saved():
            self.station_tag.config(
                text=f"{lab_config.college_name} | {lab_config.lab_name} ({lab_config.computer_id})"
            )
            self.lbl_side_lab.config(text=f"LAB: {lab_config.lab_name}")
            self.lbl_side_pc.config(text=f"STATION: {lab_config.computer_id}")
            self.view_dashboard.update_lab_header()

        LabSettingsDialog(self, on_saved_callback=on_saved)


def run_app():
    """Application entry point."""
    app = CollegeLabApp()
    app.mainloop()


if __name__ == "__main__":
    run_app()
