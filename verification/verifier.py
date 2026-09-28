"""
Verification Engine for CollegeLab AI Agent.
Enforces the mandatory post-repair verification protocol:
1. Snapshots pre-repair diagnostic indicators.
2. Re-runs targeted real diagnostic sensors post-repair.
3. Performs side-by-side BEFORE vs AFTER diff.
4. Concludes whether the fault is definitively Resolved or Requires Technician Attention.
"""

from typing import Dict, List, Any, Optional


class VerificationEngine:
    """Performs real empirical verification of repair outcomes."""

    @staticmethod
    def extract_key_metrics(raw_diag: Dict[str, Any]) -> Dict[str, Any]:
        """Flattens core diagnostic indicators into a comparable dictionary."""
        metrics = {}
        # Network metrics
        net = raw_diag.get("network", {})
        if net:
            metrics["Adapter Status"] = "PASS" if any(a.get("is_up") for a in net.get("adapters", [])) else "FAIL"
            metrics["IP Configuration"] = "PASS" if (net.get("ip_configuration", {}).get("primary_ip") and not net.get("ip_configuration", {}).get("is_apipa")) else "FAIL"
            metrics["Gateway Reachable"] = "PASS" if net.get("gateway_reachable") else "FAIL"
            metrics["DNS Resolution"] = "PASS" if net.get("dns_resolution_ok") else "FAIL"
            metrics["Internet Access"] = "PASS" if net.get("internet_reachable") else "FAIL"

        # System metrics
        sys_data = raw_diag.get("system", {})
        if sys_data:
            metrics["CPU Health"] = "PASS" if sys_data.get("cpu_status") == "Healthy" else f"WARN ({sys_data.get('cpu', {}).get('percent')}%)"
            metrics["RAM Health"] = "PASS" if sys_data.get("ram_status") == "Healthy" else f"HIGH ({sys_data.get('ram', {}).get('percent')}%)"
            metrics["Storage Health"] = "PASS" if sys_data.get("disk_status") == "Healthy" else "CRITICAL"

        return metrics

    def compare_and_verify(
        self,
        before_diag: Dict[str, Any],
        after_diag: Dict[str, Any],
        action_title: str
    ) -> Dict[str, Any]:
        """
        Compares before and after diagnostic snapshots.
        Determines empirical resolution status.
        """
        before_metrics = self.extract_key_metrics(before_diag)
        after_metrics = self.extract_key_metrics(after_diag)

        all_keys = list(dict.fromkeys(list(before_metrics.keys()) + list(after_metrics.keys())))
        comparison_rows = []

        had_failures_before = False
        failures_resolved = 0
        remaining_failures = 0

        for key in all_keys:
            val_before = before_metrics.get(key, "N/A")
            val_after = after_metrics.get(key, "N/A")

            # Determine outcome
            is_before_fail = val_before != "PASS" and "Healthy" not in val_before
            is_after_fail = val_after != "PASS" and "Healthy" not in val_after

            if is_before_fail:
                had_failures_before = True

            if is_before_fail and not is_after_fail:
                outcome = "FIXED (Resolved)"
                failures_resolved += 1
            elif is_before_fail and is_after_fail:
                outcome = "UNRESOLVED (Still Failing)"
                remaining_failures += 1
            elif not is_before_fail and not is_after_fail:
                outcome = "NOMINAL (Maintained)"
            else:
                outcome = "REGRESSED"
                remaining_failures += 1

            comparison_rows.append({
                "test_name": key,
                "before": val_before,
                "after": val_after,
                "outcome": outcome
            })

        # Overall verdict
        if had_failures_before and remaining_failures == 0:
            is_resolved = True
            verdict = "Problem Resolved"
            summary_message = "All identified diagnostic faults were successfully resolved by the safe repair action."
            badge = "🟢"
        elif had_failures_before and failures_resolved > 0 and remaining_failures > 0:
            is_resolved = False
            verdict = "Partially Resolved – Technician Attention Required"
            summary_message = f"{failures_resolved} fault(s) resolved, but {remaining_failures} fault(s) persist. Physical or lab-network technician intervention needed."
            badge = "🟡"
        elif had_failures_before and remaining_failures > 0:
            is_resolved = False
            verdict = "Problem Not Resolved – Technician Attention Required"
            summary_message = "Post-repair diagnostic checks indicate the issue persists. Hardware, physical cabling, or upstream network technician attention required."
            badge = "🔴"
        else:
            # System was already healthy
            is_resolved = True
            verdict = "System Operational (Verified)"
            summary_message = "System state verified nominal across all diagnostic tests."
            badge = "🟢"

        return {
            "is_resolved": is_resolved,
            "verdict": verdict,
            "summary_message": summary_message,
            "badge": badge,
            "action_executed": action_title,
            "comparison": comparison_rows,
            "failures_resolved_count": failures_resolved,
            "remaining_failures_count": remaining_failures
        }
