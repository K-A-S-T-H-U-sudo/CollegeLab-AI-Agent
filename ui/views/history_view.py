"""
Diagnostic History View for CollegeLab AI Agent.
Queries local SQLite database, displays past diagnostic events, and provides CSV/JSON lab export.
"""

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Optional
from ui.theme import COLORS, FONTS
from database.history import history_db


class HistoryView(tk.Frame):
    """Local audit trail and history management view."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_root"], **kwargs)
        self.db = history_db
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["bg_root"])
        container.pack(fill="both", expand=True, padx=20, pady=15)

        # Header bar
        hdr = tk.Frame(container, bg=COLORS["bg_root"])
        hdr.pack(fill="x", pady=(0, 10))

        tk.Label(hdr, text="LOCAL AUDIT TRAIL & DIAGNOSTIC HISTORY", font=FONTS["title_section"], fg=COLORS["primary"], bg=COLORS["bg_root"]).pack(side="left")

        # Controls bar (Category Filter, Export, Refresh)
        ctrl_bar = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        ctrl_bar.pack(fill="x", pady=(0, 12))

        cb_inner = tk.Frame(ctrl_bar, bg=COLORS["bg_card"])
        cb_inner.pack(fill="x", padx=16, pady=10)

        # Category Filter
        tk.Label(cb_inner, text="Filter Category:", font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(side="left", padx=(0, 6))
        self.cbo_cat = ttk.Combobox(cb_inner, values=["All", "Network Fault", "System Resource Fault", "Storage/Space Issue", "Verification", "General"], state="readonly", width=22, font=FONTS["body_small"])
        self.cbo_cat.current(0)
        self.cbo_cat.pack(side="left", padx=(0, 15))
        self.cbo_cat.bind("<<ComboboxSelected>>", lambda e: self.refresh_history())

        # Buttons
        self.btn_refresh = ttk.Button(cb_inner, text="🔄 Refresh Log", style="Secondary.TButton", command=self.refresh_history)
        self.btn_refresh.pack(side="left", padx=(0, 8))

        self.btn_export_csv = ttk.Button(cb_inner, text="📊 Export CSV Report", style="Secondary.TButton", command=self._export_csv)
        self.btn_export_csv.pack(side="left", padx=(0, 8))

        self.btn_clear = ttk.Button(cb_inner, text="🗑 Clear History", style="Secondary.TButton", command=self._clear_history)
        self.btn_clear.pack(side="right")

        # Treeview History Table
        table_frame = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        table_frame.pack(fill="both", expand=True, pady=(0, 12))

        columns = ("id", "timestamp", "computer", "category", "diagnosis", "confidence", "action", "verification")
        self.tree_hist = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree_hist.heading("id", text="#")
        self.tree_hist.heading("timestamp", text="Timestamp")
        self.tree_hist.heading("computer", text="Computer ID")
        self.tree_hist.heading("category", text="Category")
        self.tree_hist.heading("diagnosis", text="Diagnosed Fault / Event")
        self.tree_hist.heading("confidence", text="Conf")
        self.tree_hist.heading("action", text="Action Performed")
        self.tree_hist.heading("verification", text="Verification")

        self.tree_hist.column("id", width=35, anchor="center")
        self.tree_hist.column("timestamp", width=130, anchor="center")
        self.tree_hist.column("computer", width=90, anchor="center")
        self.tree_hist.column("category", width=120, anchor="w")
        self.tree_hist.column("diagnosis", width=220, anchor="w")
        self.tree_hist.column("confidence", width=60, anchor="center")
        self.tree_hist.column("action", width=160, anchor="w")
        self.tree_hist.column("verification", width=150, anchor="w")

        scroll_y = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree_hist.yview)
        self.tree_hist.configure(yscrollcommand=scroll_y.set)
        scroll_y.pack(side="right", fill="y")
        self.tree_hist.pack(fill="both", expand=True)

        self.tree_hist.bind("<<TreeviewSelect>>", self._on_select_history_row)

        # Bottom Detail Preview
        self.detail_card = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        self.detail_card.pack(fill="x")

        dc_inner = tk.Frame(self.detail_card, bg=COLORS["bg_card"])
        dc_inner.pack(fill="x", padx=16, pady=10)

        tk.Label(dc_inner, text="HISTORICAL EVENT DETAILS:", font=FONTS["caption"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"]).pack(anchor="w")
        self.lbl_detail_text = tk.Label(dc_inner, text="Select an event from the audit table above to inspect symptoms and verification.", font=FONTS["body_small"], fg=COLORS["text_primary"], bg=COLORS["bg_card"], wraplength=720, justify="left")
        self.lbl_detail_text.pack(anchor="w", pady=(4, 0))

        # Initial data load
        self.refresh_history()

    def refresh_history(self):
        """Reloads records from SQLite database."""
        for item in self.tree_hist.get_children():
            self.tree_hist.delete(item)

        cat_filter = self.cbo_cat.get()
        records = self.db.get_history(limit=100, category_filter=cat_filter)

        for r in records:
            self.tree_hist.insert(
                "",
                "end",
                values=(
                    r["id"],
                    r["timestamp"],
                    r["computer_id"],
                    r["category"],
                    r["diagnosis"],
                    r["confidence"],
                    r["action_performed"],
                    r["verification_result"]
                )
            )

    def _on_select_history_row(self, event):
        selected = self.tree_hist.selection()
        if not selected:
            return
        item_vals = self.tree_hist.item(selected[0], "values")
        event_id = int(item_vals[0])
        details = self.db.get_event_details(event_id)
        if details:
            summary = (
                f"Event #{details['id']} ({details['timestamp']}) | Lab: {details['lab_name']} | PC: {details['computer_id']}\n"
                f"Category: {details['category']} | Diagnosis: {details['diagnosis']} ({details['confidence']})\n"
                f"Symptoms Observed: {details['symptoms_summary']}\n"
                f"Action Executed: {details['action_performed']}\n"
                f"Verification Outcome: {details['verification_result']}"
            )
            self.lbl_detail_text.config(text=summary)

    def _export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Spreadsheet", "*.csv")],
            initialfile="CollegeLab_Diagnostic_Report.csv"
        )
        if filename:
            if self.db.export_to_csv(filename):
                messagebox.showinfo("Export Successful", f"Diagnostic report exported successfully to:\n{filename}")
            else:
                messagebox.showwarning("Export Empty", "No diagnostic history records available to export.")

    def _clear_history(self):
        if messagebox.askyesno("Confirm Clear", "Are you sure you want to clear all local diagnostic history logs?"):
            self.db.clear_all()
            self.refresh_history()
            self.lbl_detail_text.config(text="History cleared.")
