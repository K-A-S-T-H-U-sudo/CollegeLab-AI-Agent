"""
Dialogs module for CollegeLab AI Agent.
Provides configuration modal for College Lab Mode parameters (Lab Name, Computer ID, Room, Contact).
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config import lab_config
from ui.theme import COLORS, FONTS


class LabSettingsDialog(tk.Toplevel):
    """Modal dialog allowing lab administrator to configure laboratory metadata."""

    def __init__(self, parent, on_saved_callback=None):
        super().__init__(parent)
        self.title("Configure College Lab Metadata")
        self.geometry("520x520")
        self.configure(bg=COLORS["bg_root"])
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_saved_callback = on_saved_callback
        self._build_ui()

    def _build_ui(self):
        container = tk.Frame(self, bg=COLORS["bg_root"], padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text="COLLEGE LAB IDENTITY CONFIGURATION", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_root"]).pack(anchor="w", pady=(0, 2))
        tk.Label(container, text="Configure institutional identification. Fields left empty display as 'Not configured'.", font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_root"]).pack(anchor="w", pady=(0, 14))

        card = tk.Frame(container, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        card.pack(fill="both", expand=True, pady=(0, 16))

        inner = tk.Frame(card, bg=COLORS["bg_card"], padx=16, pady=16)
        inner.pack(fill="both", expand=True)

        # Field 1: College Name
        tk.Label(inner, text="College / Institution Name:", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 2))
        self.ent_college = ttk.Entry(inner, font=FONTS["body"])
        col_val = lab_config.college_name if lab_config.college_name != "Not configured" else ""
        self.ent_college.insert(0, col_val)
        self.ent_college.pack(fill="x", pady=(0, 8))

        # Field 2: Lab Name
        tk.Label(inner, text="Laboratory Name (e.g. AI Lab, Networks Lab):", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 2))
        self.ent_lab = ttk.Entry(inner, font=FONTS["body"])
        lab_val = lab_config.lab_name if lab_config.lab_name != "Not configured" else ""
        self.ent_lab.insert(0, lab_val)
        self.ent_lab.pack(fill="x", pady=(0, 8))

        # Field 3: Computer ID
        tk.Label(inner, text="Computer ID / Station Tag (e.g. AI-LAB-07):", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 2))
        self.ent_cid = ttk.Entry(inner, font=FONTS["body"])
        self.ent_cid.insert(0, lab_config.computer_id)
        self.ent_cid.pack(fill="x", pady=(0, 8))

        # Field 4: Room Location
        tk.Label(inner, text="Room / Hall Number:", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 2))
        self.ent_room = ttk.Entry(inner, font=FONTS["body"])
        room_val = lab_config.room if lab_config.room != "Not configured" else ""
        self.ent_room.insert(0, room_val)
        self.ent_room.pack(fill="x", pady=(0, 8))

        # Field 5: Department
        tk.Label(inner, text="Department:", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 2))
        self.ent_dept = ttk.Entry(inner, font=FONTS["body"])
        dept_val = lab_config.department if lab_config.department != "Not configured" else ""
        self.ent_dept.insert(0, dept_val)
        self.ent_dept.pack(fill="x", pady=(0, 8))

        # Field 6: Technician Contact
        tk.Label(inner, text="Technician / Administrator Email:", font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 2))
        self.ent_email = ttk.Entry(inner, font=FONTS["body"])
        contact_val = lab_config.technician_contact if lab_config.technician_contact != "Not configured" else ""
        self.ent_email.insert(0, contact_val)
        self.ent_email.pack(fill="x", pady=(0, 10))

        # Button row
        btn_row = tk.Frame(container, bg=COLORS["bg_root"])
        btn_row.pack(fill="x")

        btn_cancel = ttk.Button(btn_row, text="Cancel", style="Secondary.TButton", command=self.destroy)
        btn_cancel.pack(side="right", padx=(8, 0))

        btn_save = ttk.Button(btn_row, text="Save Settings", style="Primary.TButton", command=self._save)
        btn_save.pack(side="right")

    def _save(self):
        col_txt = self.ent_college.get().strip()
        lab_txt = self.ent_lab.get().strip()
        cid_txt = self.ent_cid.get().strip()
        rm_txt = self.ent_room.get().strip()
        dept_txt = self.ent_dept.get().strip()
        email_txt = self.ent_email.get().strip()

        lab_config.college_name = col_txt if col_txt else "Not configured"
        lab_config.lab_name = lab_txt if lab_txt else "Not configured"
        lab_config.computer_id = cid_txt if cid_txt else "LAB-PC"
        lab_config.room = rm_txt if rm_txt else "Not configured"
        lab_config.department = dept_txt if dept_txt else "Not configured"
        lab_config.technician_contact = email_txt if email_txt else "Not configured"

        if lab_config.save():
            messagebox.showinfo("Saved", "College Lab configuration saved successfully.")
            if self.on_saved_callback:
                self.on_saved_callback()
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to write configuration file.")
