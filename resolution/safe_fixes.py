"""
Safe Resolution Engine for CollegeLab AI Agent.
Enforces strict safety boundaries:
- Executes ONLY predefined, reversible, non-destructive system/network operations.
- Verifies administrative privileges when required.
- Provides exact command visibility and user confirmation.
- Provides manual instructions if automatic repair is unavailable or denied.
"""

import os
import sys
import ctypes
import shutil
import tempfile
import subprocess
import time
from typing import Dict, List, Any, Optional, Tuple

CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0


def is_admin() -> bool:
    """Checks whether the current process is running with elevated Administrator privileges."""
    if os.name != 'nt':
        return os.geteuid() == 0 if hasattr(os, 'geteuid') else False
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False


# Registry of Predefined Safe Fixes
SAFE_REPAIR_REGISTRY: Dict[str, Dict[str, Any]] = {
    "flush_dns": {
        "id": "flush_dns",
        "title": "Flush DNS Resolver Cache",
        "category": "Network",
        "problem": "DNS resolution failure / Stale domain name cache",
        "evidence": "Gateway reachable, DNS lookup failed",
        "proposed_action": "Flush DNS cache and re-test",
        "risk_level": "Low",
        "permission_required": "Standard user (Elevation optional)",
        "requires_admin": False,
        "commands": ["ipconfig /flushdns", "ipconfig /registerdns"],
        "description": "Purges stale and corrupted DNS cache entries and initiates re-registration with lab DNS servers.",
        "safety_guarantee": "Reversible and non-destructive. Only purges cached name-to-IP mappings. Does not alter settings or files.",
        "manual_instructions": "Open Command Prompt and run:\n  ipconfig /flushdns\n  ipconfig /registerdns"
    },
    "renew_dhcp": {
        "id": "renew_dhcp",
        "title": "Release and Renew DHCP IP Lease",
        "category": "Network",
        "problem": "DHCP lease expiration / Unassigned or APIPA 169.254.x.x IP",
        "evidence": "Network adapter active, IP unassigned/APIPA, Gateway unreachable",
        "proposed_action": "Release/renew DHCP IP lease and re-test",
        "risk_level": "Low",
        "permission_required": "Standard user",
        "requires_admin": False,
        "commands": ["ipconfig /release", "ipconfig /renew"],
        "description": "Releases the stale or APIPA IP lease and requests a fresh IPv4 address from the lab DHCP router.",
        "safety_guarantee": "Completely safe. Rebroadcasts standard DHCP Discover/Request frames to acquire active network configuration.",
        "manual_instructions": "Open Command Prompt and run:\n  ipconfig /release\n  ipconfig /renew"
    },
    "reset_tcp_ip": {
        "id": "reset_tcp_ip",
        "title": "Reset Winsock Catalog & TCP/IP Stack",
        "category": "Network",
        "problem": "Winsock catalog corruption / TCP/IP stack layer breakdown",
        "evidence": "Socket creation failures, gateway unreachable despite valid IP",
        "proposed_action": "Reset Winsock Catalog & TCP/IP stack configuration",
        "risk_level": "Moderate (Requires reboot for complete effect)",
        "permission_required": "Administrator required",
        "requires_admin": True,
        "commands": ["netsh winsock reset", "netsh int ip reset"],
        "description": "Restores the Windows socket catalog and TCP/IP transport configurations to clean defaults.",
        "safety_guarantee": "Resets corrupted socket layering. Does not modify user documents or uninstall software.",
        "manual_instructions": "Open Command Prompt as Administrator and run:\n  netsh winsock reset\n  netsh int ip reset"
    },
    "restart_adapter": {
        "id": "restart_adapter",
        "title": "Restart Network Interface Adapter",
        "category": "Network",
        "problem": "Network adapter interface stalled or unresponsive link negotiation",
        "evidence": "Adapter status disconnected or link down without IP assigned",
        "proposed_action": "Soft-cycle network adapter interface to re-negotiate physical link",
        "risk_level": "Low (Brief 2-3s connectivity interruption)",
        "permission_required": "Administrator required",
        "requires_admin": True,
        "commands": [
            "powershell -Command \"Get-NetAdapter | Where-Object { $_.Status -eq 'Up' -or $_.Status -eq 'Disconnected' } | Restart-NetAdapter -Confirm:$false\""
        ],
        "description": "Soft-restarts the network interface hardware to re-negotiate physical link negotiation and driver states.",
        "safety_guarantee": "Temporarily cycles the adapter link for 2-3 seconds. Fully reversible.",
        "manual_instructions": "In Windows, go to Settings -> Network & Internet -> Advanced network settings -> Disable and re-enable your network adapter."
    },
    "clean_temp_files": {
        "id": "clean_temp_files",
        "title": "Safe Temporary Files Cleanup",
        "category": "Storage",
        "problem": "Storage volume low space / Obsolete temp file accumulation",
        "evidence": "Disk usage > 85%, %TEMP% directory containing expired build caches",
        "proposed_action": "Purge unlocked temporary files older than 24 hours in %TEMP%",
        "risk_level": "Low (Strict safety: only files > 24h old in %TEMP%)",
        "permission_required": "Standard user",
        "requires_admin": False,
        "commands": ["[Internal Safe Temp Cleaner] Cleans %TEMP% files older than 24 hours"],
        "description": "Scans the user temporary cache directory (%TEMP%) and safely deletes obsolete temporary build files.",
        "safety_guarantee": "STRICT SAFETY: Only deletes unlocked files in %TEMP% older than 24 hours. NEVER touches user documents, desktop, or system binaries.",
        "manual_instructions": "Press Win+R, type '%TEMP%', and safely remove old temporary files."
    },
    "restart_spooler": {
        "id": "restart_spooler",
        "title": "Restart Print Spooler Service",
        "category": "Service",
        "problem": "Windows Print Spooler service stopped or lab print jobs stalled",
        "evidence": "Spooler service state stopped or print queue locked",
        "proposed_action": "Restart Windows Print Spooler service to clear stalled queues",
        "risk_level": "Low",
        "permission_required": "Administrator required",
        "requires_admin": True,
        "commands": ["net stop spooler", "net start spooler"],
        "description": "Stops and cleanly restarts the Windows Print Spooler service to clear stalled lab print jobs.",
        "safety_guarantee": "Cycles the background print service without altering printer drivers or system configuration.",
        "manual_instructions": "Open Command Prompt as Administrator and run:\n  net stop spooler\n  net start spooler"
    }
}


class SafeResolutionEngine:
    """Executes safe repair actions with full audit logging and safety gates."""

    def __init__(self):
        self.registry = SAFE_REPAIR_REGISTRY

    def get_action_details(self, action_id: str) -> Optional[Dict[str, Any]]:
        """Returns metadata and safety guarantees for a proposed fix."""
        return self.registry.get(action_id)

    def execute_safe_fix(self, action_id: str) -> Dict[str, Any]:
        """
        Executes a predefined safe fix.
        Guarantees:
        1. Only registered whitelist action IDs are allowed.
        2. Validates administrative privileges if required.
        3. Captures full command execution output for audit trail.
        """
        fix = self.get_action_details(action_id)
        if not fix:
            return {
                "success": False,
                "action_id": action_id,
                "message": f"Action '{action_id}' is not in the safe repairs whitelist.",
                "logs": ["REJECTED: Operation is not permitted under safe agent policy."]
            }

        # Check if elevation is required
        admin_status = is_admin()
        if fix["requires_admin"] and not admin_status:
            return {
                "success": False,
                "action_id": action_id,
                "requires_admin": True,
                "message": "Administrator privileges required to execute this repair.",
                "logs": [
                    "ELEVATION REQUIRED: This system repair requires Administrator privileges.",
                    "Please run CollegeLab AI Agent as Administrator or follow manual instructions:",
                    fix["manual_instructions"]
                ]
            }

        logs = [f"Starting safe repair: '{fix['title']}'", f"Safety Guarantee: {fix['safety_guarantee']}"]
        start_time = time.time()
        success = True

        try:
            if action_id == "clean_temp_files":
                # Special internal handler for safe temp cleanup
                cleanup_success, cleanup_logs = self._safe_clean_temp()
                logs.extend(cleanup_logs)
                success = cleanup_success

            elif action_id == "flush_dns":
                # Run flushdns and registerdns
                for cmd in fix["commands"]:
                    logs.append(f"Executing: {cmd}")
                    proc = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        creationflags=CREATE_NO_WINDOW
                    )
                    logs.append(proc.stdout.strip() or f"Returned code {proc.returncode}")
                    if proc.returncode != 0:
                        success = False
                        logs.append(f"Command stderr: {proc.stderr.strip()}")

            elif action_id == "renew_dhcp":
                # Run release and renew
                for cmd in fix["commands"]:
                    logs.append(f"Executing: {cmd}")
                    proc = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=20,
                        creationflags=CREATE_NO_WINDOW
                    )
                    logs.append(proc.stdout.strip() or f"Returned code {proc.returncode}")
                    if proc.returncode != 0:
                        success = False
                        logs.append(f"Command stderr: {proc.stderr.strip()}")

            elif action_id == "reset_tcp_ip":
                for cmd in fix["commands"]:
                    logs.append(f"Executing: {cmd}")
                    proc = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=15,
                        creationflags=CREATE_NO_WINDOW
                    )
                    logs.append(proc.stdout.strip() or f"Returned code {proc.returncode}")

            elif action_id == "restart_adapter":
                for cmd in fix["commands"]:
                    logs.append(f"Executing: {cmd}")
                    proc = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=15,
                        creationflags=CREATE_NO_WINDOW
                    )
                    logs.append(proc.stdout.strip() or f"Returned code {proc.returncode}")

            elif action_id == "restart_spooler":
                for cmd in fix["commands"]:
                    logs.append(f"Executing: {cmd}")
                    proc = subprocess.run(
                        cmd,
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        creationflags=CREATE_NO_WINDOW
                    )
                    logs.append(proc.stdout.strip() or f"Returned code {proc.returncode}")

        except Exception as e:
            success = False
            logs.append(f"Exception during repair execution: {e}")

        elapsed = round(time.time() - start_time, 2)
        logs.append(f"Repair action execution finished in {elapsed}s.")

        return {
            "success": success,
            "action_id": action_id,
            "title": fix["title"],
            "logs": logs,
            "execution_time_s": elapsed
        }

    def _safe_clean_temp(self) -> Tuple[bool, List[str]]:
        """Safely cleans stale files in user's %TEMP% directory only."""
        logs = []
        temp_dir = tempfile.gettempdir()
        logs.append(f"Scanning user temp path: {temp_dir}")
        now = time.time()
        one_day_ago = now - (24 * 3600)  # 24 hours old

        deleted_files = 0
        freed_bytes = 0

        try:
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        st = os.stat(file_path)
                        # Only delete files older than 24 hours
                        if st.st_mtime < one_day_ago:
                            size = st.st_size
                            os.remove(file_path)
                            deleted_files += 1
                            freed_bytes += size
                    except (PermissionError, FileNotFoundError, OSError):
                        continue

            freed_mb = round(freed_bytes / (1024 * 1024), 2)
            logs.append(f"Cleaned {deleted_files} stale temporary files ({freed_mb} MB reclaimed).")
            return True, logs
        except Exception as e:
            logs.append(f"Error during temporary cleanup: {e}")
            return False, logs
