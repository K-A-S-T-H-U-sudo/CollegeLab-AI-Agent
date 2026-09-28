"""
Hardware & Device Health View for CollegeLab AI Agent.
Displays real physical components queried through Windows CIM, WMI, and platform APIs.
Enforces software diagnostic disclaimer regarding physical damage.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any, Optional
from ui.theme import COLORS, FONTS
from diagnostics.device import DeviceDiagnostic


class HardwareView(tk.Frame):
    """Deep-dive hardware inventory and device diagnostics view."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_root"], **kwargs)
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
        hdr.pack(fill="x", padx=20, pady=(15, 10))
        tk.Label(hdr, text="DEVICE & HARDWARE SUBSYSTEM HEALTH", font=FONTS["title_section"], fg=COLORS["primary"], bg=COLORS["bg_root"]).pack(side="left")

        # Mandatory Disclaimer Card (Section 7)
        disc_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["warning"], highlightthickness=1)
        disc_card.pack(fill="x", padx=20, pady=(0, 15))

        dc_inner = tk.Frame(disc_card, bg=COLORS["bg_card"])
        dc_inner.pack(fill="x", padx=16, pady=10)

        tk.Label(dc_inner, text="⚠ HARDWARE DIAGNOSTIC BOUNDARY NOTICE", font=FONTS["caption"], fg=COLORS["warning"], bg=COLORS["bg_card"]).pack(anchor="w")
        tk.Label(
            dc_inner,
            text=DeviceDiagnostic.DISCLAIMER,
            font=FONTS["body_bold"],
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            wraplength=700,
            justify="left"
        ).pack(anchor="w", pady=(2, 0))

        # ==========================================
        # 1. CPU & MEMORY SUBSYSTEMS
        # ==========================================
        row1 = tk.Frame(content, bg=COLORS["bg_root"])
        row1.pack(fill="x", padx=20, pady=(0, 15))
        row1.columnconfigure(0, weight=1)
        row1.columnconfigure(1, weight=1)

        # CPU Card
        cpu_card = tk.Frame(row1, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        cpu_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(cpu_card, text="PROCESSOR (CPU) SUBSYSTEM", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=14, pady=(12, 6))
        self.cpu_frame = tk.Frame(cpu_card, bg=COLORS["bg_card"])
        self.cpu_frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.cpu_labels: Dict[str, tk.Label] = {}
        for k in ["Processor Model", "Vendor", "Architecture", "Physical Cores", "Logical Processors", "Max Clock Frequency"]:
            r = tk.Frame(self.cpu_frame, bg=COLORS["bg_card"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=k, font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"], width=18, anchor="w").pack(side="left")
            val = tk.Label(r, text="Detecting...", font=FONTS["body_small"], fg=COLORS["text_primary"], bg=COLORS["bg_card"], anchor="w")
            val.pack(side="left", fill="x", expand=True)
            self.cpu_labels[k] = val

        # RAM Slots Card
        ram_card = tk.Frame(row1, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        ram_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(ram_card, text="PHYSICAL RAM MODULES (DIMMs)", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=14, pady=(12, 6))
        
        # RAM Modules Tree
        ram_cols = ("slot", "capacity", "speed", "manufacturer")
        self.tree_ram = ttk.Treeview(ram_card, columns=ram_cols, show="headings", height=4)
        self.tree_ram.heading("slot", text="Slot")
        self.tree_ram.heading("capacity", text="Capacity")
        self.tree_ram.heading("speed", text="Clock Speed")
        self.tree_ram.heading("manufacturer", text="Vendor")
        self.tree_ram.column("slot", width=90, anchor="w")
        self.tree_ram.column("capacity", width=70, anchor="center")
        self.tree_ram.column("speed", width=80, anchor="center")
        self.tree_ram.column("manufacturer", width=120, anchor="w")
        self.tree_ram.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # ==========================================
        # 2. STORAGE DRIVES & NETWORK ADAPTERS
        # ==========================================
        row2 = tk.Frame(content, bg=COLORS["bg_root"])
        row2.pack(fill="x", padx=20, pady=(0, 15))
        row2.columnconfigure(0, weight=1)
        row2.columnconfigure(1, weight=1)

        # Storage Physical Drives
        disk_card = tk.Frame(row2, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        disk_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(disk_card, text="PHYSICAL STORAGE DRIVES", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=14, pady=(12, 6))
        disk_cols = ("model", "media", "size", "status")
        self.tree_disks = ttk.Treeview(disk_card, columns=disk_cols, show="headings", height=4)
        self.tree_disks.heading("model", text="Drive Model")
        self.tree_disks.heading("media", text="Type")
        self.tree_disks.heading("size", text="Size")
        self.tree_disks.heading("status", text="SMART")
        self.tree_disks.column("model", width=150, anchor="w")
        self.tree_disks.column("media", width=80, anchor="center")
        self.tree_disks.column("size", width=70, anchor="center")
        self.tree_disks.column("status", width=60, anchor="center")
        self.tree_disks.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # Network Interfaces
        net_card = tk.Frame(row2, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        net_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(net_card, text="NETWORK ADAPTER HARDWARE", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=14, pady=(12, 6))
        net_cols = ("name", "mac", "speed")
        self.tree_nic = ttk.Treeview(net_card, columns=net_cols, show="headings", height=4)
        self.tree_nic.heading("name", text="Adapter Hardware Name")
        self.tree_nic.heading("mac", text="MAC Address")
        self.tree_nic.heading("speed", text="Link Speed")
        self.tree_nic.column("name", width=180, anchor="w")
        self.tree_nic.column("mac", width=110, anchor="center")
        self.tree_nic.column("speed", width=80, anchor="center")
        self.tree_nic.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # ==========================================
        # 3. USB PERIPHERALS & POWER / GPU
        # ==========================================
        row3 = tk.Frame(content, bg=COLORS["bg_root"])
        row3.pack(fill="x", padx=20, pady=(0, 20))
        row3.columnconfigure(0, weight=1)
        row3.columnconfigure(1, weight=1)

        # USB Devices
        usb_card = tk.Frame(row3, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        usb_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(usb_card, text="CONNECTED USB PERIPHERALS", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=14, pady=(12, 6))
        usb_cols = ("name", "manufacturer", "status")
        self.tree_usb = ttk.Treeview(usb_card, columns=usb_cols, show="headings", height=5)
        self.tree_usb.heading("name", text="Peripheral Device Name")
        self.tree_usb.heading("manufacturer", text="Manufacturer")
        self.tree_usb.heading("status", text="Status")
        self.tree_usb.column("name", width=180, anchor="w")
        self.tree_usb.column("manufacturer", width=100, anchor="w")
        self.tree_usb.column("status", width=60, anchor="center")
        self.tree_usb.pack(fill="both", expand=True, padx=14, pady=(0, 12))

        # Battery / Display Card
        pwr_card = tk.Frame(row3, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        pwr_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))

        tk.Label(pwr_card, text="GRAPHICS (GPU) & POWER SUBSYSTEM", font=FONTS["title_card"], fg=COLORS["primary"], bg=COLORS["bg_card"]).pack(anchor="w", padx=14, pady=(12, 6))
        self.pwr_frame = tk.Frame(pwr_card, bg=COLORS["bg_card"])
        self.pwr_frame.pack(fill="both", expand=True, padx=14, pady=(0, 12))
        self.pwr_labels: Dict[str, tk.Label] = {}
        for k in ["Display GPU", "Resolution", "VRAM Buffer", "Driver Version", "Power Source", "Battery Charge"]:
            r = tk.Frame(self.pwr_frame, bg=COLORS["bg_card"])
            r.pack(fill="x", pady=2)
            tk.Label(r, text=k, font=FONTS["body_small"], fg=COLORS["text_secondary"], bg=COLORS["bg_card"], width=16, anchor="w").pack(side="left")
            val = tk.Label(r, text="Detecting...", font=FONTS["body_small"], fg=COLORS["text_primary"], bg=COLORS["bg_card"], anchor="w")
            val.pack(side="left", fill="x", expand=True)
            self.pwr_labels[k] = val

    def update_device_data(self, dev: Dict[str, Any]):
        """Populates hardware views from real device diagnostics."""
        if not dev:
            return

        # CPU
        cpu = dev.get("cpu", {})
        self.cpu_labels["Processor Model"].config(text=cpu.get("name", "Unknown"))
        self.cpu_labels["Vendor"].config(text=cpu.get("vendor", "Unknown"))
        self.cpu_labels["Architecture"].config(text=cpu.get("architecture", "Unknown"))
        self.cpu_labels["Physical Cores"].config(text=str(cpu.get("physical_cores", "1")))
        self.cpu_labels["Logical Processors"].config(text=str(cpu.get("logical_cores", "1")))
        self.cpu_labels["Max Clock Frequency"].config(text=str(cpu.get("max_clock_mhz", "N/A")))

        # RAM
        for item in self.tree_ram.get_children():
            self.tree_ram.delete(item)
        for mod in dev.get("ram_modules", {}).get("modules", []):
            self.tree_ram.insert("", "end", values=(
                mod.get("slot"),
                f"{mod.get('capacity_gb')} GB",
                f"{mod.get('speed_mhz')} MHz" if str(mod.get('speed_mhz')).isdigit() else mod.get('speed_mhz'),
                mod.get("manufacturer")
            ))

        # Storage
        for item in self.tree_disks.get_children():
            self.tree_disks.delete(item)
        for d in dev.get("storage_devices", []):
            self.tree_disks.insert("", "end", values=(
                d.get("model"),
                d.get("media_type"),
                f"{d.get('size_gb')} GB" if str(d.get('size_gb')).replace('.', '', 1).isdigit() else d.get('size_gb'),
                d.get("status")
            ))

        # Network
        for item in self.tree_nic.get_children():
            self.tree_nic.delete(item)
        for n in dev.get("network_adapters", []):
            self.tree_nic.insert("", "end", values=(
                n.get("name"),
                n.get("mac"),
                n.get("speed_bps")
            ))

        # USB
        for item in self.tree_usb.get_children():
            self.tree_usb.delete(item)
        for u in dev.get("usb_devices", []):
            self.tree_usb.insert("", "end", values=(
                u.get("name"),
                u.get("manufacturer"),
                u.get("status")
            ))

        # GPU & Battery
        gpus = dev.get("display", [])
        if gpus:
            g = gpus[0]
            self.pwr_labels["Display GPU"].config(text=g.get("name", "Standard Display"))
            self.pwr_labels["Resolution"].config(text=g.get("resolution", "Standard"))
            self.pwr_labels["VRAM Buffer"].config(text=f"{g.get('vram_mb')} MB" if str(g.get('vram_mb')).isdigit() else str(g.get('vram_mb')))
            self.pwr_labels["Driver Version"].config(text=g.get("driver_version", "N/A"))

        bat = dev.get("battery", {})
        if bat.get("present"):
            self.pwr_labels["Power Source"].config(text="AC Adapter (Charging)" if bat.get("power_plugged") else "Battery (Discharging)")
            self.pwr_labels["Battery Charge"].config(text=f"{bat.get('percent')}% remaining")
        else:
            self.pwr_labels["Power Source"].config(text="AC Main Power (Desktop Workstation)")
            self.pwr_labels["Battery Charge"].config(text="No battery detected (Desktop PC)")
