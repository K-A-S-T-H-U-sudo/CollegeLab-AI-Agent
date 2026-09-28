"""
Dedicated Safe Repair Center for CollegeLab AI Agent.
Follows the Section 13 Specification:
- Displays: Problem, Evidence, Proposed Action, Risk Level, Permission Required
- Provides: [ REVIEW ACTION ] / [ EXECUTE SAFE FIX ] and [ CANCEL ]
- Administrator elevation confirmation dialog when required
- Real Execution Console
- Empirical Verification (BEFORE vs AFTER test comparison)
- Clear verdict: "Problem Resolved" or "Problem Not Resolved"
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Dict, Any, Optional
from ui.theme import COLORS, FONTS
from ui.components import ConsoleWidget
from resolution.safe_fixes import SAFE_REPAIR_REGISTRY, is_admin


class ResolutionView(tk.Frame):
    """Enterprise Desktop Repair Center with safety gates and post-repair verification."""

    def __init__(self, parent, on_execute_fix_and_verify: Callable[[str, str], None], **kwargs):
        super().__init__(parent, bg=COLORS["bg_root"], **kwargs)
        self.on_execute_fix_and_verify = on_execute_fix_and_verify
        self._build_ui()

    def _build_ui(self):
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

        # Header
        hdr = tk.Frame(content, bg=COLORS["bg_root"])
        hdr.pack(fill="x", padx=24, pady=(18, 12))

        tk.Label(
            hdr,
            text="REPAIR CENTER",
            font=FONTS["title_section"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_root"]
        ).pack(side="left")

        tk.Label(
            hdr,
            text="Autonomous & Supervised Safe Remediation Protocol",
            font=FONTS["body_small"],
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_root"]
        ).pack(side="left", padx=(14, 0), pady=(4, 0))

        # Administrator Status Banner
        self.admin_banner = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        self.admin_banner.pack(fill="x", padx=24, pady=(0, 14))

        ab_inner = tk.Frame(self.admin_banner, bg=COLORS["bg_card"])
        ab_inner.pack(fill="x", padx=16, pady=8)

        has_admin = is_admin()
        adm_icon = "🛡 Administrator Privileges: ELEVATED (Full repair capabilities enabled)" if has_admin else "ℹ Administrator Privileges: STANDARD USER (Actions requiring elevation will prompt for confirmation)"
        adm_color = COLORS["success"] if has_admin else COLORS["warning"]
        self.lbl_admin = tk.Label(ab_inner, text=adm_icon, font=FONTS["body_bold"], fg=adm_color, bg=COLORS["bg_card"])
        self.lbl_admin.pack(side="left")

        # ==========================================
        # 1. ACTION SELECTOR & SPECIFICATION CARD
        # ==========================================
        card_repair = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        card_repair.pack(fill="x", padx=24, pady=(0, 16))

        cr_inner = tk.Frame(card_repair, bg=COLORS["bg_card"])
        cr_inner.pack(fill="x", padx=18, pady=16)

        # Selector Row
        sel_row = tk.Frame(cr_inner, bg=COLORS["bg_card"])
        sel_row.pack(fill="x", pady=(0, 14))

        tk.Label(
            sel_row,
            text="Select Safe Repair Action:",
            font=FONTS["body_bold"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"]
        ).pack(side="left", padx=(0, 12))

        self.action_keys = list(SAFE_REPAIR_REGISTRY.keys())
        self.action_titles = [f"{v['title']} ({v['category']})" for v in SAFE_REPAIR_REGISTRY.values()]

        self.cbo_actions = ttk.Combobox(sel_row, values=self.action_titles, state="readonly", width=46, font=FONTS["body"])
        self.cbo_actions.current(0)
        self.cbo_actions.pack(side="left", padx=(0, 12))
        self.cbo_actions.bind("<<ComboboxSelected>>", self._on_change_action)

        # Section 13 Structured Specifications Grid
        spec_box = tk.Frame(cr_inner, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        spec_box.pack(fill="x", pady=(0, 16))

        sb_inner = tk.Frame(spec_box, bg=COLORS["bg_card_alt"])
        sb_inner.pack(fill="x", padx=16, pady=14)

        # Fields: Problem, Evidence, Proposed Action, Risk Level, Permission Required
        def make_field(parent, label_text: str, default_val: str = ""):
            row = tk.Frame(parent, bg=COLORS["bg_card_alt"])
            row.pack(fill="x", pady=4)
            lbl_tag = tk.Label(row, text=f"{label_text}:", font=FONTS["body_bold"], fg=COLORS["primary"], bg=COLORS["bg_card_alt"], width=20, anchor="w")
            lbl_tag.pack(side="left")
            lbl_val = tk.Label(row, text=default_val, font=FONTS["body"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"], anchor="w", wraplength=640, justify="left")
            lbl_val.pack(side="left", fill="x", expand=True)
            return lbl_val

        self.lbl_problem = make_field(sb_inner, "Problem")
        self.lbl_evidence = make_field(sb_inner, "Evidence")
        self.lbl_proposed = make_field(sb_inner, "Proposed Action")
        self.lbl_risk = make_field(sb_inner, "Risk Level")
        self.lbl_permission = make_field(sb_inner, "Permission Required")
        self.lbl_commands = make_field(sb_inner, "Commands")

        # Action Buttons
        btn_bar = tk.Frame(cr_inner, bg=COLORS["bg_card"])
        btn_bar.pack(fill="x")

        self.btn_review = ttk.Button(
            btn_bar,
            text="⚡ REVIEW ACTION & EXECUTE FIX",
            style="Primary.TButton",
            command=self._on_click_execute
        )
        self.btn_review.pack(side="left", padx=(0, 12))

        self.btn_cancel = ttk.Button(
            btn_bar,
            text="✕ CANCEL",
            style="Secondary.TButton",
            command=self._on_click_cancel
        )
        self.btn_cancel.pack(side="left")

        # Initial populate
        self._update_action_preview(self.action_keys[0])

        # ==========================================
        # 2. EXECUTION CONSOLE
        # ==========================================
        console_box = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        console_box.pack(fill="x", padx=24, pady=(0, 16))

        cb_inner = tk.Frame(console_box, bg=COLORS["bg_card"])
        cb_inner.pack(fill="x", padx=18, pady=12)

        tk.Label(cb_inner, text="COMMAND EXECUTION & AUDIT LOG", font=FONTS["title_card"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        self.exec_console = ConsoleWidget(cb_inner, height=6)
        self.exec_console.pack(fill="x")

        # ==========================================
        # 3. POST-REPAIR VERIFICATION RESULTS (Section 7 & 13)
        # ==========================================
        verif_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        verif_card.pack(fill="x", padx=24, pady=(0, 20))

        vc_inner = tk.Frame(verif_card, bg=COLORS["bg_card"])
        vc_inner.pack(fill="x", padx=18, pady=14)

        tk.Label(vc_inner, text="POST-REPAIR VERIFICATION (BEFORE vs AFTER)", font=FONTS["title_card"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 8))

        # Verdict Badge Frame
        self.banner_verdict = tk.Frame(vc_inner, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        self.banner_verdict.pack(fill="x", pady=(0, 12))

        bv_inner = tk.Frame(self.banner_verdict, bg=COLORS["bg_card_alt"])
        bv_inner.pack(fill="x", padx=16, pady=10)

        self.lbl_verdict_badge = tk.Label(bv_inner, text="Awaiting Repair Execution", font=FONTS["title_card"], fg=COLORS["text_secondary"], bg=COLORS["bg_card_alt"])
        self.lbl_verdict_badge.pack(anchor="w")

        self.lbl_verdict_desc = tk.Label(
            bv_inner,
            text="After repair commands run, relevant diagnostic tests are re-executed to prove whether the issue was resolved. 'Problem Fixed' is never shown without verification.",
            font=FONTS["body_small"],
            fg=COLORS["text_muted"],
            bg=COLORS["bg_card_alt"],
            wraplength=760,
            justify="left"
        )
        self.lbl_verdict_desc.pack(anchor="w", pady=(2, 0))

        # Verification Diff Treeview
        columns = ("metric", "before", "after", "outcome")
        self.tree_diff = ttk.Treeview(vc_inner, columns=columns, show="headings", height=5)
        self.tree_diff.heading("metric", text="Diagnostic Test")
        self.tree_diff.heading("before", text="BEFORE Repair")
        self.tree_diff.heading("after", text="AFTER Repair")
        self.tree_diff.heading("outcome", text="Status / Outcome")

        self.tree_diff.column("metric", width=220, anchor="w")
        self.tree_diff.column("before", width=120, anchor="center")
        self.tree_diff.column("after", width=120, anchor="center")
        self.tree_diff.column("outcome", width=220, anchor="w")

        self.tree_diff.pack(fill="x")

    def select_action(self, action_id: str):
        """Programmatically select an action in the dropdown."""
        if action_id in self.action_keys:
            idx = self.action_keys.index(action_id)
            self.cbo_actions.current(idx)
            self._update_action_preview(action_id)

    def _on_change_action(self, event=None):
        idx = self.cbo_actions.current()
        if idx >= 0:
            action_id = self.action_keys[idx]
            self._update_action_preview(action_id)

    def _update_action_preview(self, action_id: str):
        data = SAFE_REPAIR_REGISTRY.get(action_id, {})
        self.lbl_problem.config(text=data.get("problem", data.get("title", "")))
        self.lbl_evidence.config(text=data.get("evidence", "Observed diagnostic failure"))
        self.lbl_proposed.config(text=data.get("proposed_action", data.get("description", "")))
        self.lbl_risk.config(text=data.get("risk_level", "Low"))
        self.lbl_permission.config(text=data.get("permission_required", "Standard user"))
        cmds = " -> ".join(data.get("commands", []))
        self.lbl_commands.config(text=cmds)

    def _on_click_cancel(self):
        """Resets the preview and cancels pending repair action."""
        self.exec_console.clear()
        self.exec_console.log("Action cancelled by user.", tag="INFO")

    def _on_click_execute(self):
        idx = self.cbo_actions.current()
        if idx < 0:
            return
        action_id = self.action_keys[idx]
        data = SAFE_REPAIR_REGISTRY.get(action_id, {})

        # Section 6: Administrator permission check & confirmation dialog
        if data.get("requires_admin", False) and not is_admin():
            elev_confirm = messagebox.askyesno(
                "Administrator Permission Required",
                "Administrator permission is required to perform this repair.\n\n"
                f"Action: {data.get('title')}\n"
                f"Command: {', '.join(data.get('commands', []))}\n\n"
                "Do you want to proceed and attempt to run this repair?",
                icon="warning"
            )
            if not elev_confirm:
                self.exec_console.log(f"Repair '{data.get('title')}' aborted: Administrator permission denied by user.", tag="MUTED")
                return

        # General confirmation dialog
        msg = (
            f"Review Proposed Repair Action:\n\n"
            f"Problem: {data.get('problem')}\n"
            f"Evidence: {data.get('evidence')}\n"
            f"Proposed Action: {data.get('proposed_action')}\n"
            f"Risk Level: {data.get('risk_level')}\n"
            f"Permission: {data.get('permission_required')}\n\n"
            f"Execute safe repair and automatically verify with a fresh test?"
        )
        if messagebox.askyesno("Confirm Safe Repair", msg):
            self.on_execute_fix_and_verify(action_id, data.get("title", action_id))

    def log_repair_execution(self, logs: list):
        """Displays execution output in the console widget."""
        self.exec_console.clear()
        for line in logs:
            if "Starting" in line or "Executing" in line:
                self.exec_console.log(line, tag="INFO")
            elif "Cleaned" in line or "finished" in line or "Successfully" in line:
                self.exec_console.log(line, tag="SUCCESS")
            elif "ELEVATION" in line or "Exception" in line or "REJECTED" in line:
                self.exec_console.log(line, tag="DANGER")
            else:
                self.exec_console.log(line, tag="MUTED")

    def display_verification_result(self, verif: Dict[str, Any]):
        """Populates the BEFORE vs AFTER diff table and updates verdict banner."""
        badge = verif.get("badge", "🟢")
        verdict = verif.get("verdict", "Verified")
        msg = verif.get("summary_message", "")
        is_res = verif.get("is_resolved", True)

        fg_color = COLORS["success"] if is_res else COLORS["danger"]
        status_text = "RESOLVED" if is_res else "NOT RESOLVED"

        self.banner_verdict.config(highlightbackground=fg_color)
        self.lbl_verdict_badge.config(
            text=f"{badge} REPAIR RESULT: {status_text}",
            fg=fg_color
        )
        self.lbl_verdict_desc.config(text=msg)

        # Clear table
        for item in self.tree_diff.get_children():
            self.tree_diff.delete(item)

        for row in verif.get("comparison", []):
            self.tree_diff.insert(
                "",
                "end",
                values=(row["test_name"], row["before"], row["after"], row["outcome"])
            )
