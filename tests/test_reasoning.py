"""
Tests for Propositional Logic Rule Engine, Backward Chaining, and Bayesian Probabilistic Reasoning.
"""

import pytest
from ai.models import Symptom
from ai.rule_engine import RuleEngine
from ai.bayesian_engine import BayesianEngine


def test_rule_engine_dhcp_fault():
    """IF adapter up AND no valid IP AND gateway unreachable THEN IP/DHCP fault."""
    engine = RuleEngine()
    symptoms = [
        Symptom("adapter_available", "Adapter exists", True, False, "Network"),
        Symptom("adapter_up", "Adapter is enabled", True, False, "Network"),
        Symptom("has_valid_ip", "Valid IP", False, True, "Network"),
        Symptom("gateway_reachable", "Gateway reachable", False, True, "Network"),
        Symptom("dns_resolution_ok", "DNS ok", False, True, "Network")
    ]
    engine.load_symptoms(symptoms)
    deduced = engine.run_forward_chaining()

    fault_names = [d["name"] for d in deduced]
    assert any("DHCP" in name or "IP" in name for name in fault_names)


def test_rule_engine_dns_fault():
    """IF adapter up AND valid IP AND gateway reachable AND DNS fails THEN DNS fault."""
    engine = RuleEngine()
    symptoms = [
        Symptom("adapter_available", "Adapter exists", True, False, "Network"),
        Symptom("adapter_up", "Adapter is enabled", True, False, "Network"),
        Symptom("has_valid_ip", "Valid IP", True, False, "Network"),
        Symptom("gateway_reachable", "Gateway reachable", True, False, "Network"),
        Symptom("dns_resolution_ok", "DNS ok", False, True, "Network")
    ]
    engine.load_symptoms(symptoms)
    deduced = engine.run_forward_chaining()

    fault_names = [d["name"] for d in deduced]
    assert "DNS Name Resolution Failure" in fault_names


def test_backward_chaining():
    """Tests goal-directed proving of network fault."""
    engine = RuleEngine()
    symptoms = [
        Symptom("adapter_available", "Adapter exists", True, False, "Network"),
        Symptom("adapter_up", "Adapter is enabled", True, False, "Network"),
        Symptom("has_valid_ip", "Valid IP", False, True, "Network"),
        Symptom("gateway_reachable", "Gateway reachable", False, True, "Network")
    ]
    engine.load_symptoms(symptoms)
    proof = engine.run_backward_chaining("network_layer_broken")
    assert proof["proved"] is True


def test_bayesian_posterior_calculation():
    """Tests that Bayesian probabilities update properly and sum to ~1.0."""
    bayesian = BayesianEngine()
    symptoms = [
        Symptom("adapter_available", "Adapter", True, False, "Network"),
        Symptom("dns_failed", "DNS failure", True, True, "Network"),
        Symptom("gateway_failed", "Gateway failure", False, False, "Network")
    ]
    posteriors = bayesian.compute_posteriors(symptoms)

    assert len(posteriors) > 0
    total_prob = sum(h.posterior for h in posteriors)
    assert abs(total_prob - 1.0) < 0.05
    # DNS hypothesis should have top probability when dns_failed=True and gateway_failed=False
    assert posteriors[0].fault_id == "fault_dns_problem"
    assert posteriors[0].posterior > posteriors[1].posterior
