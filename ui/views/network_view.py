"""
Network Diagnostics Detail View for CollegeLab AI Agent.
Displays real network adapters, IP configuration, DNS & Gateway latency, and core networking services.
"""

import tkinter as tk
from tkinter import ttk
from typing import Dict, Any
from ui.theme import COLORS, FONTS


class NetworkView(tk.Frame):
    """Deep-dive network diagnostic view."""

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
        tk.Label(hdr, text="NETWORK ADAPTERS & CONNECTIVITY SUBSYSTEM", font=FONTS["section_title"], fg=COLORS["text_primary"], bg=COLORS["bg_root"]).pack(side="left")

        # 1. IP Configuration & Latency Summary Card
        stat_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        stat_card.pack(fill="x", padx=20, pady=(0, 12))

        sc_inner = tk.Frame(stat_card, bg=COLORS["bg_card"])
        sc_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(sc_inner, text="IP ROUTING & PROBE MEASUREMENTS", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        grid = tk.Frame(sc_inner, bg=COLORS["bg_card"])
        grid.pack(fill="x")
        grid.columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_ip = self._create_metric_cell(grid, 0, 0, "IPv4 Address", "Detecting...")
        self.lbl_gw = self._create_metric_cell(grid, 0, 1, "Default Gateway", "Detecting...")
        self.lbl_dns = self._create_metric_cell(grid, 0, 2, "DNS Servers", "Detecting...")
        self.lbl_dhcp = self._create_metric_cell(grid, 0, 3, "DHCP Enabled", "Detecting...")

        self.lbl_gw_lat = self._create_metric_cell(grid, 1, 0, "Gateway Latency", "--- ms")
        self.lbl_dns_time = self._create_metric_cell(grid, 1, 1, "DNS Query Time", "--- ms")
        self.lbl_inet_lat = self._create_metric_cell(grid, 1, 2, "Internet Ping Latency", "--- ms")
        self.lbl_loss = self._create_metric_cell(grid, 1, 3, "Packet Loss", "--- %")

        # 2. Network Adapters Table
        nic_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        nic_card.pack(fill="x", padx=20, pady=(0, 12))

        nc_inner = tk.Frame(nic_card, bg=COLORS["bg_card"])
        nc_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(nc_inner, text="DETECTED NETWORK INTERFACES", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        cols = ("name", "type", "status", "speed", "mac", "ipv4")
        self.tree_nic = ttk.Treeview(nc_inner, columns=cols, show="headings", height=4)
        self.tree_nic.heading("name", text="Adapter Name")
        self.tree_nic.heading("type", text="Type")
        self.tree_nic.heading("status", text="Link Status")
        self.tree_nic.heading("speed", text="Link Speed")
        self.tree_nic.heading("mac", text="MAC Address")
        self.tree_nic.heading("ipv4", text="Assigned IPv4")

        self.tree_nic.column("name", width=180, anchor="w")
        self.tree_nic.column("type", width=90, anchor="center")
        self.tree_nic.column("status", width=80, anchor="center")
        self.tree_nic.column("speed", width=80, anchor="center")
        self.tree_nic.column("mac", width=110, anchor="center")
        self.tree_nic.column("ipv4", width=110, anchor="center")
        self.tree_nic.pack(fill="x")

        # 3. Windows Network Services Table
        svc_card = tk.Frame(content, bg=COLORS["bg_card"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        svc_card.pack(fill="x", padx=20, pady=(0, 15))

        svc_inner = tk.Frame(svc_card, bg=COLORS["bg_card"])
        svc_inner.pack(fill="x", padx=16, pady=12)

        tk.Label(svc_inner, text="CORE WINDOWS NETWORKING SERVICES", font=FONTS["card_title"], fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(anchor="w", pady=(0, 6))

        svc_cols = ("service", "desc", "state", "startup")
        self.tree_svc = ttk.Treeview(svc_inner, columns=svc_cols, show="headings", height=4)
        self.tree_svc.heading("service", text="Service Name")
        self.tree_svc.heading("desc", text="Description")
        self.tree_svc.heading("state", text="Current State")
        self.tree_svc.heading("startup", text="Startup Type")

        self.tree_svc.column("service", width=140, anchor="w")
        self.tree_svc.column("desc", width=220, anchor="w")
        self.tree_svc.column("state", width=100, anchor="center")
        self.tree_svc.column("startup", width=100, anchor="center")
        self.tree_svc.pack(fill="x")

    def _create_metric_cell(self, parent, r, c, title, initial_val) -> tk.Label:
        box = tk.Frame(parent, bg=COLORS["bg_card_alt"], bd=1, relief="solid", highlightbackground=COLORS["border"], highlightthickness=1)
        box.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")

        tk.Label(box, text=title, font=FONTS["caption"], fg=COLORS["text_muted"], bg=COLORS["bg_card_alt"]).pack(anchor="w", padx=8, pady=(6, 1))
        lbl = tk.Label(box, text=initial_val, font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["bg_card_alt"])
        lbl.pack(anchor="w", padx=8, pady=(0, 6))
        return lbl

    def update_network_data(self, net: Dict[str, Any]):
        """Populates network detail widgets with real sensor measurements."""
        if not net:
            return

        ip_info = net.get("ip_configuration", {})
        self.lbl_ip.config(text=ip_info.get("primary_ip") or "None")
        self.lbl_gw.config(text=ip_info.get("gateway") or "Unreachable")
        dns_list = ip_info.get("dns_servers", [])
        self.lbl_dns.config(text=", ".join(dns_list[:2]) if dns_list else "None")
        dhcp = ip_info.get("dhcp_enabled")
        self.lbl_dhcp.config(text="Yes" if dhcp is True else ("No" if dhcp is False else "Unknown"))

        gw_lat = net.get("gateway_latency_ms")
        self.lbl_gw_lat.config(text=f"{gw_lat:.1f} ms" if gw_lat is not None else "Timeout")

        dns_time = net.get("dns_resolve_time_ms")
        self.lbl_dns_time.config(text=f"{dns_time:.1f} ms" if dns_time is not None else "Failed")

        inet_lat = net.get("internet_latency_ms")
        self.lbl_inet_lat.config(text=f"{inet_lat:.1f} ms" if inet_lat is not None else "Timeout")

        loss = net.get("packet_loss_pct", 0.0)
        self.lbl_loss.config(text=f"{loss:.0f} %")

        # Populate Adapters
        for item in self.tree_nic.get_children():
            self.tree_nic.delete(item)
        for a in net.get("adapters", []):
            st = "Link Up" if a.get("is_up") else "Link Down"
            speed = f"{a.get('speed_mbps')} Mbps" if a.get('speed_mbps') else "Auto"
            self.tree_nic.insert("", "end", values=(
                a.get("name"),
                a.get("type"),
                st,
                speed,
                a.get("mac"),
                a.get("ipv4")
            ))

        # Populate Services
        for item in self.tree_svc.get_children():
            self.tree_svc.delete(item)
        for svc_name, s_data in net.get("services", {}).items():
            st_text = "Running [OK]" if s_data.get("running") else f"Stopped ({s_data.get('status')})"
            self.tree_svc.insert("", "end", values=(
                svc_name,
                s_data.get("display_name"),
                st_text,
                s_data.get("start_type", "Automatic")
            ))
