"""
System Health View for CollegeLab AI Agent.
Displays real CPU, RAM, storage volumes, uptime, top resource-consuming processes, and OS services.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from ui.theme import COLORS, FONTS


class SystemHealthView(tk.Frame):
    """Deep-dive system resource health and process inspection view."""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["bg_root"], **kwargs)
        self._build_ui()

    def _build_ui(self):
        canvas = tk.Canvas(self, bg=COLORS["bg_root"], bd=0, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS["bg_root"])

        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        content = scrollable

        # Header
        hdr = tk.Frame(content, bg=COLORS["bg_root"])
        hdr.pack(fill="x", padx=20, pady=(15, 10))
        tk.Label(hdr, text="SYSTEM RESOURCE HEALTH & WORKLOAD MONITOR", font=FONTS["section_title"], fg=COLORS["text_primary"], bg=COLORS["bg_root"]).pack(side="left")

        # 1. Resource Metrics Summary Card (CPU, RAM, Uptime)
        res_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        res_card.pack(fill="x", padx=20, pady=(0, 12))

        rc_inner = tk.Frame(res_card, bg=COLORS["bg_card"])
        rc_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(rc_inner, text="RESOURCE UTILIZATION & SYSTEM RUNTIME", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        grid = tk.Frame(rc_inner, bg=COLORS["bg_card"])
        grid.pack(fill="x")
        grid.columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_cpu = self._create_metric_cell(grid, 0, 0, "CPU Utilization", "-- %")
        self.lbl_cpu_cores = self._create_metric_cell(grid, 0, 1, "Cores / Threads", "-- / --")
        self.lbl_ram = self._create_metric_cell(grid, 0, 2, "RAM Utilization", "-- %")
        self.lbl_ram_free = self._create_metric_cell(grid, 0, 3, "Available RAM", "-- GB")

        self.lbl_uptime = self._create_metric_cell(grid, 1, 0, "System Uptime", "Calculating...")
        self.lbl_boot = self._create_metric_cell(grid, 1, 1, "Last Boot Time", "Detecting...")
        self.lbl_disk_agg = self._create_metric_cell(grid, 1, 2, "Storage Utilization", "-- %")
        self.lbl_disk_free = self._create_metric_cell(grid, 1, 3, "Free Storage Space", "-- GB")

        # 2. Storage Partitions Table
        disk_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        disk_card.pack(fill="x", padx=20, pady=(0, 12))

        dc_inner = tk.Frame(disk_card, bg=COLORS["bg_card"])
        dc_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(dc_inner, text="MOUNTED STORAGE VOLUMES", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        d_cols = ("drive", "mount", "fstype", "total", "used", "free", "percent", "status")
        self.tree_disks = ttk.Treeview(dc_inner, columns=d_cols, show="headings", height=3)
        self.tree_disks.heading("drive", text="Volume")
        self.tree_disks.heading("mount", text="Mount Point")
        self.tree_disks.heading("fstype", text="File System")
        self.tree_disks.heading("total", text="Total")
        self.tree_disks.heading("used", text="Used")
        self.tree_disks.heading("free", text="Free Space")
        self.tree_disks.heading("percent", text="Used %")
        self.tree_disks.heading("status", text="Health")

        self.tree_disks.column("drive", width=80, anchor="w")
        self.tree_disks.column("mount", width=90, anchor="w")
        self.tree_disks.column("fstype", width=90, anchor="center")
        self.tree_disks.column("total", width=80, anchor="center")
        self.tree_disks.column("used", width=80, anchor="center")
        self.tree_disks.column("free", width=80, anchor="center")
        self.tree_disks.column("percent", width=70, anchor="center")
        self.tree_disks.column("status", width=90, anchor="center")
        self.tree_disks.pack(fill="x")

        # 3. Top Active Processes Table
        proc_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        proc_card.pack(fill="x", padx=20, pady=(0, 15))

        pc_inner = tk.Frame(proc_card, bg=COLORS["bg_card"])
        pc_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(pc_inner, text="TOP RESOURCE-CONSUMING PROCESSES", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        p_cols = ("pid", "name", "cpu", "mem_mb", "mem_pct")
        self.tree_procs = ttk.Treeview(pc_inner, columns=p_cols, show="headings", height=5)
        self.tree_procs.heading("pid", text="PID")
        self.tree_procs.heading("name", text="Process Name")
        self.tree_procs.heading("cpu", text="CPU %")
        self.tree_procs.heading("mem_mb", text="Memory (MB)")
        self.tree_procs.heading("mem_pct", text="Memory %")

        self.tree_procs.column("pid", width=70, anchor="center")
        self.tree_procs.column("name", width=220, anchor="w")
        self.tree_procs.column("cpu", width=90, anchor="center")
        self.tree_procs.column("mem_mb", width=110, anchor="center")
        self.tree_procs.column("mem_pct", width=90, anchor="center")
        self.tree_procs.pack(fill="x")

    def _create_metric_cell(self, parent, r, c, title, initial_val) -> tk.Label:
        box = tk.Frame(parent, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        box.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        tk.Label(box, text=title, font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_card_alt"]).pack(anchor="w", padx=8, pady=(6, 1))
        lbl = tk.Label(box, text=initial_val, font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"])
        lbl.pack(anchor="w", padx=8, pady=(0, 6))
        return lbl

    def update_system_data(self, sys_data: Dict[str, Any]):
        """Populates system health widgets with real measurements."""
        if not sys_data:
            return

        cpu = sys_data.get("cpu", {})
        ram = sys_data.get("ram", {})
        disk = sys_data.get("disk", {})
        uptime = sys_data.get("uptime", {})

        # CPU
        self.lbl_cpu.config(text=f"{cpu.get('percent', 0.0):.1f} %")
        self.lbl_cpu_cores.config(text=f"{cpu.get('physical_cores', 1)} Cores / {cpu.get('logical_cores', 1)} Threads")

        # RAM
        self.lbl_ram.config(text=f"{ram.get('percent', 0.0):.1f} % ({ram.get('used_gb', 0)} GB used)")
        self.lbl_ram_free.config(text=f"{ram.get('available_gb', 0)} GB free")

        # Uptime
        self.lbl_uptime.config(text=uptime.get("uptime_formatted", "N/A"))
        self.lbl_boot.config(text=uptime.get("boot_time", "N/A"))

        # Storage Aggregates
        self.lbl_disk_agg.config(text=f"{disk.get('aggregate_percent', 0.0):.1f} %")
        self.lbl_disk_free.config(text=f"{disk.get('aggregate_free_gb', 0)} GB free")

        # Partitions
        for item in self.tree_disks.get_children():
            self.tree_disks.delete(item)
        for part in disk.get("partitions", []):
            st = "Normal" if part.get("percent", 0) < 85 else ("Warning" if part.get("percent", 0) < 95 else "Critical")
            self.tree_disks.insert("", "end", values=(
                part.get("device"),
                part.get("mountpoint"),
                part.get("fstype"),
                f"{part.get('total_gb')} GB",
                f"{part.get('used_gb')} GB",
                f"{part.get('free_gb')} GB",
                f"{part.get('percent')}%",
                st
            ))

        # Processes
        for item in self.tree_procs.get_children():
            self.tree_procs.delete(item)
        procs_cpu = sys_data.get("top_processes", {}).get("by_cpu", [])
        for p in procs_cpu:
            self.tree_procs.insert("", "end", values=(
                p.get("pid"),
                p.get("name"),
                f"{p.get('cpu_percent', 0):.1f}%",
                f"{p.get('memory_mb', 0)} MB",
                f"{p.get('memory_percent', 0):.1f}%"
            ))
