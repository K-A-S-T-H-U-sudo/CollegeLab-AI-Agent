"""
Real System Health Diagnostics Module for CollegeLab AI Agent.
Collects real CPU, RAM, Disk, Process, Service, and Uptime metrics on the local machine.
Evaluates metrics against defined thresholds and avoids false hardware fault claims.
"""

import os
import time
import datetime
from typing import Dict, List, Any
import psutil
from config import lab_config

CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


class SystemHealthDiagnostic:
    """Performs real system resource utilization inspection."""

    def __init__(self):
        self.thresholds = lab_config.thresholds

    def run_full_diagnosis(self) -> Dict[str, Any]:
        """Runs complete system health assessment with real metrics."""
        cpu_data = self.get_cpu_metrics()
        ram_data = self.get_ram_metrics()
        disk_data = self.get_disk_metrics()
        uptime_data = self.get_uptime_metrics()
        processes_data = self.get_top_processes(count=5)
        services_data = self.check_core_services()

        # Classifications based on threshold specifications
        cpu_status = self._classify_cpu(cpu_data["percent"])
        ram_status = self._classify_ram(ram_data["percent"])
        disk_status = self._classify_disks(disk_data["partitions"])

        # Determine overall system health
        statuses = [cpu_status, ram_status, disk_status]
        if "Critical" in statuses:
            overall_status = "Critical"
        elif "Warning" in statuses or "Moderate" in statuses:
            overall_status = "Warning"
        else:
            overall_status = "Healthy"

        return {
            "category": "System Health",
            "cpu": cpu_data,
            "cpu_status": cpu_status,
            "ram": ram_data,
            "ram_status": ram_status,
            "disk": disk_data,
            "disk_status": disk_status,
            "uptime": uptime_data,
            "top_processes": processes_data,
            "services": services_data,
            "overall_status": overall_status,
            "disclaimer": "Resource utilization reflects workload. High resource usage alone does NOT indicate physical hardware damage."
        }

    def get_cpu_metrics(self) -> Dict[str, Any]:
        """Reads CPU utilization, core count, and frequency."""
        # psutil.cpu_percent with a non-zero interval gives accurate immediate read
        cpu_pct = psutil.cpu_percent(interval=0.3)
        per_cpu = psutil.cpu_percent(interval=None, percpu=True)
        freq = psutil.cpu_freq()

        return {
            "percent": cpu_pct,
            "per_core_percent": per_cpu,
            "physical_cores": psutil.cpu_count(logical=False) or 1,
            "logical_cores": psutil.cpu_count(logical=True) or 1,
            "current_freq_mhz": round(freq.current, 1) if freq else None,
            "max_freq_mhz": round(freq.max, 1) if freq else None
        }

    def get_ram_metrics(self) -> Dict[str, Any]:
        """Reads physical memory and swap statistics."""
        vm = psutil.virtual_memory()
        swap = psutil.swap_memory()

        return {
            "total_gb": round(vm.total / (1024 ** 3), 2),
            "available_gb": round(vm.available / (1024 ** 3), 2),
            "used_gb": round(vm.used / (1024 ** 3), 2),
            "percent": vm.percent,
            "swap_total_gb": round(swap.total / (1024 ** 3), 2),
            "swap_used_gb": round(swap.used / (1024 ** 3), 2),
            "swap_percent": swap.percent
        }

    def get_disk_metrics(self) -> Dict[str, Any]:
        """Inspects all mounted storage partitions."""
        partitions = []
        total_storage_bytes = 0
        total_used_bytes = 0
        total_free_bytes = 0

        for part in psutil.disk_partitions(all=False):
            # Skip CD-ROM or unmounted drives
            if os.name == 'nt' and ('cdrom' in part.opts or part.fstype == ''):
                continue
            try:
                usage = psutil.disk_usage(part.mountpoint)
                total_storage_bytes += usage.total
                total_used_bytes += usage.used
                total_free_bytes += usage.free

                partitions.append({
                    "device": part.device,
                    "mountpoint": part.mountpoint,
                    "fstype": part.fstype,
                    "total_gb": round(usage.total / (1024 ** 3), 2),
                    "used_gb": round(usage.used / (1024 ** 3), 2),
                    "free_gb": round(usage.free / (1024 ** 3), 2),
                    "percent": usage.percent
                })
            except (PermissionError, FileNotFoundError):
                continue

        aggregate_pct = round((total_used_bytes / total_storage_bytes * 100), 1) if total_storage_bytes > 0 else 0.0

        return {
            "aggregate_total_gb": round(total_storage_bytes / (1024 ** 3), 2),
            "aggregate_used_gb": round(total_used_bytes / (1024 ** 3), 2),
            "aggregate_free_gb": round(total_free_bytes / (1024 ** 3), 2),
            "aggregate_percent": aggregate_pct,
            "partitions": partitions
        }

    def get_uptime_metrics(self) -> Dict[str, Any]:
        """Calculates system uptime since last boot."""
        boot_timestamp = psutil.boot_time()
        boot_dt = datetime.datetime.fromtimestamp(boot_timestamp)
        now_dt = datetime.datetime.now()
        uptime_delta = now_dt - boot_dt

        days = uptime_delta.days
        hours, remainder = divmod(uptime_delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        uptime_formatted = f"{days}d {hours}h {minutes}m {seconds}s"
        return {
            "boot_time": boot_dt.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime_seconds": int(uptime_delta.total_seconds()),
            "uptime_formatted": uptime_formatted,
            "days": days,
            "hours": hours,
            "minutes": minutes
        }

    def get_top_processes(self, count: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Finds processes using the highest CPU and Memory."""
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'memory_info']):
            try:
                p_info = p.info
                mem_mb = round(p_info['memory_info'].rss / (1024 * 1024), 1) if p_info.get('memory_info') else 0
                procs.append({
                    "pid": p_info['pid'],
                    "name": p_info['name'] or f"PID {p_info['pid']}",
                    "cpu_percent": p_info['cpu_percent'] or 0.0,
                    "memory_percent": round(p_info['memory_percent'] or 0.0, 1),
                    "memory_mb": mem_mb
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Sort top CPU and top Memory
        top_cpu = sorted(procs, key=lambda x: x['cpu_percent'], reverse=True)[:count]
        top_memory = sorted(procs, key=lambda x: x['memory_mb'], reverse=True)[:count]

        return {
            "by_cpu": top_cpu,
            "by_memory": top_memory
        }

    def check_core_services(self) -> Dict[str, Dict[str, Any]]:
        """Inspects status of critical Windows OS background services."""
        services = {
            "Spooler": "Print Spooler",
            "EventLog": "Windows Event Log",
            "wuauserv": "Windows Update",
            "WinDefend": "Microsoft Defender Antivirus Service"
        }
        res = {}
        for svc_name, desc in services.items():
            status = "unknown"
            is_running = False
            try:
                if os.name == "nt":
                    try:
                        s = psutil.win_service_get(svc_name)
                        status = s.status()
                        is_running = (status == "running")
                    except Exception:
                        status = "unavailable"
            except Exception:
                status = "error"
            res[svc_name] = {
                "display_name": desc,
                "status": status,
                "running": is_running
            }
        return res

    def _classify_cpu(self, pct: float) -> str:
        """Threshold: < 70% Normal/Healthy, 70-90% Moderate, > 90% High"""
        if pct > self.thresholds.get("cpu_high", 90.0):
            return "High"
        elif pct > self.thresholds.get("cpu_moderate", 70.0):
            return "Moderate"
        return "Healthy"

    def _classify_ram(self, pct: float) -> str:
        """Threshold: < 60% Healthy, 60-80% Moderate, > 80% High"""
        if pct > self.thresholds.get("ram_high", 80.0):
            return "High"
        elif pct > self.thresholds.get("ram_moderate", 60.0):
            return "Moderate"
        return "Healthy"

    def _classify_disks(self, partitions: List[Dict[str, Any]]) -> str:
        """Threshold: Free space < 5GB or usage > 95% is Critical, > 85% is Warning."""
        has_critical = False
        has_warning = False

        for part in partitions:
            pct = part["percent"]
            free_gb = part["free_gb"]
            if pct > self.thresholds.get("disk_critical_pct", 95.0) or free_gb < 2.0:
                has_critical = True
            elif pct > self.thresholds.get("disk_warning_pct", 85.0) or free_gb < self.thresholds.get("disk_min_free_gb", 5.0):
                has_warning = True

        if has_critical:
            return "Critical"
        if has_warning:
            return "Warning"
        return "Healthy"
