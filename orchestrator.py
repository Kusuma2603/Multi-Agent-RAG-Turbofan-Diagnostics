import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

"""
Step 4: Orchestrator agent.
Takes the engineer's query, sends it to all 3 agents in parallel,
then merges results into a structured diagnostic report.
"""

from concurrent.futures import ThreadPoolExecutor
from agents import fault_classifier_agent, symptom_analyzer_agent, maintenance_advisor_agent


def run_diagnostic(query: str) -> dict:
    print("[Orchestrator] Dispatching query to all agents...")

    with ThreadPoolExecutor(max_workers=3) as executor:
        future_fault    = executor.submit(fault_classifier_agent,   query)
        future_symptom  = executor.submit(symptom_analyzer_agent,   query)
        future_advice   = executor.submit(maintenance_advisor_agent, query)

        fault_result    = future_fault.result()
        symptom_result  = future_symptom.result()
        advice_result   = future_advice.result()

    print("[Orchestrator] All agents responded. Assembling report...")

    report = {
        "query":                query,
        "fault_classification": fault_result,
        "symptom_analysis":     symptom_result,
        "maintenance_advice":   advice_result,
    }
    return report


def format_report(report: dict) -> str:
    divider = "=" * 60
    return f"""
{divider}
TURBOFAN ENGINE DIAGNOSTIC REPORT
{divider}

ENGINEER QUERY:
{report['query']}

{divider}
[AGENT 1] FAULT CLASSIFICATION
{divider}
{report['fault_classification']}

{divider}
[AGENT 2] SYMPTOM ANALYSIS
{divider}
{report['symptom_analysis']}

{divider}
[AGENT 3] MAINTENANCE RECOMMENDATION
{divider}
{report['maintenance_advice']}

{divider}
"""


if __name__ == "__main__":
    test_query = (
        "The engine is showing EGT values of 820°C at cruise, "
        "N1 is stable at 92%, but we're seeing vibration levels of 5.8 mils "
        "and a slight smell of burnt oil near the rear casing."
    )
    report = run_diagnostic(test_query)
    print(format_report(report))