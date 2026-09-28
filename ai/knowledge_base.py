"""
Knowledge Base for CollegeLab AI Agent.
Encapsulates domain knowledge for college computer lab environments:
- Production rules for Forward/Backward chaining
- Bayesian priors and symptom likelihood matrices
- Diagnostic categories and action mappings
"""

from typing import List, Dict, Any
from ai.models import Rule


# 1. FAULT CATEGORIES
CATEGORIES = {
    "NETWORK": "Network Fault",
    "SYSTEM": "System Resource Fault",
    "STORAGE": "Storage/Space Issue",
    "SERVICE": "Service/Application Issue",
    "DEVICE": "Device Detection Issue",
    "GENERAL": "General Diagnostics"
}


# 2. PRODUCTION RULES (Logic Engine)
# Follows the strict diagnostic hierarchy:
# Layer 1: Adapter -> Layer 2: IP -> Layer 3: Gateway -> Layer 4: DNS -> Layer 5: Internet -> Layer 6: Nominal
RULES: List[Rule] = [
    Rule(
        rule_id="RULE-NET-01",
        name="Network Adapter Disabled or Disconnected",
        antecedents=["!adapter_up"],
        consequents=["fault_adapter_down", "network_layer_broken"],
        diagnosis_name="Network Adapter Disabled or Physical Disconnect",
        category=CATEGORIES["NETWORK"],
        confidence_factor=0.98,
        recommended_action="Inspect physical Ethernet patch cable, verify lab wall jack, or re-enable network adapter in Windows Device Manager.",
        action_key="restart_adapter",
        explanation="Hierarchy Layer 1 Failure: No active network adapter reported link-up status. Upstream layers (IP, Gateway, DNS) cannot function without an operational physical/wireless link."
    ),
    Rule(
        rule_id="RULE-NET-02",
        name="IP / DHCP Configuration Problem",
        antecedents=["adapter_up", "!has_valid_ip"],
        consequents=["fault_ip_dhcp_issue", "network_layer_broken"],
        diagnosis_name="IP Configuration / DHCP Lease Failure",
        category=CATEGORIES["NETWORK"],
        confidence_factor=0.94,
        recommended_action="Release and renew DHCP lease using Windows network stack refresh.",
        action_key="renew_dhcp",
        explanation="Hierarchy Layer 2 Failure: Network adapter is connected, but has failed to obtain a valid IPv4 address from the lab DHCP server (or has fallen back to an unrouted APIPA 169.254.x.x autoconfig address)."
    ),
    Rule(
        rule_id="RULE-NET-03",
        name="Default Gateway / Local Switch Unreachable",
        antecedents=["adapter_up", "has_valid_ip", "!gateway_reachable"],
        consequents=["fault_gateway_unreachable", "network_layer_broken"],
        diagnosis_name="Default Gateway / Local Switch Unreachable",
        category=CATEGORIES["NETWORK"],
        confidence_factor=0.92,
        recommended_action="Reset local TCP/IP stack or inspect laboratory network switch port.",
        action_key="reset_tcp_ip",
        explanation="Hierarchy Layer 3 Failure: Machine has a valid IP address, but ICMP/socket probes to the default gateway fail. The computer is isolated from the local subnet or the lab router is unresponsive."
    ),
    Rule(
        rule_id="RULE-NET-04",
        name="DNS Name Resolution Problem",
        antecedents=["adapter_up", "has_valid_ip", "gateway_reachable", "!dns_resolution_ok"],
        consequents=["fault_dns_resolution_issue", "name_resolution_broken"],
        diagnosis_name="DNS Name Resolution Failure",
        category=CATEGORIES["NETWORK"],
        confidence_factor=0.95,
        recommended_action="Flush local DNS resolver cache and re-register DNS with lab servers.",
        action_key="flush_dns",
        explanation="Hierarchy Layer 4 Failure: Adapter, IP configuration, and default gateway are fully functional, but domain name lookup queries fail. The failure is isolated specifically to the DNS resolution stage."
    ),
    Rule(
        rule_id="RULE-NET-05",
        name="External WAN / Internet ISP Outage",
        antecedents=["adapter_up", "has_valid_ip", "gateway_reachable", "dns_resolution_ok", "!internet_reachable"],
        consequents=["fault_wan_isp_outage"],
        diagnosis_name="External Internet WAN / ISP Outage",
        category=CATEGORIES["NETWORK"],
        confidence_factor=0.88,
        recommended_action="Report upstream internet connection outage to college network administrator.",
        action_key=None,
        explanation="Hierarchy Layer 5 Failure: Local network, default gateway, and DNS lookups succeed, but outbound internet traffic cannot reach external endpoints. The failure is beyond the local computer, at the campus firewall or ISP uplink."
    ),
    Rule(
        rule_id="RULE-SYS-01",
        name="System Memory Saturation (High RAM)",
        antecedents=["ram_usage_high"],
        consequents=["fault_ram_exhaustion"],
        diagnosis_name="High System RAM Utilization",
        category=CATEGORIES["SYSTEM"],
        confidence_factor=0.90,
        recommended_action="Review top memory-consuming processes and close non-essential lab programs or browser tabs.",
        action_key=None,
        explanation="Physical RAM utilization exceeds the laboratory safe threshold (> 80%). Software workloads (IDEs, compilers, browser tabs) may be saturating available memory. This does not indicate physical memory failure."
    ),
    Rule(
        rule_id="RULE-SYS-02",
        name="Sustained High CPU Workload",
        antecedents=["cpu_usage_high"],
        consequents=["fault_cpu_exhaustion"],
        diagnosis_name="High CPU Utilization",
        category=CATEGORIES["SYSTEM"],
        confidence_factor=0.88,
        recommended_action="Inspect running processes for runaway threads or infinite loops from student code.",
        action_key=None,
        explanation="Overall processor usage exceeds 90%. Software diagnosis indicates heavy computational load. This does not imply physical hardware damage."
    ),
    Rule(
        rule_id="RULE-DISK-01",
        name="Storage Capacity Depletion",
        antecedents=["disk_space_critical"],
        consequents=["fault_storage_depleted"],
        diagnosis_name="Critical Storage Space Shortage",
        category=CATEGORIES["STORAGE"],
        confidence_factor=0.92,
        recommended_action="Clean safe user temporary files (%TEMP%) and cached student project artifacts.",
        action_key="clean_temp_files",
        explanation="Available disk space on the primary system volume is critically low (< 5GB free or > 85% full), which can destabilize OS operations and student workspace builds."
    ),
    Rule(
        rule_id="RULE-SVC-01",
        name="Windows Print Spooler Stalled",
        antecedents=["spooler_service_stopped"],
        consequents=["fault_print_spooler_down"],
        diagnosis_name="Print Spooler Service Stalled",
        category=CATEGORIES["SERVICE"],
        confidence_factor=0.95,
        recommended_action="Restart Windows Print Spooler service.",
        action_key="restart_spooler",
        explanation="The Windows Print Spooler service is stopped, preventing lab printing services."
    ),
    Rule(
        rule_id="RULE-NOM-01",
        name="Nominal Operational State",
        antecedents=[
            "adapter_up", "has_valid_ip", "gateway_reachable", "dns_resolution_ok", "internet_reachable",
            "!ram_usage_high", "!cpu_usage_high", "!disk_space_critical"
        ],
        consequents=["system_all_healthy"],
        diagnosis_name="All Subsystems Fully Operational",
        category=CATEGORIES["GENERAL"],
        confidence_factor=1.0,
        recommended_action="No repair action required. Computer is healthy.",
        action_key=None,
        explanation="Supported diagnostics completed successfully. All real diagnostic checks across network adapters, IP routing, DNS, gateway, internet, CPU, memory, and storage passed within safe thresholds."
    )
]


# 3. BAYESIAN DIAGNOSTIC KNOWLEDGE BASE
# Documented priors and symptom likelihood matrices calibrated for college computer labs.
# Priors represent base rate probabilities of mutually exclusive root causes.
# Likelihoods represent P(Symptom = Abnormal | Hypothesis).
# Crucially includes hyp_nominal so normal runs correctly produce >99% nominal probability.

BAYESIAN_HYPOTHESES: Dict[str, Dict[str, Any]] = {
    "hyp_nominal": {
        "name": "No Supported Fault Detected (Nominal System State)",
        "category": CATEGORIES["GENERAL"],
        "prior": 0.70,
        "recommended_action": "No repair required. All supported diagnostic checks completed successfully.",
        "action_key": None,
        "likelihoods": {
            "adapter_down": 0.01,
            "no_valid_ip": 0.01,
            "gateway_failed": 0.01,
            "dns_failed": 0.01,
            "internet_failed": 0.01,
            "ram_high": 0.02,
            "cpu_high": 0.02,
            "disk_critical": 0.01,
            "spooler_stopped": 0.01
        }
    },
    "fault_dns_problem": {
        "name": "DNS Resolution Problem",
        "category": CATEGORIES["NETWORK"],
        "prior": 0.07,
        "recommended_action": "Flush local DNS resolver cache and re-register DNS with lab servers.",
        "action_key": "flush_dns",
        "likelihoods": {
            "adapter_down": 0.01,
            "no_valid_ip": 0.02,
            "gateway_failed": 0.04,     # Gateway is working during a pure DNS issue
            "dns_failed": 0.96,         # High probability of DNS failing
            "internet_failed": 0.85,    # Outbound named requests will fail
            "ram_high": 0.04,
            "cpu_high": 0.04,
            "disk_critical": 0.02,
            "spooler_stopped": 0.01
        }
    },
    "fault_gateway_router": {
        "name": "Gateway / Local Switch Outage",
        "category": CATEGORIES["NETWORK"],
        "prior": 0.05,
        "recommended_action": "Reinitialize TCP/IP network stack and inspect lab switch port.",
        "action_key": "reset_tcp_ip",
        "likelihoods": {
            "adapter_down": 0.02,
            "no_valid_ip": 0.08,
            "gateway_failed": 0.96,     # Primary symptom: Gateway unreachable
            "dns_failed": 0.90,         # Downstream symptom: queries cannot exit subnet
            "internet_failed": 0.95,    # Downstream symptom: internet blocked
            "ram_high": 0.03,
            "cpu_high": 0.03,
            "disk_critical": 0.02,
            "spooler_stopped": 0.01
        }
    },
    "fault_ip_dhcp": {
        "name": "IP / DHCP Configuration Problem",
        "category": CATEGORIES["NETWORK"],
        "prior": 0.06,
        "recommended_action": "Release and renew DHCP lease using Windows network stack refresh.",
        "action_key": "renew_dhcp",
        "likelihoods": {
            "adapter_down": 0.02,
            "no_valid_ip": 0.96,        # Primary symptom: No valid IP or APIPA
            "gateway_failed": 0.92,     # Cannot route without IP
            "dns_failed": 0.90,
            "internet_failed": 0.95,
            "ram_high": 0.03,
            "cpu_high": 0.03,
            "disk_critical": 0.02,
            "spooler_stopped": 0.01
        }
    },
    "fault_wan_isp": {
        "name": "External Internet WAN / ISP Outage",
        "category": CATEGORIES["NETWORK"],
        "prior": 0.03,
        "recommended_action": "Report upstream internet connection outage to college network administrator.",
        "action_key": None,
        "likelihoods": {
            "adapter_down": 0.01,
            "no_valid_ip": 0.01,
            "gateway_failed": 0.02,     # Gateway is reachable
            "dns_failed": 0.15,         # Local DNS or cached DNS may still resolve
            "internet_failed": 0.95,    # Outbound WAN traffic fails
            "ram_high": 0.02,
            "cpu_high": 0.02,
            "disk_critical": 0.01,
            "spooler_stopped": 0.01
        }
    },
    "fault_adapter_driver": {
        "name": "Network Adapter / Driver / Cable Disconnect",
        "category": CATEGORIES["DEVICE"],
        "prior": 0.02,
        "recommended_action": "Re-enable adapter in Device Manager and re-plug Ethernet patch cable.",
        "action_key": "restart_adapter",
        "likelihoods": {
            "adapter_down": 0.98,       # Primary symptom: Adapter is DOWN
            "no_valid_ip": 0.95,
            "gateway_failed": 0.98,
            "dns_failed": 0.98,
            "internet_failed": 0.99,
            "ram_high": 0.02,
            "cpu_high": 0.02,
            "disk_critical": 0.01,
            "spooler_stopped": 0.01
        }
    },
    "fault_system_ram": {
        "name": "High RAM Utilization / Memory Leak",
        "category": CATEGORIES["SYSTEM"],
        "prior": 0.03,
        "recommended_action": "Terminate runaway student processes or close excess background tasks.",
        "action_key": None,
        "likelihoods": {
            "adapter_down": 0.01,
            "no_valid_ip": 0.01,
            "gateway_failed": 0.02,
            "dns_failed": 0.02,
            "internet_failed": 0.02,
            "ram_high": 0.96,           # Primary symptom: RAM usage high
            "cpu_high": 0.45,
            "disk_critical": 0.08,
            "spooler_stopped": 0.02
        }
    },
    "fault_system_cpu": {
        "name": "High CPU Utilization / Runaway Process",
        "category": CATEGORIES["SYSTEM"],
        "prior": 0.02,
        "recommended_action": "Inspect Task Manager and terminate runaway infinite loop processes.",
        "action_key": None,
        "likelihoods": {
            "adapter_down": 0.01,
            "no_valid_ip": 0.01,
            "gateway_failed": 0.02,
            "dns_failed": 0.02,
            "internet_failed": 0.02,
            "ram_high": 0.35,
            "cpu_high": 0.96,           # Primary symptom: CPU usage high
            "disk_critical": 0.04,
            "spooler_stopped": 0.01
        }
    },
    "fault_storage_full": {
        "name": "Storage Space Depletion",
        "category": CATEGORIES["STORAGE"],
        "prior": 0.015,
        "recommended_action": "Clean temporary cache (%TEMP%) and obsolete lab downloads.",
        "action_key": "clean_temp_files",
        "likelihoods": {
            "adapter_down": 0.01,
            "no_valid_ip": 0.01,
            "gateway_failed": 0.01,
            "dns_failed": 0.02,
            "internet_failed": 0.02,
            "ram_high": 0.08,
            "cpu_high": 0.06,
            "disk_critical": 0.98,      # Primary symptom: Disk full
            "spooler_stopped": 0.01
        }
    },
    "fault_print_spooler": {
        "name": "Print Spooler Service Stalled",
        "category": CATEGORIES["SERVICE"],
        "prior": 0.005,
        "recommended_action": "Restart Windows Print Spooler service.",
        "action_key": "restart_spooler",
        "likelihoods": {
            "adapter_down": 0.01,
            "no_valid_ip": 0.01,
            "gateway_failed": 0.01,
            "dns_failed": 0.01,
            "internet_failed": 0.01,
            "ram_high": 0.02,
            "cpu_high": 0.02,
            "disk_critical": 0.02,
            "spooler_stopped": 0.98     # Primary symptom: Spooler stopped
        }
    }
}
