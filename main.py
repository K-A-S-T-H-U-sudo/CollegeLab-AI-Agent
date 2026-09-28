"""
AI-Based Intelligent College Lab Fault Diagnosis and Resolution Agent
Short Name: CollegeLab AI Agent
Entry point module.
"""

import sys
import os
import argparse

# Ensure current directory is in Python module search path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from config import APP_TITLE, APP_SHORT_NAME, APP_SUBTITLE, APP_VERSION, lab_config
from agent import CollegeLabAgent


def run_cli_mode(scan_mode: str = "full"):
    """Runs a non-interactive diagnostic scan directly in the terminal."""
    print("=" * 70)
    print(f"{APP_TITLE}")
    print(f"[{APP_SHORT_NAME}] v{APP_VERSION} - CLI Mode")
    print(f"LAB: {lab_config.lab_name} | STATION: {lab_config.computer_id} | ROOM: {lab_config.room}")
    print("=" * 70)

    agent = CollegeLabAgent()
    print(f"[*] Perceiving system state (mode: {scan_mode})...")
    raw = agent.perceive(scan_mode=scan_mode)

    print("[*] Reasoning through Logic and Bayesian Engines...")
    report = agent.decide()

    print("\n" + "=" * 35 + " DIAGNOSIS REPORT " + "=" * 35)
    print(f"Timestamp:          {report.timestamp}")
    print(f"Computer ID:        {report.computer_id}")
    print(f"Primary Fault:      {report.primary_fault}")
    print(f"Category:           {report.category}")
    print(f"Confidence:         {report.confidence} ({int(report.confidence_score * 100)}%)")
    print(f"Overall Status:     {report.overall_status}")
    print(f"Recommended Action: {report.recommended_action}")
    if report.action_key:
        print(f"Action Key:         {report.action_key}")

    print("\n--- OBSERVED EVIDENCE ---")
    for ev in report.evidence:
        marker = "[OK]" if ev["passed"] else "[FAIL]"
        print(f"  {marker:6s} {ev['description']}")

    print("\n--- TOP BAYESIAN CANDIDATES ---")
    for b in report.bayesian_rankings[:3]:
        print(f"  {b['name']:40s} | Posterior: {b['posterior']*100:5.1f}% | Prior: {b['prior']*100:4.1f}%")

    print("\n--- FORWARD CHAINING RULES FIRED ---")
    fired = [line for line in report.reasoning_trace if "-> FIRED" in line]
    if fired:
        for f in fired:
            print(f"  {f}")
    else:
        print("  All nominal rules evaluated. No abnormal production rules fired.")

    print("\n" + "=" * 70)


def main():
    parser = argparse.ArgumentParser(description=f"{APP_TITLE} ({APP_SHORT_NAME})")
    parser.add_argument("--cli", action="store_true", help="Run in headless Command Line Interface mode")
    parser.add_argument("--scan", type=str, default="full", choices=["quick", "full", "network", "system", "device"], help="Diagnostic scan mode for CLI")
    parser.add_argument("--version", action="version", version=f"{APP_SHORT_NAME} v{APP_VERSION}")

    args = parser.parse_args()

    if args.cli:
        run_cli_mode(scan_mode=args.scan)
    else:
        # Launch Desktop GUI
        from ui.app import run_app
        run_app()


if __name__ == "__main__":
    main()
