"""
Configuration module for CollegeLab AI Agent.
Manages persistent laboratory configuration and diagnostic thresholds.
"""

import json
import os
import socket
import platform
from pathlib import Path

APP_TITLE = "AI-Based Intelligent College Lab Fault Diagnosis and Resolution Agent"
APP_SHORT_NAME = "CollegeLab AI Agent"
APP_SUBTITLE = "Intelligent Computer Fault Diagnosis & Resolution"
APP_VERSION = "1.0.0"

# Configuration file location
CONFIG_FILE_NAME = "lab_config.json"

DEFAULT_THRESHOLDS = {
    "cpu_moderate": 70.0,      # > 70% is Moderate load
    "cpu_high": 90.0,          # > 90% is High load
    "ram_moderate": 60.0,      # 60-80% is Moderate
    "ram_high": 80.0,          # > 80% is High
    "disk_warning_pct": 85.0,  # > 85% used is Warning
    "disk_critical_pct": 95.0, # > 95% used is Critical
    "disk_min_free_gb": 5.0,   # Less than 5 GB free is Warning
    "ping_high_latency_ms": 150.0,
    "ping_timeout_s": 2.0,
}

import sys
import tempfile


def get_default_config_dir() -> str:
    """Finds a reliable writable directory for persistent configuration."""
    candidates = []
    if getattr(sys, "frozen", False):
        candidates.append(os.path.dirname(sys.executable))
    else:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))

    local_appdata = os.environ.get("LOCALAPPDATA")
    if local_appdata:
        candidates.append(os.path.join(local_appdata, "CollegeLabAI"))
    candidates.append(os.path.join(os.path.expanduser("~"), ".collegelab_ai"))
    candidates.append(tempfile.gettempdir())

    for p in candidates:
        try:
            os.makedirs(p, exist_ok=True)
            t = os.path.join(p, ".cfg_test")
            with open(t, "w") as f:
                f.write("1")
            os.remove(t)
            return p
        except Exception:
            continue
    return tempfile.gettempdir()


class LabConfig:
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = get_default_config_dir()
        self.config_dir = config_dir
        self.config_path = os.path.join(config_dir, CONFIG_FILE_NAME)
        
        # Default Lab identity - real hostname for Computer ID
        hostname = socket.gethostname() or "LAB-PC"
        self.data = {
            "college_name": "Not configured",
            "lab_name": "Not configured",
            "computer_id": hostname,
            "room": "Not configured",
            "department": "Not configured",
            "technician_contact": "Not configured",
            "thresholds": DEFAULT_THRESHOLDS.copy(),
            "auto_verify_after_fix": True,
            "theme": "dark"
        }
        self.load()

    def load(self):
        """Loads configuration from JSON file if available."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                print(f"[Warning] Failed to load config from {self.config_path}: {e}")

    def save(self):
        """Persists current configuration to JSON file."""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4)
            return True
        except Exception as e:
            print(f"[Error] Failed to save config to {self.config_path}: {e}")
            return False

    @property
    def college_name(self) -> str:
        return self.data.get("college_name") or "Not configured"

    @college_name.setter
    def college_name(self, val: str):
        val_str = str(val).strip()
        self.data["college_name"] = val_str if val_str else "Not configured"

    @property
    def lab_name(self) -> str:
        return self.data.get("lab_name") or "Not configured"

    @lab_name.setter
    def lab_name(self, val: str):
        val_str = str(val).strip()
        self.data["lab_name"] = val_str if val_str else "Not configured"

    @property
    def computer_id(self) -> str:
        return self.data.get("computer_id") or socket.gethostname() or "LAB-PC"

    @computer_id.setter
    def computer_id(self, val: str):
        val_str = str(val).strip()
        self.data["computer_id"] = val_str if val_str else socket.gethostname()

    @property
    def room(self) -> str:
        return self.data.get("room") or "Not configured"

    @room.setter
    def room(self, val: str):
        val_str = str(val).strip()
        self.data["room"] = val_str if val_str else "Not configured"

    @property
    def department(self) -> str:
        return self.data.get("department") or "Not configured"

    @department.setter
    def department(self, val: str):
        val_str = str(val).strip()
        self.data["department"] = val_str if val_str else "Not configured"

    @property
    def technician_contact(self) -> str:
        return self.data.get("technician_contact") or "Not configured"

    @technician_contact.setter
    def technician_contact(self, val: str):
        val_str = str(val).strip()
        self.data["technician_contact"] = val_str if val_str else "Not configured"

    @property
    def thresholds(self) -> dict:
        return self.data.get("thresholds", DEFAULT_THRESHOLDS)


# Global instance
lab_config = LabConfig()

