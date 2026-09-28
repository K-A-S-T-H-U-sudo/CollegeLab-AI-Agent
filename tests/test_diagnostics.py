"""
Tests for Real Diagnostic Modules (Network, System, Device).
"""

import pytest
from diagnostics.network import NetworkDiagnostic
from diagnostics.system import SystemHealthDiagnostic
from diagnostics.device import DeviceDiagnostic


def test_network_diagnostic():
    diag = NetworkDiagnostic()
    res = diag.run_full_diagnosis()

    assert "adapters" in res
    assert "ip_configuration" in res
    assert "stages" in res
    assert isinstance(res["adapters"], list)
    assert res["summary_status"] in ("Healthy", "Warning", "Critical")
    # Multi-stage check
    stages = res["stages"]
    for s in ["Adapter", "IP Configuration", "Default Gateway", "DNS Resolution", "Internet Access"]:
        assert s in stages
        assert stages[s] in ("PASS", "FAIL")


def test_system_health_diagnostic():
    diag = SystemHealthDiagnostic()
    res = diag.run_full_diagnosis()

    assert "cpu" in res
    assert "ram" in res
    assert "disk" in res
    assert "uptime" in res
    assert res["cpu"]["percent"] >= 0.0
    assert res["ram"]["total_gb"] > 0
    assert res["disk"]["aggregate_total_gb"] > 0
    assert res["overall_status"] in ("Healthy", "Warning", "Critical")
    # Verify disclaimer presence
    assert "hardware" in res["disclaimer"].lower()


def test_device_diagnostic():
    diag = DeviceDiagnostic()
    res = diag.run_full_diagnosis()

    assert "cpu" in res
    assert "disclaimer" in res
    assert DeviceDiagnostic.DISCLAIMER in res["disclaimer"]
    assert "summary_status" in res
