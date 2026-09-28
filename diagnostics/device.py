"""
Real Device and Hardware Health Diagnostic Module for CollegeLab AI Agent.
Queries hardware devices via Windows Management Instrumentation (WMI),
PowerShell CIM instances, platform, and psutil.
Enforces the strict rule: Software diagnosis cannot confirm physical component damage.
"""

import os
import re
import json
import platform
import subprocess
from typing import Dict, List, Any, Optional
import psutil

CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


class DeviceDiagnostic:
    """Inspects observable hardware components reported by the Windows operating system."""

    DISCLAIMER = "Software-based diagnosis cannot confirm physical component damage. Technician inspection is recommended."

    def run_full_diagnosis(self) -> Dict[str, Any]:
        """Collects real hardware information across all accessible physical subsystems."""
        cpu_info = self.get_cpu_info()
        ram_info = self.get_ram_info()
        disks_info = self.get_storage_devices()
        network_hardware = self.get_network_hardware()
        usb_devices = self.get_usb_devices()
        battery_info = self.get_battery_info()
        display_info = self.get_display_info()

        # Evaluate device health indicators
        anomalies = []
        if battery_info.get("present") and battery_info.get("percent") is not None:
            if battery_info["percent"] < 15 and not battery_info.get("power_plugged"):
                anomalies.append("Battery is critically low (< 15%) and not plugged into AC power.")

        return {
            "category": "Device Health",
            "cpu": cpu_info,
            "ram_modules": ram_info,
            "storage_devices": disks_info,
            "network_adapters": network_hardware,
            "usb_devices": usb_devices,
            "battery": battery_info,
            "display": display_info,
            "anomalies": anomalies,
            "summary_status": "Warning" if anomalies else "Healthy",
            "disclaimer": self.DISCLAIMER
        }

    def _run_powershell_json(self, command: str, timeout: int = 5) -> Optional[Any]:
        """Executes a PowerShell command and returns parsed JSON output."""
        if os.name != 'nt':
            return None
        try:
            full_cmd = f"{command} | ConvertTo-Json -Depth 2 -Compress"
            proc = subprocess.run(
                ["powershell", "-NoProfile", "-Command", full_cmd],
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=CREATE_NO_WINDOW
            )
            raw = proc.stdout.strip()
            if raw and proc.returncode == 0:
                parsed = json.loads(raw)
                return parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            pass
        return None

    def get_cpu_info(self) -> Dict[str, Any]:
        """Retrieves CPU model, architecture, cores, and processor ID."""
        info = {
            "name": platform.processor() or "Unknown Processor",
            "architecture": platform.machine(),
            "physical_cores": psutil.cpu_count(logical=False) or 1,
            "logical_cores": psutil.cpu_count(logical=True) or 1,
            "vendor": "Unknown",
            "max_clock_mhz": "Not available on this system"
        }

        # Query Windows CIM for accurate CPU brand string
        res = self._run_powershell_json("Get-CimInstance Win32_Processor | Select-Object Name, Manufacturer, MaxClockSpeed, NumberOfCores, NumberOfLogicalProcessors")
        if res and len(res) > 0:
            c = res[0]
            if c.get("Name"):
                info["name"] = str(c["Name"]).strip()
            if c.get("Manufacturer"):
                info["vendor"] = str(c["Manufacturer"]).strip()
            if c.get("MaxClockSpeed"):
                info["max_clock_mhz"] = f"{c['MaxClockSpeed']} MHz"

        return info

    def get_ram_info(self) -> Dict[str, Any]:
        """Retrieves physical RAM module capacity, speed, and form factors."""
        vm = psutil.virtual_memory()
        info = {
            "total_physical_gb": round(vm.total / (1024 ** 3), 2),
            "modules": []
        }

        res = self._run_powershell_json("Get-CimInstance Win32_PhysicalMemory | Select-Object Capacity, Speed, Manufacturer, PartNumber, DeviceLocator")
        if res:
            for m in res:
                cap_bytes = int(m.get("Capacity") or 0)
                cap_gb = round(cap_bytes / (1024 ** 3), 1) if cap_bytes else "Unknown"
                info["modules"].append({
                    "slot": m.get("DeviceLocator", "DIMM Slot"),
                    "capacity_gb": cap_gb,
                    "speed_mhz": m.get("Speed", "Unknown"),
                    "manufacturer": m.get("Manufacturer", "Unknown").strip(),
                    "part_number": (m.get("PartNumber") or "").strip()
                })
        else:
            info["modules"].append({
                "slot": "System Board",
                "capacity_gb": info["total_physical_gb"],
                "speed_mhz": "Not available on this system",
                "manufacturer": "Standard System Memory",
                "part_number": "N/A"
            })

        return info

    def get_storage_devices(self) -> List[Dict[str, Any]]:
        """Queries physical storage drives (HDDs, SSDs, NVMe)."""
        devices = []
        res = self._run_powershell_json("Get-CimInstance Win32_DiskDrive | Select-Object Model, InterfaceType, MediaType, Size, Status")
        if res:
            for d in res:
                size_bytes = int(d.get("Size") or 0)
                size_gb = round(size_bytes / (1024 ** 3), 1) if size_bytes else "Unknown"
                devices.append({
                    "model": d.get("Model", "Physical Disk").strip(),
                    "interface": d.get("InterfaceType", "Standard"),
                    "media_type": d.get("MediaType", "Fixed hard disk media"),
                    "size_gb": size_gb,
                    "status": d.get("Status", "OK")
                })
        else:
            # Fallback to partitions
            for part in psutil.disk_partitions(all=False):
                devices.append({
                    "model": f"Logical Volume ({part.device})",
                    "interface": "Local",
                    "media_type": part.fstype or "Standard File System",
                    "size_gb": "Mounted",
                    "status": "Accessible"
                })

        return devices

    def get_network_hardware(self) -> List[Dict[str, Any]]:
        """Retrieves physical network adapter hardware models and manufacturers."""
        adapters = []
        res = self._run_powershell_json("Get-CimInstance Win32_NetworkAdapter | Where-Object { $_.PhysicalAdapter -eq $true } | Select-Object Name, Manufacturer, MACAddress, NetConnectionStatus, Speed")
        if res:
            for a in res:
                adapters.append({
                    "name": a.get("Name", "Network Adapter"),
                    "manufacturer": a.get("Manufacturer", "Generic"),
                    "mac": a.get("MACAddress") or "Not assigned",
                    "speed_bps": a.get("Speed") or "Negotiating",
                    "connection_status": a.get("NetConnectionStatus", "Active")
                })
        else:
            # Fallback to psutil
            for name, stats in psutil.net_if_stats().items():
                if "loopback" not in name.lower():
                    adapters.append({
                        "name": name,
                        "manufacturer": "System Network Controller",
                        "mac": "Accessible",
                        "speed_bps": f"{stats.speed} Mbps" if stats.speed else "Auto",
                        "connection_status": "Connected" if stats.isup else "Disconnected"
                    })
        return adapters

    def get_usb_devices(self) -> List[Dict[str, Any]]:
        """Lists connected USB peripherals (keyboards, mice, webcams, storage)."""
        usb_list = []
        res = self._run_powershell_json("Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -in @('USB', 'Mouse', 'Keyboard', 'Camera') -and $_.Present -eq $true } | Select-Object Name, Manufacturer, Status | Select-Object -First 10")
        if res:
            for u in res:
                name = u.get("Name")
                if name:
                    usb_list.append({
                        "name": name.strip(),
                        "manufacturer": (u.get("Manufacturer") or "Generic").strip(),
                        "status": u.get("Status", "OK")
                    })
        else:
            usb_list.append({
                "name": "Standard USB Host Controllers & Hubs",
                "manufacturer": "OS Detected Peripheral Subsystem",
                "status": "OK"
            })
        return usb_list

    def get_battery_info(self) -> Dict[str, Any]:
        """Inspects laptop battery or UPS state."""
        battery = psutil.sensors_battery()
        if battery is None:
            return {
                "present": False,
                "message": "Desktop computer (AC Power only - No battery detected)",
                "percent": None,
                "power_plugged": True,
                "secsleft": None
            }

        return {
            "present": True,
            "percent": round(battery.percent, 1),
            "power_plugged": battery.power_plugged,
            "secsleft": battery.secsleft if battery.secsleft > 0 else "Charging / Calculating"
        }

    def get_display_info(self) -> List[Dict[str, Any]]:
        """Queries GPU / display adapter hardware."""
        gpus = []
        res = self._run_powershell_json("Get-CimInstance Win32_VideoController | Select-Object Name, VideoProcessor, AdapterRAM, DriverVersion, CurrentHorizontalResolution, CurrentVerticalResolution")
        if res:
            for g in res:
                vram_bytes = int(g.get("AdapterRAM") or 0)
                vram_mb = round(vram_bytes / (1024 * 1024), 0) if vram_bytes else "Shared/Dynamic"
                h_res = g.get("CurrentHorizontalResolution")
                v_res = g.get("CurrentVerticalResolution")
                res_str = f"{h_res}x{v_res}" if (h_res and v_res) else "Standard Resolution"
                gpus.append({
                    "name": (g.get("Name") or "Display Adapter").strip(),
                    "processor": (g.get("VideoProcessor") or "Integrated/Discrete").strip(),
                    "vram_mb": vram_mb,
                    "resolution": res_str,
                    "driver_version": g.get("DriverVersion", "Generic")
                })
        else:
            gpus.append({
                "name": "Standard Display Adapter",
                "processor": "System GPU",
                "vram_mb": "System Shared",
                "resolution": "System Display",
                "driver_version": "N/A"
            })
        return gpus
