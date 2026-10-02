# AI-Based Intelligent College Lab Fault Diagnosis and Resolution Agent

### Short Name: **CollegeLab AI Agent**
**Version:** 1.0.0  
**Target Platform:** Windows 10 / Windows 11 / Windows Server (College Computer Laboratories)

---

## 1. Project Objective & Overview

Computer laboratories in colleges host dozens or hundreds of workstations utilized by students for programming, networking, data science, and software engineering. Laboratory computers frequently suffer from operational disruptions including:
- Expired or conflicting DHCP leases and APIPA autoconfig (`169.254.x.x`) IP assignments.
- Corrupted local DNS client resolver caches causing failure of web requests or repository clones.
- Stalled lab default gateway routes or isolated subnet switches.
- System memory exhaustion from unclosed student IDEs, background containers, or memory leaks.
- Disk partition space depletion from accumulated student project artifacts and build caches.
- Stalled Windows background services (such as the Print Spooler or DNS Client).

**CollegeLab AI Agent** is an autonomous desktop diagnostic and resolution agent developed specifically for college computer laboratories. Unlike mock or static dashboard demos, **CollegeLab AI Agent executes real system inspections** on the host machine, applies **Knowledge-Based Propositional Logic** and **Bayesian Probabilistic Reasoning** to diagnose the root cause, offers **predefined, non-destructive, reversible safe fixes**, and crucially performs **empirical post-repair verification** to prove whether the issue has actually been resolved.

---

## 2. Core Agent Cognitive Architecture

The intelligent agent adheres to the autonomous agent workflow:

```
              ┌──────────────────────────────────────────────┐
              │             Computer Environment             │
              └──────────────────────┬───────────────────────┘
                                     │
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │  1. PERCEIVE: Real System Sensor & Observation Layer     │
        │     - Network Diagnostic (Adapters, IP, Gateway, DNS)    │
        │     - System Health Diagnostic (CPU, RAM, Disk, Services) │
        │     - Device Hardware Diagnostic (CIM/WMI, Peripherals)  │
        └────────────────────────────┬─────────────────────────────┘
                                     │ (Observed Symptoms & Metrics)
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │  2. REASON: Knowledge Representation & Inference Engines │
        │     ├── Forward Chaining Production Rules (Logic Trace)  │
        │     ├── Goal-Directed Backward Chaining (Proof Engine)   │
        │     └── Bayesian Inference (Prior -> Likelihood -> Post) │
        └────────────────────────────┬─────────────────────────────┘
                                     │ (Diagnosed Fault & Confidence)
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │  3. DECIDE: Decision Agent & Resolution Formulation      │
        │     - Classifies Severity: Healthy / Warning / Critical   │
        │     - Selects Whitelisted Safe Repair or Manual Guidance │
        └────────────────────────────┬─────────────────────────────┘
                                     │ (Approved Action)
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │  4. ACT: Safe Resolution Engine                          │
        │     - Whitelist Validation & Admin Elevation Verification│
        │     - Non-Destructive Reversible Operations Execution    │
        └────────────────────────────┬─────────────────────────────┘
                                     │ (Post-Repair Trigger)
                                     ▼
        ┌──────────────────────────────────────────────────────────┐
        │  5. VERIFY: Empirical Post-Repair Verification Engine     │
        │     - Re-Runs Real Sensor Diagnostics                    │
        │     - Compares BEFORE vs AFTER Metric States             │
        │     - Issues Final Verdict: Resolved / Tech Required     │
        └────────────────────────────┬─────────────────────────────┘
                                     │
                                     ▼
              ┌──────────────────────────────────────────────┐
              │    Local SQLite Audit History & Lab Report   │
              └──────────────────────────────────────────────┘
```

---

## 3. Real Diagnostic Subsystems (No Mock Data)

### A. Network Diagnostics & Multi-Stage Connectivity Pipeline
Rather than simply stating "Internet Unavailable", the agent tests connectivity stage-by-stage to pinpoint the exact failure point:
1. **Stage 1: Adapter Link** — Checks if physical Ethernet or Wi-Fi hardware exists, is enabled, and is marked operational (`psutil.net_if_stats`).
2. **Stage 2: IP Configuration** — Inspects assigned IPv4 address, netmask, DHCP state, and detects APIPA autoconfig (`169.254.x.x`).
3. **Stage 3: Default Gateway** — Queries the active lab router and measures ICMP latency and packet loss.
4. **Stage 4: DNS Resolution** — Tests domain name resolution against public and lab hostnames (`google.com`, `cloudflare.com`, `wikipedia.org`).
5. **Stage 5: Internet Access** — Tests outbound TCP connections across HTTP/HTTPS/DNS ports (`1.1.1.1:80`, `8.8.8.8:53`).

### B. System Health Diagnostics
- **CPU Metrics:** Real-time overall utilization, per-core percentage, logical/physical core count, and current frequency.
  - Threshold: `< 70%` Healthy, `70-90%` Moderate, `> 90%` High.
- **RAM Metrics:** Physical memory total, available, used, and percentage.
  - Threshold: `< 60%` Healthy, `60-80%` Moderate, `> 80%` High.
- **Storage Partitions:** Real usage across all mounted volumes. Free space and percentage full.
  - Threshold: `< 85%` Healthy, `85-95%` Warning, `> 95%` or `< 5 GB free` Critical.
- **Top Processes:** Real-time top 5 processes by CPU utilization and top 5 by memory consumption.
- **Uptime:** Time elapsed since last system boot.

### C. Hardware & Device Subsystem Inspection
- Queries Windows CIM / WMI instances:
  - Processor Model, Vendor, Architecture, Max Clock.
  - Physical RAM DIMM slots, capacities, clock speeds, and vendors.
  - Physical storage drive models, media type (SSD/HDD), and SMART status.
  - Connected USB peripherals (keyboards, mice, cameras, hubs).
  - Battery/power status (laptop charge percentage, AC plugged status).
  - Graphics display adapters (GPU model, VRAM buffer, resolution, driver).
- **Physical Damage Boundary Notice:**
  > *"Software-based diagnosis cannot confirm physical component damage. Technician inspection is recommended."*  
  The agent strictly adheres to this ethical boundary and never falsely claims physical hardware damage.

---

## 4. AI Reasoning & Inference Techniques

### A. Knowledge Representation & Propositional Logic
Observable system metrics are translated into symbolic facts in working memory:
- `adapter_available`
- `adapter_up`
- `has_valid_ip`
- `gateway_reachable`
- `dns_resolution_ok`
- `internet_reachable`
- `ram_usage_high`
- `cpu_usage_high`
- `disk_space_critical`

### B. Forward Chaining Rule Engine
A forward-chaining deduction engine continually matches facts against knowledge-base production rules:
- **Rule NET-01 (IP / DHCP Fault):**
  $$\text{adapter\_available} \land \text{adapter\_up} \land \neg \text{has\_valid\_ip} \land \neg \text{gateway\_reachable} \implies \text{Fault: IP/DHCP Configuration}$$
- **Rule NET-02 (DNS Resolution Fault):**
  $$\text{adapter\_available} \land \text{adapter\_up} \land \text{has\_valid\_ip} \land \text{gateway\_reachable} \land \neg \text{dns\_resolution\_ok} \implies \text{Fault: DNS Resolution Failure}$$
- **Rule NET-03 (Gateway Switch Unreachable):**
  $$\text{adapter\_available} \land \text{adapter\_up} \land \text{has\_valid\_ip} \land \neg \text{gateway\_reachable} \land \neg \text{internet\_reachable} \implies \text{Fault: Gateway / Switch Outage}$$
- **Rule NET-04 (Adapter Disconnected):**
  $$\neg \text{adapter\_up} \implies \text{Fault: Network Adapter Disabled or Unplugged}$$
- **Rule SYS-01 (RAM Overload):**
  $$\text{ram\_usage\_high} \implies \text{Fault: System RAM Saturation}$$
- **Rule DISK-01 (Storage Full):**
  $$\text{disk\_space\_critical} \implies \text{Fault: Critical Storage Shortage}$$

### C. Goal-Directed Backward Chaining
When investigating a high-level query such as `network_layer_broken`, the engine recurses through rule premises to prove or disprove the hypothesis from working memory facts.

### D. Bayesian Probabilistic Reasoning
For each candidate fault hypothesis $H_i$, the agent computes the posterior probability using Bayes' Theorem:

$$P(H_i \mid E) = \frac{P(H_i) \cdot P(E \mid H_i)}{\sum_{k} P(H_k) \cdot P(E \mid H_k)}$$

Where:
- **Prior Probabilities $P(H_i)$** are derived from documented empirical college computer laboratory maintenance frequencies:
  - IP/DHCP lease expiration: $0.35$
  - DNS cache stall / failure: $0.25$
  - Gateway / Switch port disconnect: $0.15$
  - High RAM exhaustion: $0.12$
  - Storage space depletion: $0.08$
  - Hardware adapter failure: $0.05$
- **Likelihoods $P(s_j \mid H_i)$** represent symptom conditional probabilities calibrated to real network behaviors.
- The UI provides an **explainable step-by-step mathematical breakdown** showing prior, likelihood products, evidence marginal, and posterior calculation.

---

## 5. Safe Resolution Engine & Policy

The agent enforces strict safety boundaries:
1. **Never executes arbitrary commands.** Only actions in the predefined safe whitelist are accepted.
2. **Never deletes user files, formats drives, or modifies BIOS/firmware.**
3. **Never disables antivirus or firewall services.**
4. **Verifies Administrator elevation** before attempting privileged repairs (e.g. TCP/IP stack reset).

### Supported Predefined Safe Fixes:
| Action ID | Title | Safety Guarantee | Admin Req. |
|---|---|---|---|
| `flush_dns` | Flush DNS Resolver Cache | Only purges temporary domain name cache. Does not alter settings. | No |
| `renew_dhcp` | Release & Renew DHCP Lease | Rebroadcasts standard DHCP discover frames for a fresh IP lease. | No |
| `reset_tcp_ip` | Reset TCP/IP Stack & Winsock | Restores Winsock catalog to clean defaults. Does not delete files. | Yes |
| `restart_adapter` | Restart Network Adapter | Soft-cycles adapter interface link for 2-3 seconds. | Yes |
| `clean_temp_files` | Safe User Temp Cleanup | Deletes only unlocked files in `%TEMP%` older than 24 hours. | No |
| `restart_spooler` | Restart Print Spooler | Restarts background printing service to clear hung lab print jobs. | Yes |

---

## 6. Empirical Verification Protocol (BEFORE vs AFTER)

The agent **never assumes that a repair succeeded**. Every repair undergoes an empirical before-and-after comparison:
1. Pre-repair diagnostic indicators are snapshotted.
2. The safe fix is executed with console logging.
3. The relevant diagnostic tests are immediately re-run.
4. A comparison diff table is rendered:
   ```
   Diagnostic Indicator  | BEFORE Repair | AFTER Repair | Verification Outcome
   ----------------------|---------------|--------------|---------------------
   Default Gateway       | FAIL          | PASS         | FIXED (Resolved)
   DNS Resolution        | FAIL          | PASS         | FIXED (Resolved)
   Internet Access       | FAIL          | PASS         | FIXED (Resolved)
   ```
5. If all failures are resolved: **"Problem Resolved" (🟢)**  
   If failures persist: **"Problem Not Resolved – Technician Attention Required" (🔴)**

---

## 7. Project Structure

```
collegelabs_ai_agent/
├── main.py                     # Main application entry point (GUI & CLI)
├── agent.py                    # Autonomous Agent Orchestrator (Perceive-Reason-Decide-Act-Verify)
├── config.py                   # Lab metadata & diagnostic threshold configurations
├── build_exe.py                # Standalone Windows EXE compiler script
├── build_exe.bat               # Double-click Windows batch builder
├── run_agent.bat               # Double-click launcher
├── requirements.txt            # Python dependencies
├── README.md                   # Complete architectural and operational documentation
├── diagnostics/
│   ├── __init__.py
│   ├── network.py              # Real 5-stage network & adapter inspection
│   ├── system.py               # Real CPU, RAM, Disk, Process, Service diagnostics
│   └── device.py               # Real hardware CIM/WMI component inspection
├── ai/
│   ├── __init__.py
│   ├── models.py               # Fact, Rule, Symptom, Hypothesis dataclasses
│   ├── knowledge_base.py       # Production rules, priors, likelihood matrices
│   ├── rule_engine.py          # Forward and Backward Chaining inference engines
│   └── bayesian_engine.py      # Bayesian probability calculator and explainability
├── resolution/
│   ├── __init__.py
│   └── safe_fixes.py           # Predefined safe fix registry and executor
├── verification/
│   ├── __init__.py
│   └── verifier.py             # Empirical BEFORE vs AFTER comparison engine
├── database/
│   ├── __init__.py
│   └── history.py              # Local SQLite database for audit trail & CSV export
├── ui/
│   ├── __init__.py
│   ├── theme.py                # Custom dark slate laboratory theme & typography
│   ├── components.py           # Stat cards, Status badges, Gauges, Terminal console
│   ├── dialogs.py              # Lab Settings configuration modal
│   ├── app.py                  # Main window coordinating views & background threading
│   └── views/
│       ├── __init__.py
│       ├── dashboard_view.py   # System specs, lab identity, status cards
│       ├── diagnostics_runner_view.py # Multi-stage pipeline & scan execution
│       ├── reasoning_view.py   # AI Diagnosis, Evidence list, Bayesian formulas
│       ├── resolution_view.py  # Safe Fix runner & Before/After verification diff
│       ├── hardware_view.py    # Detailed hardware inventory & disclaimer
│       └── history_view.py     # Local audit logs with CSV export
└── tests/
    ├── __init__.py
    ├── test_diagnostics.py     # Real sensor diagnostic unit tests
    ├── test_reasoning.py       # Propositional Logic & Bayesian engine tests
    ├── test_safe_fixes.py      # Whitelist enforcement & safety guarantee tests
    └── test_history.py         # SQLite logging & CSV export unit tests
```

---

## 8. Installation & Execution Guide

### Prerequisites
- Windows 10 or Windows 11 (64-bit).
- Python 3.10+ (if running from source).
- Administrator privileges (recommended for network resets and service restarts).

### Running from Source
1. Open PowerShell or Command Prompt in the project folder:
   ```powershell
   cd C:\Users\KASTHURI\.gemini\antigravity-ide\scratch\collegelabs_ai_agent
   ```
2. Install requirements:
   ```powershell
   pip install -r requirements.txt
   ```
3. Run the desktop application:
   ```powershell
   python main.py
   ```
   Or double-click `run_agent.bat`.

### Command Line Interface (CLI) Mode
For automated lab maintenance scripts, run in headless mode:
```powershell
python main.py --cli --scan full
```

### Running Automated Test Suite
Run the 10 automated unit tests:
```powershell
python -m pytest -v
```

---

## 9. Windows Standalone Executable (`CollegeLabAI.exe`)

The application can be packaged into a standalone Windows executable that runs without requiring Python:

### Building `CollegeLabAI.exe`:
Run the compiler script:
```powershell
python build_exe.py
```
Or double-click `build_exe.bat`.

The compiled executable will be located at:
`dist\CollegeLabAI.exe`

### Lab Deployment Instructions:
1. Copy `CollegeLabAI.exe` to a USB flash drive or laboratory network share.
2. Copy it onto any target college laboratory computer.
3. Right-click `CollegeLabAI.exe` and select **"Run as administrator"** (for full network reset capabilities).
4. Configure the **Lab Settings** (Lab Name, Computer ID, Room).
5. Run scans, view real diagnostic telemetry, execute safe repairs, and verify results.

---

## 10. Demonstration Scenario

Here is how to demonstrate the agent during an evaluation or college presentation:

1. **Initial Perception:**
   - Launch `CollegeLabAI.exe`.
   - The application automatically gathers real specs (Hostname, OS, CPU model, RAM modules, Disks, IPv4 address).
2. **Execute Diagnostic Scan:**
   - Click **[ RUN QUICK SCAN ]** or **[ FULL DIAGNOSTIC ]**.
   - Watch the multi-stage network pipeline evaluate:
     `Adapter [PASS] → IP [PASS] → Gateway [PASS] → DNS [PASS] → Internet [PASS]`
3. **Inspect AI Reasoning:**
   - Open the **🧠 AI Reasoning & Diagnosis** tab.
   - Inspect the **Observed Sensory Evidence** checklist (`✔ PASS` / `✖ FAIL`).
   - Examine the **Bayesian Probabilistic Diagnosis** table showing prior probabilities vs posterior scores.
   - Click any candidate fault to view the exact mathematical formula derivation.
   - Inspect the **Forward Chaining Inference Trace** showing which rules fired.
4. **Execute Safe Fix & Verify:**
   - Open the **🛠 Safe Resolution & Verify** tab.
   - Select an action (e.g. `Flush DNS Resolver Cache` or `Release and Renew DHCP Lease`).
   - Click **[ EXECUTE SAFE FIX & VERIFY ]**.
   - Confirm the safety warning dialog.
   - The agent executes the safe fix, re-runs diagnostics, computes the delta, and presents the **BEFORE vs AFTER comparison table** with the final verdict: **"Problem Resolved" (🟢)**.
5. **Audit History & Report Export:**
   - Open the **📋 Local Audit History** tab.
   - Click **[ Export CSV Report ]** to generate a lab technician maintenance log.
    

DEMO Video 
     https://drive.google.com/file/d/1vLJdI4SGuArnwYEyxLpRx24AAzQMfFBJ/view?usp=drivesdk   )
