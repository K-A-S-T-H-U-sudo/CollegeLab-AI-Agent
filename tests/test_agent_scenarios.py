"""
Section 17 Test Suite: Comprehensive Diagnostic Scenarios
Tests the structured diagnostic hierarchy and evidence-based reasoning:
- TEST 1: Healthy network -> All supported network checks pass. No fault reported.
- TEST 2: DNS failure -> DNS stage fails. DNS-related diagnosis becomes most likely.
- TEST 3: No valid IP -> IP configuration / DHCP-related diagnosis.
- TEST 4: Adapter unavailable -> Adapter/device-level issue. Never claim DNS/internet repair solved it.
- TEST 5: High RAM usage -> System health warning based on RAM usage.
"""

import pytest
from ai.models import Symptom
from ai.rule_engine import RuleEngine
from ai.bayesian_engine import BayesianEngine
from agent import CollegeLabAgent


def test_scenario_1_healthy_network():
    """TEST 1: Healthy network -> All checks pass -> No fault reported, nominal dominates."""
    symptoms = [
        Symptom("adapter_available", "Network adapter detected", True, False, "Network"),
        Symptom("adapter_up", "Network adapter is enabled and connected", True, False, "Network"),
        Symptom("has_valid_ip", "Valid IPv4 address obtained", True, False, "Network"),
        Symptom("gateway_reachable", "Default gateway reachable", True, False, "Network"),
        Symptom("dns_resolution_ok", "DNS resolution successful", True, False, "Network"),
        Symptom("internet_reachable", "External internet reachable", True, False, "Network"),
    ]

    # Rule Engine Check
    rule_engine = RuleEngine()
    rule_engine.load_symptoms(symptoms)
    deduced = rule_engine.run_forward_chaining()
    # No network fault rules should fire
    network_faults = [d for d in deduced if "Network" in d.get("category", "")]
    assert len(network_faults) == 0

    # Bayesian Check
    bayes = BayesianEngine()
    posteriors = bayes.compute_posteriors(symptoms)
    top_hyp = posteriors[0]
    assert top_hyp.fault_id == "hyp_nominal"
    assert top_hyp.posterior > 0.90  # Nominal dominates > 90%

    # Bug check: DNS fault probability must be near zero
    dns_hyp = next((h for h in posteriors if h.fault_id == "fault_dns_problem"), None)
    assert dns_hyp is not None
    assert dns_hyp.posterior < 0.05  # Was 49.9% in buggy prototype!


def test_scenario_2_dns_failure():
    """TEST 2: DNS failure -> DNS fails -> DNS-related diagnosis is top fault, recommends flush_dns."""
    symptoms = [
        Symptom("adapter_available", "Network adapter detected", True, False, "Network"),
        Symptom("adapter_up", "Network adapter is enabled and connected", True, False, "Network"),
        Symptom("has_valid_ip", "Valid IPv4 address obtained", True, False, "Network"),
        Symptom("gateway_reachable", "Default gateway reachable", True, False, "Network"),
        Symptom("dns_resolution_ok", "DNS resolution failed", False, True, "Network"),
        Symptom("dns_failed", "DNS lookup failure observed", True, True, "Network"),
        Symptom("internet_reachable", "External internet unreachable", False, True, "Network"),
    ]

    # Rule Engine Check
    rule_engine = RuleEngine()
    rule_engine.load_symptoms(symptoms)
    deduced = rule_engine.run_forward_chaining()
    fault_names = [d["name"] for d in deduced]
    assert "DNS Name Resolution Failure" in fault_names

    # Bayesian Check
    bayes = BayesianEngine()
    posteriors = bayes.compute_posteriors(symptoms)
    top_hyp = posteriors[0]
    assert top_hyp.fault_id == "fault_dns_problem"
    assert top_hyp.posterior > 0.70  # High confidence DNS fault


def test_scenario_3_no_valid_ip():
    """TEST 3: No valid IP -> IP configuration / DHCP-related diagnosis."""
    symptoms = [
        Symptom("adapter_available", "Network adapter detected", True, False, "Network"),
        Symptom("adapter_up", "Network adapter is enabled and connected", True, False, "Network"),
        Symptom("has_valid_ip", "No valid IPv4 address assigned", False, True, "Network"),
        Symptom("ip_unassigned_or_apipa", "Unassigned or APIPA 169.254.x.x address", True, True, "Network"),
        Symptom("gateway_reachable", "Default gateway unreachable", False, True, "Network"),
        Symptom("gateway_failed", "Default gateway failure observed", True, True, "Network"),
        Symptom("dns_resolution_ok", "DNS failed", False, True, "Network"),
        Symptom("internet_reachable", "Internet failed", False, True, "Network"),
    ]

    # Rule Engine Check
    rule_engine = RuleEngine()
    rule_engine.load_symptoms(symptoms)
    deduced = rule_engine.run_forward_chaining()
    fault_names = [d["name"] for d in deduced]
    assert any("DHCP" in name or "IP" in name for name in fault_names)

    # Bayesian Check
    bayes = BayesianEngine()
    posteriors = bayes.compute_posteriors(symptoms)
    top_hyp = posteriors[0]
    assert top_hyp.fault_id == "fault_ip_dhcp"


def test_scenario_4_adapter_unavailable():
    """TEST 4: Adapter unavailable -> Hardware/device-level issue. NOT DNS/internet."""
    symptoms = [
        Symptom("adapter_available", "No active network adapters detected", False, True, "Network"),
        Symptom("adapter_up", "Adapter link disconnected", False, True, "Network"),
        Symptom("adapter_down", "Adapter down observed", True, True, "Network"),
        Symptom("has_valid_ip", "No IP available", False, True, "Network"),
        Symptom("gateway_reachable", "Gateway unreachable", False, True, "Network"),
        Symptom("dns_resolution_ok", "DNS failed", False, True, "Network"),
        Symptom("internet_reachable", "Internet unreachable", False, True, "Network"),
    ]

    # Rule Engine Check
    rule_engine = RuleEngine()
    rule_engine.load_symptoms(symptoms)
    deduced = rule_engine.run_forward_chaining()
    fault_names = [d["name"] for d in deduced]
    assert any("Adapter" in f for f in fault_names)

    # Bayesian Check
    bayes = BayesianEngine()
    posteriors = bayes.compute_posteriors(symptoms)
    top_hyp = posteriors[0]
    assert top_hyp.fault_id == "fault_adapter_driver"
    # Never claim DNS was the problem
    assert top_hyp.fault_id != "fault_dns_problem"


def test_scenario_5_high_ram_usage():
    """TEST 5: High RAM usage -> System health warning based on RAM usage."""
    symptoms = [
        Symptom("adapter_available", "Network adapter detected", True, False, "Network"),
        Symptom("adapter_up", "Adapter up", True, False, "Network"),
        Symptom("has_valid_ip", "Valid IP", True, False, "Network"),
        Symptom("gateway_reachable", "Gateway reachable", True, False, "Network"),
        Symptom("dns_resolution_ok", "DNS ok", True, False, "Network"),
        Symptom("internet_reachable", "Internet ok", True, False, "Network"),
        Symptom("ram_usage_high", "RAM usage >= 80%", True, True, "System Health"),
        Symptom("ram_high", "High RAM utilization observed", True, True, "System Health"),
    ]

    rule_engine = RuleEngine()
    rule_engine.load_symptoms(symptoms)
    deduced = rule_engine.run_forward_chaining()
    fault_names = [d["name"] for d in deduced]
    assert any("RAM" in name or "Memory" in name for name in fault_names)

    bayes = BayesianEngine()
    posteriors = bayes.compute_posteriors(symptoms)
    top_hyp = posteriors[0]
    assert top_hyp.fault_id == "fault_system_ram"
