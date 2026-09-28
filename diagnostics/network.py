"""
Real Network Diagnostics Module for CollegeLab AI Agent.
Inspects physical and logical network state on Windows systems:
Adapters, IP/APIPA, Gateway, DNS, Latency, Packet Loss, Services, and Multi-stage connectivity.
"""

import os
import re
import socket
import subprocess
import time
from typing import Dict, List, Any, Optional, Tuple
import psutil

# Windows flag to suppress terminal window flashes when invoking subprocess
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


class NetworkDiagnostic:
    """
    Performs real, multi-stage network diagnostics on the local computer.
    Stages:
      Adapter -> IP Address -> Default Gateway -> DNS Resolution -> Internet Connectivity
    """

    def __init__(self):
        self.stage_results = {
            "adapter": False,
            "ip": False,
            "gateway": False,
            "dns": False,
            "internet": False
        }
        self.failed_stage = None

    def run_full_diagnosis(self) -> Dict[str, Any]:
        """Runs the complete suite of network tests and returns structured real data."""
        adapters = self.get_adapters()
        ip_info = self.get_ip_configuration()
        services = self.check_network_services()
        
        # Test 1: Adapter state
        adapter_ok = any(a.get("is_up") and not a.get("is_loopback") for a in adapters)
        self.stage_results["adapter"] = adapter_ok

        # Test 2: IP Configuration
        primary_ip = ip_info.get("primary_ip")
        is_apipa = ip_info.get("is_apipa", False)
        has_valid_ip = bool(primary_ip and not is_apipa and primary_ip != "127.0.0.1")
        self.stage_results["ip"] = has_valid_ip

        # Test 3: Gateway reachability
        gateway_ip = ip_info.get("gateway")
        gateway_reachable = False
        gateway_latency_ms = None
        if gateway_ip and gateway_ip != "0.0.0.0":
            gw_res = self.ping_host(gateway_ip, count=2, timeout_ms=1000)
            gateway_reachable = gw_res["success"]
            gateway_latency_ms = gw_res.get("avg_latency_ms")
        self.stage_results["gateway"] = gateway_reachable

        # Test 4: DNS Resolution & Public DNS Reachability
        dns_servers = ip_info.get("dns_servers", [])
        dns_resolution_ok, dns_resolve_time = self.test_dns_resolution(["google.com", "cloudflare.com", "wikipedia.org"])
        public_dns_reachable = self.test_socket_connect("8.8.8.8", 53, timeout=1.5) or self.test_socket_connect("1.1.1.1", 53, timeout=1.5)
        dns_overall_ok = dns_resolution_ok or (public_dns_reachable and gateway_reachable)
        self.stage_results["dns"] = dns_resolution_ok

        # Test 5: Internet Connectivity & Latency
        internet_ping = self.ping_host("8.8.8.8", count=3, timeout_ms=1500)
        http_ok = self.test_http_connectivity()
        internet_ok = internet_ping["success"] or http_ok
        self.stage_results["internet"] = internet_ok

        # Stage analysis: identify the exact breakdown point
        failed_stage = None
        stage_sequence = ["adapter", "ip", "gateway", "dns", "internet"]
        for stage in stage_sequence:
            if not self.stage_results[stage]:
                failed_stage = stage
                break
        self.failed_stage = failed_stage

        return {
            "category": "Network",
            "adapters": adapters,
            "ip_configuration": ip_info,
            "services": services,
            "gateway_reachable": gateway_reachable,
            "gateway_latency_ms": gateway_latency_ms,
            "dns_resolution_ok": dns_resolution_ok,
            "dns_resolve_time_ms": dns_resolve_time,
            "public_dns_reachable": public_dns_reachable,
            "internet_reachable": internet_ok,
            "internet_latency_ms": internet_ping.get("avg_latency_ms"),
            "packet_loss_pct": internet_ping.get("packet_loss_pct", 100.0 if not internet_ok else 0.0),
            "http_ok": http_ok,
            "stages": {
                "Adapter": "PASS" if self.stage_results["adapter"] else "FAIL",
                "IP Configuration": "PASS" if self.stage_results["ip"] else "FAIL",
                "Default Gateway": "PASS" if self.stage_results["gateway"] else "FAIL",
                "DNS Resolution": "PASS" if self.stage_results["dns"] else "FAIL",
                "Internet Access": "PASS" if self.stage_results["internet"] else "FAIL",
            },
            "failed_stage": failed_stage,
            "summary_status": "Healthy" if internet_ok and dns_resolution_ok else ("Warning" if gateway_reachable else "Critical")
        }

    def get_adapters(self) -> List[Dict[str, Any]]:
        """Enumerates real network interfaces, addresses, status and speeds."""
        adapters = []
        try:
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()

            for nic_name, nic_addrs in addrs.items():
                stat = stats.get(nic_name)
                is_up = stat.isup if stat else False
                speed_mbps = stat.speed if stat else 0
                mtu = stat.mtu if stat else 1500

                ipv4_list = []
                mac_address = "N/A"
                for addr in nic_addrs:
                    if addr.family == socket.AF_INET:
                        ipv4_list.append(addr.address)
                    elif hasattr(psutil, "AF_LINK") and addr.family == psutil.AF_LINK:
                        mac_address = addr.address

                # Determine adapter type (Wi-Fi, Ethernet, Loopback, Virtual)
                lower_name = nic_name.lower()
                is_loopback = "loopback" in lower_name or "127.0.0.1" in ipv4_list
                if "wi-fi" in lower_name or "wireless" in lower_name or "wlan" in lower_name:
                    nic_type = "Wi-Fi"
                elif "ethernet" in lower_name or "eth" in lower_name or "local area" in lower_name:
                    nic_type = "Ethernet"
                elif "vethernet" in lower_name or "virtual" in lower_name or "vmnet" in lower_name:
                    nic_type = "Virtual"
                elif is_loopback:
                    nic_type = "Loopback"
                else:
                    nic_type = "Network Adapter"

                adapters.append({
                    "name": nic_name,
                    "type": nic_type,
                    "is_up": is_up,
                    "speed_mbps": speed_mbps,
                    "mac": mac_address,
                    "ipv4": ipv4_list[0] if ipv4_list else "None",
                    "all_ipv4": ipv4_list,
                    "is_loopback": is_loopback
                })
        except Exception as e:
            print(f"[NetworkDiagnostic] Error querying adapters: {e}")

        return adapters

    def get_ip_configuration(self) -> Dict[str, Any]:
        """Queries IP, Subnet, Gateway, and DNS servers using ipconfig and system routing."""
        info = {
            "primary_ip": None,
            "subnet_mask": None,
            "gateway": None,
            "dns_servers": [],
            "dhcp_enabled": None,
            "is_apipa": False
        }

        # 1. Inspect local socket to determine outbound route interface
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(0.5)
            # Connecting to a public address (doesn't send packets) determines selected interface
            s.connect(("8.8.8.8", 80))
            info["primary_ip"] = s.getsockname()[0]
            s.close()
        except Exception:
            # Fallback to scanning interfaces for non-loopback IP
            addrs = psutil.net_if_addrs()
            for nic, addr_list in addrs.items():
                for a in addr_list:
                    if a.family == socket.AF_INET and not a.address.startswith("127."):
                        info["primary_ip"] = a.address
                        info["subnet_mask"] = a.netmask
                        break
                if info["primary_ip"]:
                    break

        if info["primary_ip"] and info["primary_ip"].startswith("169.254."):
            info["is_apipa"] = True

        # 2. Query Windows ipconfig /all to retrieve actual Gateway and DNS
        if os.name == "nt":
            try:
                cmd = ["ipconfig", "/all"]
                proc = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    creationflags=CREATE_NO_WINDOW
                )
                output = proc.stdout

                # Parse Default Gateway
                gw_matches = re.findall(r"Default Gateway[ .:]+:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", output)
                if gw_matches:
                    # Choose first valid non-zero gateway
                    for gw in gw_matches:
                        if gw != "0.0.0.0":
                            info["gateway"] = gw
                            break

                # Parse DNS Servers
                dns_matches = re.findall(r"DNS Servers[ .:]+:\s*([0-9]+\.[0-9]+\.[0-9]+\.[0-9]+)", output)
                if dns_matches:
                    info["dns_servers"] = list(dict.fromkeys(dns_matches))

                # Check DHCP Enabled
                if "DHCP Enabled. . . . . . . . . . . : Yes" in output:
                    info["dhcp_enabled"] = True
                elif "DHCP Enabled. . . . . . . . . . . : No" in output:
                    info["dhcp_enabled"] = False

            except Exception as e:
                print(f"[NetworkDiagnostic] Failed to parse ipconfig: {e}")

        # If gateway still None on Windows, try Get-NetRoute
        if not info["gateway"] and os.name == "nt":
            try:
                ps_cmd = "Get-CimInstance Win32_NetworkAdapterConfiguration -Filter 'IPEnabled=True' | Select-Object -ExpandProperty DefaultIPGateway"
                proc = subprocess.run(
                    ["powershell", "-NoProfile", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=4,
                    creationflags=CREATE_NO_WINDOW
                )
                gws = [line.strip() for line in proc.stdout.splitlines() if re.match(r"^\d+\.\d+\.\d+\.\d+$", line.strip())]
                if gws:
                    info["gateway"] = gws[0]
            except Exception:
                pass

        return info

    def ping_host(self, host: str, count: int = 2, timeout_ms: int = 1000) -> Dict[str, Any]:
        """Pings a target host and measures real latency and packet loss."""
        result = {
            "host": host,
            "success": False,
            "avg_latency_ms": None,
            "packet_loss_pct": 100.0,
            "raw_output": ""
        }
        if not host:
            return result

        try:
            if os.name == "nt":
                cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), host]
            else:
                cmd = ["ping", "-c", str(count), "-W", str(int(timeout_ms / 1000)), host]

            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=(count * timeout_ms / 1000.0) + 2.0,
                creationflags=CREATE_NO_WINDOW
            )
            result["raw_output"] = proc.stdout

            if proc.returncode == 0:
                result["success"] = True
                # Parse average latency on Windows: "Average = 14ms"
                avg_match = re.search(r"Average = (\d+)ms", proc.stdout)
                if avg_match:
                    result["avg_latency_ms"] = float(avg_match.group(1))
                else:
                    # Fallback check for time=XXms
                    times = re.findall(r"time[<=](\d+)ms", proc.stdout)
                    if times:
                        nums = [float(t) for t in times]
                        result["avg_latency_ms"] = sum(nums) / len(nums)
                    else:
                        result["avg_latency_ms"] = 1.0

                # Parse packet loss: "(0% loss)"
                loss_match = re.search(r"\((\d+)% loss\)", proc.stdout)
                if loss_match:
                    result["packet_loss_pct"] = float(loss_match.group(1))
                else:
                    result["packet_loss_pct"] = 0.0
            else:
                result["packet_loss_pct"] = 100.0

        except Exception as e:
            result["raw_output"] = f"Ping exception: {e}"

        return result

    def test_dns_resolution(self, test_domains: List[str]) -> Tuple[bool, Optional[float]]:
        """Tests DNS resolution speed and success for a list of domains."""
        successful_lookups = 0
        total_time_ms = 0.0

        for domain in test_domains:
            t0 = time.time()
            try:
                ip = socket.gethostbyname(domain)
                elapsed_ms = (time.time() - t0) * 1000.0
                if ip:
                    successful_lookups += 1
                    total_time_ms += elapsed_ms
            except Exception:
                pass

        if successful_lookups > 0:
            avg_time = round(total_time_ms / successful_lookups, 1)
            return True, avg_time
        return False, None

    def test_socket_connect(self, host: str, port: int, timeout: float = 1.5) -> bool:
        """Tests low-level TCP connectivity to a host:port."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((host, port))
            s.close()
            return True
        except Exception:
            return False

    def test_http_connectivity(self) -> bool:
        """Verifies HTTP/HTTPS outbound traffic reaches internet endpoints."""
        endpoints = [
            ("1.1.1.1", 80),
            ("8.8.8.8", 53),
            ("www.google.com", 80),
            ("www.cloudflare.com", 80)
        ]
        for host, port in endpoints:
            if self.test_socket_connect(host, port, timeout=1.5):
                return True
        return False

    def check_network_services(self) -> Dict[str, Dict[str, Any]]:
        """Checks status of essential Windows network services."""
        services_to_check = {
            "Dnscache": "DNS Client",
            "Dhcp": "DHCP Client",
            "LanmanWorkstation": "Workstation (LAN Networking)",
            "WlanSvc": "WLAN AutoConfig (Wi-Fi)",
            "NlaSvc": "Network Location Awareness"
        }
        status_map = {}

        for svc_name, desc in services_to_check.items():
            status = "Unknown"
            running = False
            start_type = "Unknown"
            try:
                if os.name == "nt":
                    # Use psutil win_service_get
                    try:
                        svc = psutil.win_service_get(svc_name)
                        info = svc.as_dict()
                        status = info.get("status", "unknown")
                        running = (status == "running")
                        start_type = info.get("start_type", "unknown")
                    except Exception:
                        # Fallback to sc query
                        proc = subprocess.run(
                            ["sc", "query", svc_name],
                            capture_output=True,
                            text=True,
                            timeout=2,
                            creationflags=CREATE_NO_WINDOW
                        )
                        if "RUNNING" in proc.stdout:
                            status = "running"
                            running = True
                        elif "STOPPED" in proc.stdout:
                            status = "stopped"
                            running = False
            except Exception as e:
                status = f"Query error: {e}"

            status_map[svc_name] = {
                "display_name": desc,
                "status": status,
                "running": running,
                "start_type": start_type
            }

        return status_map
