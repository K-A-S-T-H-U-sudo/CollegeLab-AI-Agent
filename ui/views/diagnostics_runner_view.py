"""
Diagnostics Runner View for CollegeLab AI Agent.
Runs real system and network tests with multi-stage visualization:
Adapter -> IP -> Gateway -> DNS -> Internet
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any, Optional
from ui.theme import COLORS, FONTS
from ui.components import ConsoleWidget


class DiagnosticsRunnerView(tk.Frame):
    """Execution panel for diagnostic scans with stage progression."""

    def __init__(self, parent, on_trigger_scan: Callable[[str], None], **kwargs):
        super().__init__(parent, bg=COLORS["bg_root"], **kwargs)
        self.on_trigger_scan = on_trigger_scan
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["bg_root"])
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # Header
        hdr = tk.Frame(container, bg=COLORS["bg_root"])
        hdr.pack(fill="x", pady=(0, 10))

        tk.Label(hdr, text="DIAGNOSTIC TEST RUNNER & MULTI-STAGE ANALYSIS", font=FONTS["title_section"], fg=COLORS["primary"], bg=COLORS["bg_root"]).pack(side="left")

        # Scan Buttons Bar
        btn_bar = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        btn_bar.pack(fill="x", pady=(0, 12), padx=0)

        inner_btn = tk.Frame(btn_bar, bg=COLORS["bg_card"])
        inner_btn.pack(fill="x", padx=16, pady=12)

        self.btn_quick = ttk.Button(inner_btn, text="⚡ QUICK SCAN", style="Primary.TButton", command=lambda: self.on_trigger_scan("quick"))
        self.btn_quick.pack(side="left", padx=(0, 8))

        self.btn_full = ttk.Button(inner_btn, text="🔍 FULL DIAGNOSTIC", style="Secondary.TButton", command=lambda: self.on_trigger_scan("full"))
        self.btn_full.pack(side="left", padx=8)

        self.btn_net = ttk.Button(inner_btn, text="🌐 NETWORK ONLY", style="Secondary.TButton", command=lambda: self.on_trigger_scan("network"))
        self.btn_net.pack(side="left", padx=8)

        self.btn_sys = ttk.Button(inner_btn, text="⚡ SYSTEM HEALTH", style="Secondary.TButton", command=lambda: self.on_trigger_scan("system"))
        self.btn_sys.pack(side="left", padx=8)

        self.btn_dev = ttk.Button(inner_btn, text="💻 DEVICE HEALTH", style="Secondary.TButton", command=lambda: self.on_trigger_scan("device"))
        self.btn_dev.pack(side="left", padx=8)

        # Progress bar
        prog_frame = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        prog_frame.pack(fill="x", pady=(0, 12))

        prog_inner = tk.Frame(prog_frame, bg=COLORS["bg_card"])
        prog_inner.pack(fill="x", padx=16, pady=10)

        self.lbl_status = tk.Label(prog_inner, text="Ready. Click any scan button above to begin real inspection.", font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"])
        self.lbl_status.pack(anchor="w", pady=(0, 4))

        self.progressbar = ttk.Progressbar(prog_inner, mode="determinate", length=400)
        self.progressbar.pack(fill="x")

        # ==========================================
        # MULTI-STAGE CONNECTIVITY PIPELINE
        # ==========================================
        stages_card = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        stages_card.pack(fill="x", pady=(0, 10))

        tk.Label(stages_card, text="NETWORK DIAGNOSTIC — CONNECTIVITY CHAIN", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(12, 4))
        tk.Label(stages_card, text="Real-time evaluation along the 5-layer diagnostic hierarchy:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(0, 10))

        self.stages_container = tk.Frame(stages_card, bg=COLORS["bg_card"])
        self.stages_container.pack(fill="x", padx=16, pady=(0, 12))

        self.stage_widgets: Dict[str, Dict[str, Any]] = {}
        stage_names = [
            ("adapter", "1. Adapter", "Physical / Wi-Fi Link"),
            ("ip", "2. IP Config", "Valid IPv4 Lease"),
            ("gateway", "3. Gateway", "Local Switch & Router"),
            ("dns", "4. DNS", "Domain Resolution"),
            ("internet", "5. Internet", "Outbound WAN Traffic")
        ]

        for i, (key, title, subtitle) in enumerate(stage_names):
            box = tk.Frame(self.stages_container, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
            box.pack(side="left", fill="both", expand=True, padx=(0 if i == 0 else 6, 0))

            lbl_t = tk.Label(box, text=title, font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"])
            lbl_t.pack(anchor="w", padx=10, pady=(6, 1))

            lbl_sub = tk.Label(box, text=subtitle, font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_card_alt"])
            lbl_sub.pack(anchor="w", padx=10, pady=(0, 4))

            badge = tk.Label(box, text="PENDING", font=FONTS["badge"], bg=COLORS["bg_card"], fg=COLORS["text_secondary"], padx=6, pady=2)
            badge.pack(anchor="w", padx=10, pady=(0, 6))

            self.stage_widgets[key] = {
                "box": box,
                "badge": badge,
                "title": lbl_t
            }

        # ==========================================
        # DIAGNOSIS SUMMARY BOX (Section 11)
        # ==========================================
        self.diag_box = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        self.diag_box.pack(fill="x", pady=(0, 10))

        db_inner = tk.Frame(self.diag_box, bg=COLORS["bg_card"])
        db_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(db_inner, text="DIAGNOSIS", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 4))

        self.lbl_diag_title = tk.Label(db_inner, text="Diagnosis: Pending Scan", font=FONTS["section_title"], fg=COLORS["primary"], bg=COLORS["bg_card"])
        self.lbl_diag_title.pack(anchor="w")

        self.lbl_diag_conf = tk.Label(db_inner, text="Confidence: ---", font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"])
        self.lbl_diag_conf.pack(anchor="w", pady=(1, 4))

        # Why explanation
        why_frame = tk.Frame(db_inner, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        why_frame.pack(fill="x", pady=(4, 10))

        wf_inner = tk.Frame(why_frame, bg=COLORS["bg_card_alt"])
        wf_inner.pack(fill="x", padx=12, pady=8)

        tk.Label(wf_inner, text="Why?", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"]).pack(anchor="w")
        self.lbl_diag_why = tk.Label(
            wf_inner,
            text="Run a diagnostic scan to see the evidence-based causal explanation.",
            font=FONTS["body_small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card_alt"],
            wraplength=700,
            justify="left"
        )
        self.lbl_diag_why.pack(anchor="w", pady=(2, 0))

        # Actions Row [ RUN RECHECK ] [ ATTEMPT SAFE FIX ] [ VIEW DETAILS ]
        actions_row = tk.Frame(db_inner, bg=COLORS["bg_card"])
        actions_row.pack(fill="x")

        self.btn_recheck = ttk.Button(actions_row, text="RUN RECHECK", style="Primary.TButton", command=lambda: self.on_trigger_scan("network"))
        self.btn_recheck.pack(side="left", padx=(0, 6))

        self.btn_attempt_fix = ttk.Button(actions_row, text="ATTEMPT SAFE FIX", style="Secondary.TButton", state="disabled")
        self.btn_attempt_fix.pack(side="left", padx=6)

        self.btn_view_details = ttk.Button(actions_row, text="VIEW DETAILS", style="Secondary.TButton")
        self.btn_view_details.pack(side="left", padx=6)

        # Real-time Execution Console
        console_frame = tk.Frame(container, bg=COLORS["bg_root"])
        console_frame.pack(fill="both", expand=True)

        tk.Label(console_frame, text="REAL-TIME DIAGNOSTIC LOG & MEASUREMENT OUTPUT", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_root"]).pack(anchor="w", pady=(0, 4))
        self.console = ConsoleWidget(console_frame, height=8)
        self.console.pack(fill="both", expand=True)

    def set_callbacks(self, on_attempt_fix: Callable[[str, str], None], on_view_reasoning: Callable[[], None]):
        """Wires up action buttons to application orchestrator."""
        self._on_attempt_fix_cb = on_attempt_fix
        self._on_view_reasoning_cb = on_view_reasoning
        self.btn_view_details.config(command=on_view_reasoning)

    def update_diagnosis_info(self, report):
        """Updates the Diagnosis box with report details."""
        self.lbl_diag_title.config(text=f"Diagnosis: {report.primary_fault}")
        self.lbl_diag_conf.config(text=f"Confidence: {report.confidence}")
        
        why_text = report.why_considered
        if report.why_others_less_likely:
            why_text += f"\n{report.why_others_less_likely}"
        self.lbl_diag_why.config(text=why_text)

        if report.action_key:
            self.btn_attempt_fix.config(
                state="normal",
                text=f"ATTEMPT SAFE FIX ({report.action_key})",
                command=lambda: getattr(self, '_on_attempt_fix_cb', lambda k, a: None)(report.action_key, report.recommended_action)
            )
        else:
            self.btn_attempt_fix.config(state="disabled", text="ATTEMPT SAFE FIX")

    def set_progress(self, message: str, percent: int):
        """Updates progress bar and status message."""
        self.lbl_status.config(text=message)
        self.progressbar["value"] = percent
        self.console.log(f"[{percent:3d}%] {message}", tag="INFO")

    def update_stage_results(self, net_data: Dict[str, Any]):
        """Renders the outcome of each stage in the multi-stage network pipeline."""
        stages = net_data.get("stages", {})
        failed_stage = net_data.get("failed_stage")

        stage_map = {
            "adapter": stages.get("Adapter", "PENDING"),
            "ip": stages.get("IP Configuration", "PENDING"),
            "gateway": stages.get("Default Gateway", "PENDING"),
            "dns": stages.get("DNS Resolution", "PENDING"),
            "internet": stages.get("Internet Access", "PENDING")
        }

        for key, res in stage_map.items():
            w = self.stage_widgets.get(key)
            if not w:
                continue

            if res == "PASS":
                w["badge"].config(text="✔ PASS", bg=COLORS["success_bg"], fg=COLORS["success"])
                w["box"].config(highlightbackground=COLORS["success"])
            elif res == "FAIL":
                w["badge"].config(text="✖ FAIL", bg=COLORS["danger_bg"], fg=COLORS["danger"])
                w["box"].config(highlightbackground=COLORS["danger"])
            else:
                w["badge"].config(text="SKIPPED", bg=COLORS["bg_card"], fg=COLORS["text_muted"])
                w["box"].config(highlightbackground=COLORS["border"])

        if failed_stage:
            stage_names_dict = {
                "adapter": "Adapter Link (Hardware/Driver/Cable)",
                "ip": "IP Configuration (DHCP/APIPA)",
                "gateway": "Default Gateway (Local Router/Switch)",
                "dns": "DNS Resolution (Domain Name Servers)",
                "internet": "Internet Uplink (External ISP WAN)"
            }
            stage_desc = stage_names_dict.get(failed_stage, failed_stage)
            self.lbl_failed_stage.config(
                text=f"✖ CONNECTIVITY BREAKDOWN DETECTED AT STAGE: {stage_desc.upper()}",
                fg=COLORS["danger"]
            )
        else:
            self.lbl_failed_stage.config(
                text="✔ ALL 5 NETWORK STAGES COMPLETED NOMINALLY (Adapter → IP → Gateway → DNS → Internet)",
                fg=COLORS["success"]
            )

    def log_diagnostic_summary(self, raw: Dict[str, Any]):
        """Logs structured diagnostic results into the console."""
        self.console.log("==================================================", tag="MUTED")
        self.console.log(f"DIAGNOSTIC SCAN COMPLETED: {raw.get('timestamp')}", tag="BOLD")
        self.console.log("==================================================", tag="MUTED")

        # Network
        net = raw.get("network")
        if net:
            ip_info = net.get("ip_configuration", {})
            self.console.log(f"[NETWORK] Primary IPv4: {ip_info.get('primary_ip')} | Gateway: {ip_info.get('gateway')} | APIPA: {ip_info.get('is_apipa')}", tag="INFO")
            self.console.log(f"[NETWORK] DNS OK: {net.get('dns_resolution_ok')} (Query: {net.get('dns_resolve_time_ms')}ms) | Internet Reachable: {net.get('internet_reachable')}", tag="INFO")
            if net.get("internet_latency_ms"):
                self.console.log(f"[NETWORK] Avg Ping Latency: {net.get('internet_latency_ms')}ms | Packet Loss: {net.get('packet_loss_pct')}%", tag="INFO")

        # System
        sys_data = raw.get("system")
        if sys_data:
            cpu = sys_data.get("cpu", {})
            ram = sys_data.get("ram", {})
            disk = sys_data.get("disk", {})
            self.console.log(f"[SYSTEM] CPU: {cpu.get('percent')}% ({cpu.get('logical_cores')} Cores) -> Status: {sys_data.get('cpu_status')}", tag="INFO")
            self.console.log(f"[SYSTEM] RAM: {ram.get('used_gb')}GB / {ram.get('total_gb')}GB ({ram.get('percent')}%) -> Status: {sys_data.get('ram_status')}", tag="INFO")
            self.console.log(f"[SYSTEM] Storage: {disk.get('aggregate_used_gb')}GB / {disk.get('aggregate_total_gb')}GB ({disk.get('aggregate_percent')}%) -> Status: {sys_data.get('disk_status')}", tag="INFO")
            self.console.log(f"[SYSTEM] System Uptime: {sys_data.get('uptime', {}).get('uptime_formatted')}", tag="INFO")

        # Device
        dev = raw.get("device")
        if dev:
            cpu_dev = dev.get("cpu", {})
            self.console.log(f"[DEVICE] Hardware CPU: {cpu_dev.get('name')} | Architecture: {cpu_dev.get('architecture')}", tag="INFO")
            self.console.log(f"[DEVICE] Disks: {len(dev.get('storage_devices', []))} physical drive(s) detected", tag="INFO")
            self.console.log(f"[DISCLAIMER] {dev.get('disclaimer')}", tag="WARNING")
