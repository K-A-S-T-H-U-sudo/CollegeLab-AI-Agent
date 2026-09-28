"""
Intelligent College Lab Fault Diagnosis and Resolution Agent.
Implements the Autonomous Agent Cognitive Cycle:
PERCEIVE -> REASON -> DECIDE -> ACT -> VERIFY
"""

import time
import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from config import lab_config
from diagnostics.network import NetworkDiagnostic
from diagnostics.system import SystemHealthDiagnostic
from diagnostics.device import DeviceDiagnostic
from ai.models import Symptom, DiagnosisReport
from ai.knowledge_base import CATEGORIES
from ai.rule_engine import RuleEngine
from ai.bayesian_engine import BayesianEngine
from resolution.safe_fixes import SafeResolutionEngine
from verification.verifier import VerificationEngine
from database.history import history_db


class CollegeLabAgent:
    """
    Intelligent Agent for College Computer Laboratories.
    Inspects observable system state, reasons through Logic and Bayesian models,
    executes safe software/network repairs, and empirically verifies outcomes.
    """

    def __init__(self):
        self.config = lab_config
        self.network_sensor = NetworkDiagnostic()
        self.system_sensor = SystemHealthDiagnostic()
        self.device_sensor = DeviceDiagnostic()

        self.rule_engine = RuleEngine()
        self.bayesian_engine = BayesianEngine()
        self.resolution_engine = SafeResolutionEngine()
        self.verification_engine = VerificationEngine()
        self.history = history_db

        # Agent state
        self.current_raw_diagnostics: Dict[str, Any] = {}
        self.current_symptoms: List[Symptom] = []
        self.last_report: Optional[DiagnosisReport] = None
        self.last_verification: Optional[Dict[str, Any]] = None

    # ==========================================
    # 1. PERCEIVE: Real System Sensor Ingestion
    # ==========================================
    def perceive(self, scan_mode: str = "full", progress_callback: Optional[Callable[[str, int], None]] = None) -> Dict[str, Any]:
        """
        Sensors Layer: Performs real queries on current computer.
        scan_mode options: 'quick', 'full', 'network', 'system', 'device'
        """
        raw: Dict[str, Any] = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scan_mode": scan_mode,
            "computer_id": self.config.computer_id,
            "lab_name": self.config.lab_name,
            "room": self.config.room
        }

        if progress_callback:
            progress_callback("Inspecting network adapters and routes...", 15)

        if scan_mode in ("quick", "full", "network"):
            raw["network"] = self.network_sensor.run_full_diagnosis()

        if progress_callback:
            progress_callback("Measuring CPU, RAM, and Disk utilization...", 45)

        if scan_mode in ("quick", "full", "system"):
            raw["system"] = self.system_sensor.run_full_diagnosis()

        if progress_callback:
            progress_callback("Querying device hardware and peripherals...", 75)

        if scan_mode in ("full", "device"):
            raw["device"] = self.device_sensor.run_full_diagnosis()

        if progress_callback:
            progress_callback("Perception complete. Synthesizing symptoms...", 100)

        self.current_raw_diagnostics = raw
        self.current_symptoms = self._extract_symptoms(raw)
        return raw

    def _extract_symptoms(self, raw: Dict[str, Any]) -> List[Symptom]:
        """Converts raw sensor measurements into symbolic symptom propositions."""
        symptoms: List[Symptom] = []

        # --- Network Symptoms ---
        net = raw.get("network", {})
        if net:
            adapters = net.get("adapters", [])
            has_adapter = len(adapters) > 0
            is_up = any(a.get("is_up") and not a.get("is_loopback") for a in adapters)
            ip_info = net.get("ip_configuration", {})
            primary_ip = ip_info.get("primary_ip")
            is_apipa = ip_info.get("is_apipa", False)
            has_valid_ip = bool(primary_ip and not is_apipa and primary_ip != "127.0.0.1")

            gateway_ok = net.get("gateway_reachable", False)
            dns_ok = net.get("dns_resolution_ok", False)
            internet_ok = net.get("internet_reachable", False)

            symptoms.append(Symptom("adapter_available", "Network Adapter Present", has_adapter, not has_adapter, "Network"))
            symptoms.append(Symptom("adapter_up", "Network Adapter Link Up", is_up, not is_up, "Network"))
            symptoms.append(Symptom("has_valid_ip", f"Assigned IPv4: {primary_ip or 'None'}", has_valid_ip, not has_valid_ip, "Network"))
            symptoms.append(Symptom("is_apipa", "APIPA (169.254.x.x) Autoconfig IP", is_apipa, is_apipa, "Network"))
            symptoms.append(Symptom("gateway_reachable", f"Gateway Reachable: {ip_info.get('gateway') or 'None'}", gateway_ok, not gateway_ok, "Network"))
            symptoms.append(Symptom("gateway_failed", "Default Gateway Unreachable", not gateway_ok, not gateway_ok, "Network"))
            symptoms.append(Symptom("dns_resolution_ok", "DNS Resolution Success", dns_ok, not dns_ok, "Network"))
            symptoms.append(Symptom("dns_failed", "DNS Resolution Failure", not dns_ok, not dns_ok, "Network"))
            symptoms.append(Symptom("internet_reachable", "External Internet Reachable", internet_ok, not internet_ok, "Network"))
            symptoms.append(Symptom("internet_failed", "External Internet Unreachable", not internet_ok, not internet_ok, "Network"))

        # --- System Symptoms ---
        sys_data = raw.get("system", {})
        if sys_data:
            cpu_status = sys_data.get("cpu_status", "Healthy")
            ram_status = sys_data.get("ram_status", "Healthy")
            disk_status = sys_data.get("disk_status", "Healthy")

            is_cpu_high = cpu_status == "High"
            is_ram_high = ram_status == "High"
            is_disk_crit = disk_status in ("Warning", "Critical")

            symptoms.append(Symptom("cpu_usage_high", f"CPU Utilization ({sys_data.get('cpu', {}).get('percent')}%)", is_cpu_high, is_cpu_high, "System"))
            symptoms.append(Symptom("ram_usage_high", f"RAM Utilization ({sys_data.get('ram', {}).get('percent')}%)", is_ram_high, is_ram_high, "System"))
            symptoms.append(Symptom("disk_space_critical", f"Storage Partitions Status ({disk_status})", is_disk_crit, is_disk_crit, "Storage"))

            # Check Spooler service
            spooler = sys_data.get("services", {}).get("Spooler", {})
            if spooler and spooler.get("status") in ("stopped", "unavailable"):
                symptoms.append(Symptom("spooler_service_stopped", "Windows Print Spooler Stalled", True, True, "Service"))

        return symptoms

    # ==========================================
    # 2. REASON: Logic Inference & Bayesian Probabilities
    # ==========================================
    def reason(self) -> Tuple[List[Dict[str, Any]], List[Any]]:
        """
        Executes Forward Chaining Rules and Bayesian Inference.
        Returns: (deduced_rules, bayesian_hypotheses)
        """
        self.rule_engine.load_symptoms(self.current_symptoms)
        deduced_rules = self.rule_engine.run_forward_chaining()
        bayesian_hypotheses = self.bayesian_engine.compute_posteriors(self.current_symptoms)
        return deduced_rules, bayesian_hypotheses

    # ==========================================
    # ==========================================
    # 3. DECIDE: Synthesize & Select Recommended Action
    # ==========================================
    def decide(self) -> DiagnosisReport:
        """
        Combines rule-based deduction and Bayesian ranking to produce the final diagnosis report.
        Enforces the 6-layer diagnostic hierarchy and generates full Explainable AI reasoning:
        - WHAT WAS OBSERVED
        - WHAT IT MEANS
        - WHY THIS FAULT WAS CONSIDERED
        - WHY OTHER FAULTS WERE LESS LIKELY
        - WHAT ACTION IS RECOMMENDED
        """
        deduced_rules, bayesian_hypotheses = self.reason()

        # Backward chaining verification for key goals
        backward_goals = []
        if any(s.is_abnormal for s in self.current_symptoms if s.category == "Network"):
            bg = self.rule_engine.run_backward_chaining("network_layer_broken")
            backward_goals.append(bg)

        # Separate abnormal symptoms
        abnormal_symptoms = [s for s in self.current_symptoms if s.is_abnormal]

        evidence_items = []
        for s in self.current_symptoms:
            evidence_items.append({
                "key": s.key,
                "description": s.description,
                "passed": not s.is_abnormal,
                "category": s.category,
                "status_str": "PASS [OK]" if not s.is_abnormal else "FAIL [X]"
            })

        net_diag = self.current_raw_diagnostics.get("network", {})
        ip_info = net_diag.get("ip_configuration", {}) if net_diag else {}
        primary_ip = ip_info.get("primary_ip")
        gateway_ip = ip_info.get("gateway")
        stages = net_diag.get("stages", {}) if net_diag else {}

        # -------------------------------------------------------------
        # Case A: All Implemented Tests Passed (Nominal State)
        # -------------------------------------------------------------
        if not abnormal_symptoms:
            overall_status = "Healthy"
            primary_fault = "All Subsystems Nominal (No Supported Fault Detected)"
            category = "General Diagnostics"
            test_result_summary = "Supported diagnostics completed successfully."
            confidence = "Not Applicable (No Active Fault)"
            confidence_score = 1.0
            confidence_reason = (
                "Diagnostic confidence applies to specific fault hypotheses. "
                "Because all implemented tests passed within safe parameters, no fault is asserted."
            )
            what_was_observed = (
                "All real diagnostic sensors (Network Adapter link, IPv4 lease, Default Gateway ping, "
                "DNS resolution, Internet connectivity, CPU load, RAM utilization, and Storage capacity) "
                "passed within normal operating thresholds."
            )
            what_it_means = "The computer is operating normally within the scope of supported software diagnostics."
            why_considered = "Evaluated the baseline nominal hypothesis against all real sensor observations."
            why_others_less_likely = "No threshold breaches or failure signatures were observed on any monitored subsystem."
            rec_action = "No repair required. System is running within normal laboratory parameters."
            action_key = None

        # -------------------------------------------------------------
        # Case B: Network Diagnostic Hierarchy Breakdown
        # -------------------------------------------------------------
        elif stages.get("Adapter") == "FAIL":
            overall_status = "Critical"
            primary_fault = "Network Adapter Disabled or Disconnected"
            category = "Device / Network"
            test_result_summary = "Network failure detected at Layer 1 (Adapter Link)."
            confidence = "High"
            confidence_score = 0.98
            confidence_reason = "Adapter link failure is the foundational physical/data-link layer. Upstream layers cannot function without it."
            what_was_observed = "No network adapter reported link-up status or enabled state."
            what_it_means = "The computer has no active physical Ethernet connection or Wi-Fi link."
            why_considered = "Real adapter query confirmed link is down or adapter is disabled."
            why_others_less_likely = "IP, Gateway, and DNS failures are secondary symptoms of having no link, not separate software faults."
            rec_action = "Check Ethernet cable connection, verify lab wall port, or re-enable network adapter."
            action_key = "restart_adapter"

        elif stages.get("IP Configuration") == "FAIL":
            overall_status = "Critical"
            primary_fault = "IP Configuration / DHCP Lease Failure"
            category = "Network Fault"
            test_result_summary = "Network failure detected at Layer 2 (IP Configuration)."
            confidence = "High"
            confidence_score = 0.94
            confidence_reason = "Network adapter is connected (Layer 1 passed), but IPv4 address assignment failed (Layer 2 failed)."
            what_was_observed = f"Adapter is connected, but IPv4 is '{primary_ip or 'None'}' (APIPA Autoconfig: {ip_info.get('is_apipa', False)})."
            what_it_means = "The computer cannot communicate on the local network because it lacks a valid IP configuration from DHCP."
            why_considered = "Adapter is functional, isolating the failure to IP lease assignment."
            why_others_less_likely = "Physical link is working. Gateway and DNS failures are downstream effects of having no valid IP."
            rec_action = "Release and renew DHCP lease using Windows network stack refresh."
            action_key = "renew_dhcp"

        elif stages.get("Default Gateway") == "FAIL":
            overall_status = "Critical"
            primary_fault = "Default Gateway / Local Switch Unreachable"
            category = "Network Fault"
            test_result_summary = "Network failure detected at Layer 3 (Default Gateway)."
            confidence = "High"
            confidence_score = 0.92
            confidence_reason = "Adapter and IP layers passed (Layers 1-2), but local gateway probe failed (Layer 3 failed)."
            what_was_observed = f"Valid IP '{primary_ip}' assigned, but ping probes to default gateway '{gateway_ip}' failed."
            what_it_means = "The computer cannot communicate beyond its local subnet or the lab router is unresponsive."
            why_considered = "First failed layer in the hierarchy after successful IP configuration."
            why_others_less_likely = "Adapter and IP configuration succeeded. DNS and Internet failures are downstream results of gateway inaccessibility."
            rec_action = "Reset TCP/IP network stack and inspect lab switch port."
            action_key = "reset_tcp_ip"

        elif stages.get("DNS Resolution") == "FAIL":
            overall_status = "Warning"
            primary_fault = "DNS Name Resolution Failure"
            category = "Network Fault"
            test_result_summary = "Network failure detected at Layer 4 (DNS Resolution)."
            confidence = "High"
            confidence_score = 0.95
            confidence_reason = "DNS resolution is the first failed layer after successful gateway connectivity."
            what_was_observed = f"Adapter link active, IP assigned ({primary_ip}), gateway reachable ({gateway_ip}), but domain name lookup failed."
            what_it_means = "Because the computer can reach the gateway but cannot resolve domain names, the failure is isolated to the DNS resolution stage."
            why_considered = "Local network routing is fully functional, isolating the problem to the DNS resolver cache or server."
            why_others_less_likely = "Adapter, IP, and Gateway checks all passed, ruling out physical disconnection, DHCP failure, and local router outages."
            rec_action = "Flush local DNS resolver cache and re-register DNS with lab servers."
            action_key = "flush_dns"

        elif stages.get("Internet Access") == "FAIL":
            overall_status = "Warning"
            primary_fault = "External Internet WAN / ISP Outage"
            category = "Network Fault"
            test_result_summary = "Network failure detected at Layer 5 (External Internet WAN)."
            confidence = "High"
            confidence_score = 0.88
            confidence_reason = "All local layers (Adapter, IP, Gateway, DNS) succeeded, but external outbound WAN traffic timed out."
            what_was_observed = "Local network, gateway, and DNS lookups succeeded, but outbound packets to external internet endpoints timed out."
            what_it_means = "The local lab machine is healthy; the outage is upstream at the college firewall, proxy, or ISP link."
            why_considered = "First failed layer is external WAN connectivity."
            why_others_less_likely = "All local networking checks passed, ruling out computer-level network adapter, DHCP, and gateway issues."
            rec_action = "Report upstream internet connection outage to college network administrator."
            action_key = None

        # -------------------------------------------------------------
        # Case C: System Resource or Service Issues
        # -------------------------------------------------------------
        elif any(s.key == "ram_usage_high" for s in abnormal_symptoms):
            overall_status = "Warning"
            primary_fault = "High System RAM Utilization"
            category = "System Resource Fault"
            test_result_summary = "System resource threshold exceeded (RAM)."
            confidence = "High"
            confidence_score = 0.90
            confidence_reason = "Physical memory utilization exceeds the laboratory threshold (> 80%)."
            what_was_observed = f"Real-time RAM usage is {self.current_raw_diagnostics.get('system', {}).get('ram', {}).get('percent')}%."
            what_it_means = "High memory usage is causing system sluggishness. This reflects workload, not physical hardware damage."
            why_considered = "Real memory measurement exceeded safe threshold."
            why_others_less_likely = "Network and storage subsystems operating within normal parameters."
            rec_action = "Review running processes and close non-essential lab software or browser tabs."
            action_key = None

        elif any(s.key == "cpu_usage_high" for s in abnormal_symptoms):
            overall_status = "Warning"
            primary_fault = "High CPU Utilization"
            category = "System Resource Fault"
            test_result_summary = "System resource threshold exceeded (CPU)."
            confidence = "High"
            confidence_score = 0.88
            confidence_reason = "Processor usage exceeds the laboratory threshold (> 90%)."
            what_was_observed = f"Real-time CPU utilization is {self.current_raw_diagnostics.get('system', {}).get('cpu', {}).get('percent')}%."
            what_it_means = "Heavy computational load or runaway thread detected. Does not imply physical hardware failure."
            why_considered = "CPU usage is consistently above 90%."
            why_others_less_likely = "Memory and network tests passed within normal bounds."
            rec_action = "Inspect running processes for runaway student loops or background tasks."
            action_key = None

        elif any(s.key == "disk_space_critical" for s in abnormal_symptoms):
            overall_status = "Critical"
            primary_fault = "Critical Storage Space Shortage"
            category = "Storage/Space Issue"
            test_result_summary = "Primary storage partition capacity depleted."
            confidence = "High"
            confidence_score = 0.92
            confidence_reason = "Free storage space is critically low (< 5GB free or > 85% full)."
            what_was_observed = "System storage volume is near full capacity."
            what_it_means = "Low disk space can prevent file writes, workspace builds, and OS updates."
            why_considered = "Disk partition sensor reported usage beyond safe limits."
            why_others_less_likely = "Other hardware components report nominal metrics."
            rec_action = "Clean safe user temporary files (%TEMP%) and obsolete lab project caches."
            action_key = "clean_temp_files"

        elif any(s.key == "spooler_service_stopped" for s in abnormal_symptoms):
            overall_status = "Warning"
            primary_fault = "Print Spooler Service Stalled"
            category = "Service/Application Issue"
            test_result_summary = "Windows Print Spooler service is stopped."
            confidence = "High"
            confidence_score = 0.95
            confidence_reason = "Service state reported as stopped in Windows Service Controller."
            what_was_observed = "Spooler service is stopped."
            what_it_means = "Students cannot print lab reports or assignments."
            why_considered = "Direct service state inspection."
            why_others_less_likely = "System and network are operational."
            rec_action = "Restart Windows Print Spooler service."
            action_key = "restart_spooler"

        else:
            # Fallback to top Bayesian candidate
            top_bayes = bayesian_hypotheses[0]
            overall_status = "Warning"
            primary_fault = top_bayes.name
            category = top_bayes.category
            test_result_summary = "Anomalies detected by diagnostic sensors."
            confidence = "Medium" if top_bayes.posterior >= 0.50 else "Low"
            confidence_score = top_bayes.posterior
            confidence_reason = f"Bayesian posterior probability of {top_bayes.posterior * 100:.1f}% based on observed symptom vector."
            what_was_observed = ", ".join([s.description for s in abnormal_symptoms])
            what_it_means = "Diagnostic sensors detected abnormal states matching candidate fault signatures."
            why_considered = f"Top probabilistic candidate according to Bayes' rule ({top_bayes.posterior * 100:.1f}%)."
            why_others_less_likely = "Other candidate hypotheses showed lower alignment with the observed evidence."
            rec_action = top_bayes.recommended_action or "Review diagnostic details and consult technician."
            action_key = top_bayes.action_key

        report = DiagnosisReport(
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            computer_id=self.config.computer_id,
            lab_name=self.config.lab_name,
            overall_status=overall_status,
            primary_fault=primary_fault,
            category=category,
            confidence=confidence,
            confidence_score=round(confidence_score, 3),
            confidence_reason=confidence_reason,
            test_result_summary=test_result_summary,
            what_was_observed=what_was_observed,
            what_it_means=what_it_means,
            why_considered=why_considered,
            why_others_less_likely=why_others_less_likely,
            evidence=evidence_items,
            reasoning_trace=self.rule_engine.reasoning_trace,
            backward_chaining_goals=backward_goals,
            bayesian_rankings=[{
                "fault_id": h.fault_id,
                "name": h.name,
                "category": h.category,
                "prior": h.prior,
                "posterior": h.posterior,
                "math_breakdown": h.math_breakdown,
                "recommended_action": h.recommended_action
            } for h in bayesian_hypotheses],
            recommended_action=rec_action,
            action_key=action_key,
            raw_diagnostics=self.current_raw_diagnostics
        )

        self.last_report = report

        # Automatically log diagnosis to history database
        symptoms_str = ", ".join([s.description for s in abnormal_symptoms]) if abnormal_symptoms else "All nominal"
        self.history.log_event(
            computer_id=self.config.computer_id,
            lab_name=self.config.lab_name,
            category=category,
            symptoms_summary=symptoms_str,
            diagnosis=primary_fault,
            confidence=confidence,
            confidence_score=round(confidence_score, 3),
            action_performed="Diagnostic Scan",
            verification_result="Pending Repair" if abnormal_symptoms else "Verified Nominal",
            full_report=self.current_raw_diagnostics
        )

        return report

    # ==========================================
    # 4. ACT: Execute Safe Whitelisted Repair
    # ==========================================
    def act(self, action_key: str) -> Dict[str, Any]:
        """
        Executes a safe, reversible repair action with full logging.
        Guarantees that only predefined actions in the whitelist are executed.
        """
        return self.resolution_engine.execute_safe_fix(action_key)

    # ==========================================
    # 5. VERIFY: Post-Repair Empirical Validation
    # ==========================================
    def verify(self, action_key: str, action_title: str) -> Dict[str, Any]:
        """
        Core Verification Workflow:
        1. Uses before_snapshot from self.current_raw_diagnostics.
        2. Re-runs targeted real diagnostic sensors.
        3. Compares BEFORE vs AFTER metrics.
        4. Logs resolution outcome to database.
        """
        before_snapshot = self.current_raw_diagnostics.copy()

        # Re-perceive current computer state
        after_snapshot = self.perceive(scan_mode="quick")
        self.decide()

        # Verification comparison
        verification_result = self.verification_engine.compare_and_verify(
            before_diag=before_snapshot,
            after_diag=after_snapshot,
            action_title=action_title
        )

        self.last_verification = verification_result

        # Update database with verification record
        self.history.log_event(
            computer_id=self.config.computer_id,
            lab_name=self.config.lab_name,
            category="Verification",
            symptoms_summary=f"Post-repair for '{action_title}'",
            diagnosis=verification_result["verdict"],
            confidence="High",
            confidence_score=1.0 if verification_result["is_resolved"] else 0.5,
            action_performed=action_title,
            verification_result=verification_result["verdict"],
            full_report={"before": before_snapshot, "after": after_snapshot, "diff": verification_result}
        )

        return verification_result
