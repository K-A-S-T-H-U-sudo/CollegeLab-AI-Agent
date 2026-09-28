"""
Automated Test Runner for CollegeLab AI Agent.
Runs all unit and integration tests across diagnostic, reasoning, database, and scenario modules.
"""

import sys
import os

# Ensure local directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tests.test_diagnostics as td
import tests.test_history as th
import tests.test_reasoning as tr
import tests.test_safe_fixes as ts
import tests.test_agent_scenarios as tas


def run_all_tests():
    test_functions = [
        # Real diagnostic modules
        ("test_network_diagnostic", td.test_network_diagnostic),
        ("test_system_health_diagnostic", td.test_system_health_diagnostic),
        ("test_device_diagnostic", td.test_device_diagnostic),

        # History DB
        ("test_history_logging_and_export", th.test_history_logging_and_export),

        # Reasoning & Bayesian Engine
        ("test_rule_engine_dhcp_fault", tr.test_rule_engine_dhcp_fault),
        ("test_rule_engine_dns_fault", tr.test_rule_engine_dns_fault),
        ("test_backward_chaining", tr.test_backward_chaining),
        ("test_bayesian_posterior_calculation", tr.test_bayesian_posterior_calculation),

        # Safe fixes
        ("test_registry_safety_guarantees", ts.test_registry_safety_guarantees),
        ("test_whitelist_rejection", ts.test_whitelist_rejection),

        # Section 17 Scenarios
        ("test_scenario_1_healthy_network", tas.test_scenario_1_healthy_network),
        ("test_scenario_2_dns_failure", tas.test_scenario_2_dns_failure),
        ("test_scenario_3_no_valid_ip", tas.test_scenario_3_no_valid_ip),
        ("test_scenario_4_adapter_unavailable", tas.test_scenario_4_adapter_unavailable),
        ("test_scenario_5_high_ram_usage", tas.test_scenario_5_high_ram_usage),
    ]

    print("=" * 60)
    print("COLLEGELAB AI AGENT - COMPREHENSIVE TEST SUITE")
    print("=" * 60)

    passed = 0
    failed = 0

    for name, fn in test_functions:
        try:
            fn()
            print(f"[PASS] {name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {name}: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_functions)} tests.")
    print("=" * 60)

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
