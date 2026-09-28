"""
Reasoning & AI Diagnosis View for CollegeLab AI Agent.
Displays:
1. Diagnosis Summary Card (Fault, Confidence, Recommended Action, [ATTEMPT SAFE FIX])
2. Observed Evidence Checklist (✓ PASS / ✗ FAIL)
3. Explainable Forward Chaining Logic Trace & Rule Deductions
4. Bayesian Probabilistic Diagnosis Ranking with step-by-step mathematical breakdown
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Dict, Any, Optional
from ui.theme import COLORS, FONTS
from ui.components import ConsoleWidget


class ReasoningView(tk.Frame):
    """Deep-dive explainable AI view."""

    def __init__(self, parent, on_attempt_fix: Callable[[str, str], None], **kwargs):
        super().__init__(parent, bg=COLORS["bg_root"], **kwargs)
        self.on_attempt_fix = on_attempt_fix
        self.current_report = None
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

        # Title
        hdr = tk.Frame(content, bg=COLORS["bg_root"])
        hdr.pack(fill="x", padx=20, pady=(15, 10))
        tk.Label(hdr, text="INTELLIGENT AI FAULT DIAGNOSIS & REASONING ENGINE", font=FONTS["title_section"], fg=COLORS["primary"], bg=COLORS["bg_root"]).pack(side="left")

        # ==========================================
        # 1. PRIMARY FAULT & RECOMMENDED ACTION CARD (Section 15)
        # ==========================================
        self.fault_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        self.fault_card.pack(fill="x", padx=20, pady=(0, 15))

        fc_inner = tk.Frame(self.fault_card, bg=COLORS["bg_card"])
        fc_inner.pack(fill="x", padx=20, pady=16)

        # Fault name & status badge
        row1 = tk.Frame(fc_inner, bg=COLORS["bg_card"])
        row1.pack(fill="x", pady=(0, 8))

        tk.Label(row1, text="PRIMARY DIAGNOSED FAULT:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w")
        self.lbl_fault_title = tk.Label(row1, text="No Scan Performed", font=FONTS["title_hero"], fg=COLORS["text_primary"], bg=COLORS["bg_card"])
        self.lbl_fault_title.pack(side="left", anchor="w", pady=(2, 0))

        self.lbl_conf_badge = tk.Label(row1, text="CONFIDENCE: ---", font=FONTS["body_bold"], bg=COLORS["bg_card_alt"], fg=COLORS["primary"], padx=10, pady=4)
        self.lbl_conf_badge.pack(side="right")

        # Category and Severity
        self.lbl_meta = tk.Label(fc_inner, text="Category: --- | System Status: ---", font=FONTS["body_small"], fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        self.lbl_meta.pack(anchor="w", pady=(0, 10))

        # Recommended Action
        act_box = tk.Frame(fc_inner, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        act_box.pack(fill="x", pady=(4, 12))

        act_inner = tk.Frame(act_box, bg=COLORS["bg_card_alt"])
        act_inner.pack(fill="x", padx=14, pady=10)

        tk.Label(act_inner, text="RECOMMENDED ACTION:", font=FONTS["caption"], fg=COLORS["warning"], bg=COLORS["bg_card_alt"]).pack(anchor="w")
        self.lbl_action_text = tk.Label(act_inner, text="Run a diagnostic scan to identify recommended fixes.", font=FONTS["body"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"], wraplength=700, justify="left")
        self.lbl_action_text.pack(anchor="w", pady=(4, 8))

        self.btn_attempt_fix = ttk.Button(
            act_inner,
            text="⚡ ATTEMPT SAFE FIX NOW",
            style="Primary.TButton",
            command=self._on_click_fix
        )
        self.btn_attempt_fix.pack(anchor="w")

        # ==========================================
        # 2. TWO-COLUMN: Observed Evidence & Bayesian Ranking
        # ==========================================
        two_col = tk.Frame(content, bg=COLORS["bg_root"])
        two_col.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        two_col.columnconfigure(0, weight=1)
        two_col.columnconfigure(1, weight=1)

        # LEFT COLUMN: Observed Evidence Checklist
        ev_card = tk.Frame(two_col, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        ev_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        tk.Label(ev_card, text="OBSERVED SENSORY EVIDENCE", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(ev_card, text="Observable parameters collected from real system state:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(0, 10))

        self.ev_container = tk.Frame(ev_card, bg=COLORS["bg_card"])
        self.ev_container.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Placeholder label
        self.lbl_ev_empty = tk.Label(self.ev_container, text="No evidence collected yet.", font=FONTS["body_small"], fg=COLORS["text_muted"], bg=COLORS["bg_card"])
        self.lbl_ev_empty.pack(anchor="w")

        # RIGHT COLUMN: Bayesian Probabilistic Diagnosis (Section 4)
        bayes_card = tk.Frame(two_col, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        bayes_card.grid(row=0, column=1, sticky="nsew")

        tk.Label(bayes_card, text="BAYESIAN PROBABILISTIC DIAGNOSIS", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(bayes_card, text="P(Fault | Evidence) calculated using calibrated college lab priors:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(0, 10))

        self.bayes_table_frame = tk.Frame(bayes_card, bg=COLORS["bg_card"])
        self.bayes_table_frame.pack(fill="both", expand=True, padx=16, pady=(0, 14))

        # Bayesian Treeview table
        columns = ("fault", "prior", "posterior", "confidence")
        self.tree_bayes = ttk.Treeview(self.bayes_table_frame, columns=columns, show="headings", height=6)
        self.tree_bayes.heading("fault", text="Candidate Fault Cause")
        self.tree_bayes.heading("prior", text="Prior P(H)")
        self.tree_bayes.heading("posterior", text="Posterior P(H|E)")
        self.tree_bayes.heading("confidence", text="Confidence")

        self.tree_bayes.column("fault", width=180, anchor="w")
        self.tree_bayes.column("prior", width=65, anchor="center")
        self.tree_bayes.column("posterior", width=85, anchor="center")
        self.tree_bayes.column("confidence", width=85, anchor="center")

        self.tree_bayes.pack(fill="x")
        self.tree_bayes.bind("<<TreeviewSelect>>", self._on_select_bayes_item)

        # Selected Bayesian Math Breakdown Text
        tk.Label(bayes_card, text="MATHEMATICAL FORMULA BREAKDOWN:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(8, 2))
        self.txt_bayes_math = ConsoleWidget(bayes_card, height=6)
        self.txt_bayes_math.pack(fill="x", padx=16, pady=(0, 14))

        # ==========================================
        # 3. FORWARD CHAINING LOGIC TRACE (Section 5)
        # ==========================================
        logic_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        logic_card.pack(fill="x", padx=20, pady=(0, 20))

        tk.Label(logic_card, text="PROPOSITIONAL LOGIC & FORWARD CHAINING INFERENCE TRACE", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(logic_card, text="Step-by-step knowledge base rule firings and working memory derivations:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=16, pady=(0, 10))

        self.txt_logic_trace = ConsoleWidget(logic_card, height=8)
        self.txt_logic_trace.pack(fill="x", padx=16, pady=(0, 14))

    def update_report(self, report):
        """Renders comprehensive diagnosis report onto the reasoning view."""
        self.current_report = report

        # 1. Update Fault Summary Card
        self.lbl_fault_title.config(text=report.primary_fault or "All Systems Nominal")
        conf_str = f"CONFIDENCE: {report.confidence} ({int(report.confidence_score * 100)}%)"
        self.lbl_conf_badge.config(text=conf_str)

        status_color = COLORS["success"] if report.overall_status == "Healthy" else (COLORS["warning"] if report.overall_status == "Warning" else COLORS["danger"])
        self.lbl_meta.config(
            text=f"Category: {report.category} | Lab Computer Status: {report.overall_status}",
            fg=status_color
        )
        self.lbl_action_text.config(text=report.recommended_action or "No action needed.")

        if report.action_key:
            self.btn_attempt_fix.config(state="normal", text=f"⚡ ATTEMPT SAFE FIX ({report.action_key})")
        else:
            self.btn_attempt_fix.config(state="disabled", text="⚡ NO SAFE FIX APPLICABLE")

        # 2. Update Evidence Checklist
        for child in self.ev_container.winfo_children():
            child.destroy()

        for ev in report.evidence:
            row = tk.Frame(self.ev_container, bg=COLORS["bg_card"])
            row.pack(fill="x", pady=2)

            passed = ev["passed"]
            icon = "✔" if passed else "✖"
            icon_fg = COLORS["success"] if passed else COLORS["danger"]
            icon_lbl = tk.Label(row, text=icon, font=FONTS["body_bold"], fg=icon_fg, bg=COLORS["bg_card"], width=2)
            icon_lbl.pack(side="left")

            desc_lbl = tk.Label(row, text=ev["description"], font=FONTS["body_small"], fg=COLORS["text_primary"] if passed else COLORS["danger"], bg=COLORS["bg_card"])
            desc_lbl.pack(side="left", padx=4)

            stat_lbl = tk.Label(row, text=ev["status_str"], font=FONTS["caption"], fg=COLORS["success"] if passed else COLORS["danger"], bg=COLORS["bg_card"])
            stat_lbl.pack(side="right")

        # 3. Update Bayesian Table
        for item in self.tree_bayes.get_children():
            self.tree_bayes.delete(item)

        rankings = getattr(report, "bayesian_rankings", [])
        for r in rankings:
            prior_pct = f"{r['prior'] * 100:.1f}%"
            post_pct = f"{r['posterior'] * 100:.1f}%"
            conf = "HIGH" if r["posterior"] >= 0.7 else ("MED" if r["posterior"] >= 0.3 else "LOW")
            self.tree_bayes.insert("", "end", values=(r["name"], prior_pct, post_pct, conf), tags=(r["fault_id"],))

        # Show top hypothesis math breakdown
        if rankings:
            self.txt_bayes_math.clear()
            self.txt_bayes_math.log(f"Hypothesis: {rankings[0]['name']}", tag="BOLD")
            self.txt_bayes_math.log(rankings[0]["math_breakdown"], tag="INFO")

        # 4. Update Logic Trace
        self.txt_logic_trace.clear()
        trace = getattr(report, "reasoning_trace", [])
        for line in trace:
            if "-> FIRED" in line:
                self.txt_logic_trace.log(line, tag="SUCCESS")
            elif "Perceived" in line:
                self.txt_logic_trace.log(line, tag="INFO")
            elif "ABNORMAL" in line:
                self.txt_logic_trace.log(line, tag="DANGER")
            else:
                self.txt_logic_trace.log(line, tag="MUTED")

    def _on_select_bayes_item(self, event):
        """When user clicks a row in Bayesian table, display its mathematical derivation."""
        selected = self.tree_bayes.selection()
        if not selected or not self.current_report:
            return
        item_vals = self.tree_bayes.item(selected[0], "values")
        name = item_vals[0]
        for r in self.current_report.bayesian_rankings:
            if r["name"] == name:
                self.txt_bayes_math.clear()
                self.txt_bayes_math.log(f"Candidate: {r['name']}", tag="BOLD")
                self.txt_bayes_math.log(r["math_breakdown"], tag="INFO")
                break

    def _on_click_fix(self):
        if self.current_report and self.current_report.action_key:
            self.on_attempt_fix(self.current_report.action_key, self.current_report.recommended_action)
