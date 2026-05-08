"""
Step 1: Generate a synthetic turbofan engine fault dataset.
Run this first before ingest.py.
Creates: data/turbofan_faults.json (~50 scenarios)
"""

import json
import os
import random

random.seed(42)

OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "turbofan_faults.json")

FAULT_TEMPLATES = [
    {
        "fault_type": "Turbine Blade Erosion",
        "symptoms_pool": [
            "increased EGT at cruise", "reduced thrust output", "slight smoke from exhaust",
            "higher fuel consumption", "decreased N1 response"
        ],
        "egt_range": (780, 850),
        "n1_range": (88, 95),
        "n2_range": (94, 99),
        "vib_range": (3.0, 6.0),
        "severity_pool": ["Moderate", "High"],
        "actions": [
            "Perform borescope inspection of HPT blades. Replace blades exceeding wear limits. "
            "Check turbine clearances. Log EGT margin trend before return to service.",
            "Immediate borescope inspection required. Ground aircraft if blade tip loss is confirmed. "
            "HPT blade replacement mandatory before next flight.",
        ],
        "notes_pool": [
            "Common after high-cycle operation in sandy environments.",
            "EGT margin reduction of >15°C from baseline is a red flag.",
            "Monitor EGT trend data over the last 50 cycles for confirmation.",
        ],
    },
    {
        "fault_type": "Compressor Stall",
        "symptoms_pool": [
            "loud bang during acceleration", "EGT spike above limits", "N1 fluctuation",
            "airframe shudder", "temporary thrust loss", "abnormal compressor noise"
        ],
        "egt_range": (770, 840),
        "n1_range": (82, 96),
        "n2_range": (90, 98),
        "vib_range": (2.5, 5.5),
        "severity_pool": ["High", "Critical"],
        "actions": [
            "Reduce thrust immediately. Inspect compressor blades for FOD or damage. "
            "Check bleed air valves and variable stator vane schedule. Do not dispatch until root cause found.",
            "Ground aircraft. Perform full compressor borescope. Inspect bleed valves and inlet for blockage. "
            "Review engine control unit (ECU) fault codes.",
        ],
        "notes_pool": [
            "Often triggered by FOD ingestion or icing conditions.",
            "Repeated stalls indicate degraded stall margin — check HPT clearances.",
            "ECU fault code P0420 or similar may be logged. Pull ACARS data for confirmation.",
        ],
    },
    {
        "fault_type": "Oil System Degradation",
        "symptoms_pool": [
            "low oil pressure warning", "high oil temperature", "oil consumption above limits",
            "oil fumes in cabin bleed air", "chip detector warning", "milky oil appearance"
        ],
        "egt_range": (680, 760),
        "n1_range": (88, 95),
        "n2_range": (93, 99),
        "vib_range": (1.5, 4.0),
        "severity_pool": ["Moderate", "High", "Critical"],
        "actions": [
            "Sample oil and send for spectrometric analysis. Check chip detector for metallic debris. "
            "Inspect oil cooler, seals, and scavenge lines. Top up oil within approved limits.",
            "Ground aircraft if chip detector shows metal particles. Perform full bearing inspection. "
            "Replace oil filter and flush system before return to service.",
        ],
        "notes_pool": [
            "Milky oil indicates water contamination — likely a cooler seal failure.",
            "High iron/silver content in oil sample suggests bearing wear.",
            "Monitor oil quantity trending. Loss >0.3 qt/hr requires investigation.",
        ],
    },
    {
        "fault_type": "Fan Blade Imbalance",
        "symptoms_pool": [
            "high vibration in fan section", "airframe vibration at cruise", "N1 speed oscillation",
            "unusual noise from fan cowl", "visible fan blade nick or damage"
        ],
        "egt_range": (670, 740),
        "n1_range": (88, 96),
        "n2_range": (94, 99),
        "vib_range": (5.0, 9.5),
        "severity_pool": ["Moderate", "High"],
        "actions": [
            "Perform fan trim balance. Inspect all fan blades for nicks, dents, or FOD damage. "
            "Check spinner for cracks. Re-balance fan assembly if within limits.",
            "If vibration >8 mils, ground aircraft. Inspect fan blades per AMM limits. "
            "Replace damaged blade and perform full fan balance before dispatch.",
        ],
        "notes_pool": [
            "FOD strikes are the most common cause — inspect inlet carefully.",
            "Vibration asymmetry between left and right accelerometers confirms fan source.",
            "Fan blade replacement requires weight-matched replacement blade from same set.",
        ],
    },
    {
        "fault_type": "Fuel System Leak",
        "symptoms_pool": [
            "fuel flow higher than expected", "fuel smell near nacelle", "visible fuel stain on cowl",
            "low fuel pressure warning", "unexpected fuel imbalance between tanks"
        ],
        "egt_range": (680, 750),
        "n1_range": (88, 95),
        "n2_range": (93, 98),
        "vib_range": (1.0, 3.0),
        "severity_pool": ["High", "Critical"],
        "actions": [
            "Identify leak source — check fuel manifold, supply lines, and fuel nozzle fittings. "
            "Isolate affected circuit. Replace leaking component and pressure-test before return to service.",
            "Ground aircraft immediately. Perform full fuel system leak check per AMM. "
            "Do not dispatch with any active fuel leak.",
        ],
        "notes_pool": [
            "Check fuel nozzle O-rings — they harden and crack with age.",
            "Fuel imbalance >500 lbs unexplained by normal use requires investigation.",
            "Inspect fuel manifold joints during every 'C' check as a preventive measure.",
        ],
    },
    {
        "fault_type": "Hot Section Deterioration",
        "symptoms_pool": [
            "EGT creep over multiple flights", "reduced thrust at fixed throttle", "increased TSFC",
            "higher fuel burn at cruise", "EGT margin below minimum"
        ],
        "egt_range": (790, 860),
        "n1_range": (86, 93),
        "n2_range": (93, 98),
        "vib_range": (2.0, 4.5),
        "severity_pool": ["Moderate", "High"],
        "actions": [
            "Perform full hot section borescope. Measure EGT margin against baseline. "
            "If margin is <20°C, schedule engine removal for shop visit.",
            "Trend monitor EGT over next 10 cycles. If degradation continues, pull engine "
            "for HPT and combustor inspection. Check for liner burnthrough or NGV cracking.",
        ],
        "notes_pool": [
            "EGT margin is the primary indicator of hot section health.",
            "Gradual deterioration is normal — sudden step change indicates acute damage.",
            "Review last borescope images for combustor liner condition.",
        ],
    },
    {
        "fault_type": "Variable Stator Vane Malfunction",
        "symptoms_pool": [
            "compressor stall at specific N1 range", "EGT anomaly during acceleration",
            "erratic N1 response", "VSV actuator fault code", "asymmetric compressor noise"
        ],
        "egt_range": (740, 810),
        "n1_range": (80, 95),
        "n2_range": (90, 98),
        "vib_range": (2.0, 5.0),
        "severity_pool": ["Moderate", "High"],
        "actions": [
            "Check VSV actuator rigging and range of motion. Inspect VSV feedback LVDT. "
            "Verify VSV schedule matches ECU commands. Replace actuator if out of rig.",
            "Download ECU fault history. Perform VSV full-range functional test. "
            "If actuator binding found, replace and re-rig per AMM before dispatch.",
        ],
        "notes_pool": [
            "VSV faults often trigger ACARS EICAS message — pull full fault history.",
            "Check for ice ingestion if fault occurred during descent through icing conditions.",
            "LVDT signal dropout is a common root cause — check connector integrity.",
        ],
    },
    {
        "fault_type": "Bearing Failure",
        "symptoms_pool": [
            "chip detector alert", "high vibration N1 or N2", "abnormal noise at idle",
            "oil temperature rising", "metal particles in oil sample", "sudden vibration onset"
        ],
        "egt_range": (690, 760),
        "n1_range": (88, 95),
        "n2_range": (93, 99),
        "vib_range": (6.0, 12.0),
        "severity_pool": ["High", "Critical"],
        "actions": [
            "Ground aircraft immediately. Chip detector positive means potential bearing failure. "
            "Perform oil spectral analysis. Do not operate engine until bearing inspection is complete.",
            "Pull engine for shop visit. Inspect No.1, No.3, and No.4 bearings. "
            "Replace all bearings in the affected sump. Flush oil system and replace filter.",
        ],
        "notes_pool": [
            "Chip detector activations should ALWAYS be treated as serious until proven otherwise.",
            "Metallic particle shape indicates failure mode — flakes suggest spalling, fines suggest wear.",
            "Vibration signature analysis (frequency spectrum) can pinpoint which bearing is failing.",
        ],
    },
]


def generate_scenario(scenario_id: int, template: dict) -> dict:
    symptoms = random.sample(template["symptoms_pool"], k=random.randint(2, 4))
    egt = round(random.uniform(*template["egt_range"]), 1)
    n1 = round(random.uniform(*template["n1_range"]), 1)
    n2 = round(random.uniform(*template["n2_range"]), 1)
    vib = round(random.uniform(*template["vib_range"]), 2)
    severity = random.choice(template["severity_pool"])
    action = random.choice(template["actions"])
    note = random.choice(template["notes_pool"])

    return {
        "id": scenario_id,
        "fault_type": template["fault_type"],
        "symptoms": symptoms,
        "sensor_readings": {
            "EGT_degC": egt,
            "N1_percent": n1,
            "N2_percent": n2,
            "vibration_mils": vib,
        },
        "severity": severity,
        "recommended_action": action,
        "notes": note,
    }


def main():
    scenarios = []
    scenario_id = 1

    # Generate ~6 scenarios per fault type → ~48 total
    for template in FAULT_TEMPLATES:
        for _ in range(6):
            scenarios.append(generate_scenario(scenario_id, template))
            scenario_id += 1

    random.shuffle(scenarios)

    # Re-assign sequential IDs after shuffle
    for i, s in enumerate(scenarios, start=1):
        s["id"] = i

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w") as f:
        json.dump(scenarios, f, indent=2)

    print(f"✅ Generated {len(scenarios)} scenarios → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
