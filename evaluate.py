"""
Voltex Repair Triage Agent
evaluate.py — Evaluation Pipeline

Runs 20 test scenarios through the triage agent and scores each result.

Scoring dimensions per scenario (max 5 points):
  - correct_repair_path (0/1): right routing decision
  - correct_coverage    (0/1): right coverage type identified
  - correct_ber         (0/1): BER flag correct
  - correct_escalation  (0/1): escalation flag correct
  - correct_urgency     (0/1): urgency level correct

Overall score: sum / (20 * 5) as percentage
"""

import json
import time
from pathlib import Path
from datetime import datetime
from agent import RepairTriageAgent

# ─────────────────────────────────────────────
# TEST SCENARIOS — 20 CASES
# ─────────────────────────────────────────────

TEST_SCENARIOS = [

    # ── TECH BAR REPAIRS ─────────────────────
    {
        "id"                 : "T01",
        "name"               : "Laptop screen crack — VoltCare Plus",
        "fault_description"  : "Dropped laptop, cracked screen. Display still works with crack.",
        "product_type"       : "laptop",
        "product_age_months" : 8,
        "product_value"      : 750.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "plus",
        "is_accidental_damage": True,
        "expected_repair_path": "tech_bar",
        "expected_coverage"  : ["voltcare_plus_ad", "manufacturer_warranty"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["LOW", "MEDIUM"],
        "notes"              : "Screen replacement at Tech Bar, VoltCare Plus AD or manufacturer warranty"
    },
    {
        "id"                 : "T02",
        "name"               : "Laptop battery replacement — CRA",
        "fault_description"  : "Laptop battery drains completely within 30 minutes. Swollen battery pushing trackpad up.",
        "product_type"       : "laptop",
        "product_age_months" : 18,
        "product_value"      : 600.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "tech_bar",
        "expected_coverage"  : ["consumer_rights_act", "voltcare_essential", "voltcare_plus"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["LOW", "MEDIUM"],
        "notes"              : "Battery fault, CRA applies at 18 months, Tech Bar repair"
    },
    {
        "id"                 : "T03",
        "name"               : "Phone screen crack — in warranty",
        "fault_description"  : "Dropped phone, screen cracked. Touchscreen not responding on left side.",
        "product_type"       : "phone",
        "product_age_months" : 5,
        "product_value"      : 500.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "plus",
        "is_accidental_damage": True,
        "expected_repair_path": "tech_bar",
        "expected_coverage"  : ["voltcare_plus_ad", "manufacturer_warranty"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["LOW", "MEDIUM"],
        "notes"              : "Phone screen, Tech Bar, VoltCare Plus or manufacturer warranty"
    },
    {
        "id"                 : "T04",
        "name"               : "TV smart features not working",
        "fault_description"  : "Smart TV apps keep crashing. Netflix and YouTube won't load. WiFi shows connected.",
        "product_type"       : "tv",
        "product_age_months" : 10,
        "product_value"      : 500.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "essential",
        "is_accidental_damage": False,
        "expected_repair_path": "tech_bar",
        "expected_coverage"  : ["voltcare_essential", "manufacturer_warranty"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["LOW", "MEDIUM"],
        "notes"              : "Software fault, Tech Bar can handle, manufacturer warranty or VoltCare"
    },

    # ── NEWARK REPAIRS ───────────────────────
    {
        "id"                 : "T05",
        "name"               : "Phone liquid damage — VoltCare Complete",
        "fault_description"  : "Spilled coffee on phone. Phone turned off, speaker muffled, buttons unresponsive.",
        "product_type"       : "phone",
        "product_age_months" : 14,
        "product_value"      : 650.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "complete",
        "is_accidental_damage": True,
        "expected_repair_path": "newark",
        "expected_coverage"  : ["voltcare_complete"],
        "expected_ber"       : False,
        "expected_escalation": True,
        "expected_urgency"   : ["HIGH"],
        "notes"              : "Liquid damage always Newark, Complete = HIGH urgency, escalate"
    },
    {
        "id"                 : "T06",
        "name"               : "Laptop motherboard failure — no coverage",
        "fault_description"  : "Laptop completely dead. Won't turn on at all. No lights, no fan, nothing.",
        "product_type"       : "laptop",
        "product_age_months" : 30,
        "product_value"      : 800.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "newark",
        "expected_coverage"  : ["consumer_rights_act", "no_coverage"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "Motherboard failure, Newark specialist, CRA may apply at 30 months"
    },
    {
        "id"                 : "T07",
        "name"               : "TV backlight failure — VoltCare Complete",
        "fault_description"  : "TV screen gone dark but can faintly see picture with torch. Backlight failed.",
        "product_type"       : "tv",
        "product_age_months" : 26,
        "product_value"      : 600.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "complete",
        "is_accidental_damage": False,
        "expected_repair_path": "newark",
        "expected_coverage"  : ["voltcare_complete"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["HIGH"],
        "notes"              : "Backlight is display fault, Newark, Complete = HIGH urgency"
    },
    {
        "id"                 : "T08",
        "name"               : "Phone charging port — no VoltCare",
        "fault_description"  : "Phone won't charge. Tried multiple cables. Charging port looks damaged.",
        "product_type"       : "phone",
        "product_age_months" : 20,
        "product_value"      : 400.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "newark",
        "expected_coverage"  : ["consumer_rights_act", "no_coverage"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "Charging port is connectivity fault, Newark, CRA at 20 months"
    },

    # ── ENGINEER REPAIRS ─────────────────────
    {
        "id"                 : "T09",
        "name"               : "Washing machine not draining — CRA",
        "fault_description"  : "Water not draining. Standing water at bottom after every cycle.",
        "product_type"       : "washing_machine",
        "product_age_months" : 36,
        "product_value"      : 450.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "engineer",
        "expected_coverage"  : ["consumer_rights_act"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "Drain pump fault, engineer visit, CRA at 36 months"
    },
    {
        "id"                 : "T10",
        "name"               : "Washing machine drum bearing — VoltCare Essential",
        "fault_description"  : "Very loud banging noise during spin cycle. Drum seems loose.",
        "product_type"       : "washing_machine",
        "product_age_months" : 24,
        "product_value"      : 500.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "essential",
        "is_accidental_damage": False,
        "expected_repair_path": "engineer",
        "expected_coverage"  : ["voltcare_essential"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "Bearing failure, engineer, VoltCare Essential covers breakdown"
    },
    {
        "id"                 : "T11",
        "name"               : "Fridge door seal — simple fix",
        "fault_description"  : "Fridge door not sealing properly. Food not staying cold enough. Door seal damaged.",
        "product_type"       : "fridge_freezer",
        "product_age_months" : 28,
        "product_value"      : 500.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "engineer",
        "expected_coverage"  : ["consumer_rights_act"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM", "LOW"],
        "notes"              : "Door seal is mechanical fault, simple engineer fix, CRA applies"
    },
    {
        "id"                 : "T12",
        "name"               : "Dishwasher not draining — VoltCare Plus",
        "fault_description"  : "Dishwasher not draining properly. Standing water at bottom after cycle.",
        "product_type"       : "dishwasher",
        "product_age_months" : 15,
        "product_value"      : 350.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "plus",
        "is_accidental_damage": False,
        "expected_repair_path": "engineer",
        "expected_coverage"  : ["voltcare_plus", "manufacturer_warranty"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "Water drainage fault, engineer, VoltCare Plus or manufacturer warranty"
    },

    # ── BER / REPLACE ────────────────────────
    {
        "id"                 : "T13",
        "name"               : "Fridge compressor failure — BER",
        "fault_description"  : "Fridge completely stopped cooling. Compressor clicking then going quiet. Food spoiling.",
        "product_type"       : "fridge_freezer",
        "product_age_months" : 84,
        "product_value"      : 280.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "replace",
        "expected_coverage"  : ["no_coverage"],
        "expected_ber"       : True,
        "expected_escalation": True,
        "expected_urgency"   : ["HIGH", "MEDIUM"],
        "notes"              : "Compressor repair £255 vs £280 product value = 91% BER threshold exceeded"
    },
    {
        "id"                 : "T14",
        "name"               : "Old laptop motherboard — BER",
        "fault_description"  : "Laptop completely dead. Board fried. Multiple components shorted.",
        "product_type"       : "laptop",
        "product_age_months" : 60,
        "product_value"      : 300.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "replace",
        "expected_coverage"  : ["no_coverage"],
        "expected_ber"       : True,
        "expected_escalation": True,
        "expected_urgency"   : ["HIGH", "MEDIUM"],
        "notes"              : "Motherboard £250 labour + parts vs £300 product value = BER"
    },

    # ── COVERAGE EDGE CASES ──────────────────
    {
        "id"                 : "T15",
        "name"               : "VoltCare Essential — AD not covered",
        "fault_description"  : "Knocked TV off stand. Screen cracked and TV won't turn on.",
        "product_type"       : "tv",
        "product_age_months" : 18,
        "product_value"      : 700.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "essential",
        "is_accidental_damage": True,
        "expected_repair_path": "newark",
        "expected_coverage"  : ["voltcare_essential", "no_coverage", "consumer_rights_act"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "Essential does not cover AD — customer pays or CRA if manufacturing defect"
    },
    {
        "id"                 : "T16",
        "name"               : "VoltCare Complete — washing machine motor",
        "fault_description"  : "Washing machine motor completely failed. Machine won't spin at all.",
        "product_type"       : "washing_machine",
        "product_age_months" : 30,
        "product_value"      : 600.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "complete",
        "is_accidental_damage": False,
        "expected_repair_path": "engineer",
        "expected_coverage"  : ["voltcare_complete"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["HIGH"],
        "notes"              : "Complete covers motor failure, engineer, HIGH urgency from 48hr SLA"
    },
    {
        "id"                 : "T17",
        "name"               : "Manufacturer warranty — new fridge fault",
        "fault_description"  : "Brand new fridge making loud compressor noise from day one. Not cooling properly.",
        "product_type"       : "fridge_freezer",
        "product_age_months" : 2,
        "product_value"      : 800.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "engineer",
        "expected_coverage"  : ["manufacturer_warranty"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "2 months old, manufacturer warranty, engineer visit"
    },

    # ── ESCALATION TRIGGERS ──────────────────
    {
        "id"                 : "T18",
        "name"               : "Liquid damage — laptop — escalate",
        "fault_description"  : "Spilled water on laptop keyboard. Some keys not working and screen flickering.",
        "product_type"       : "laptop",
        "product_age_months" : 16,
        "product_value"      : 900.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "plus",
        "is_accidental_damage": True,
        "expected_repair_path": "newark",
        "expected_coverage"  : ["voltcare_plus_ad"],
        "expected_ber"       : False,
        "expected_escalation": True,
        "expected_urgency"   : ["MEDIUM", "HIGH"],
        "notes"              : "Liquid damage always escalates regardless of coverage"
    },
    {
        "id"                 : "T19",
        "name"               : "Ambiguous fault — LOW confidence",
        "fault_description"  : "Phone just stopped working. Nothing happened to it.",
        "product_type"       : "phone",
        "product_age_months" : 9,
        "product_value"      : 550.0,
        "has_voltcare"       : False,
        "voltcare_tier"      : None,
        "is_accidental_damage": False,
        "expected_repair_path": "newark",
        "expected_coverage"  : ["manufacturer_warranty", "consumer_rights_act"],
        "expected_ber"       : False,
        "expected_escalation": True,
        "expected_urgency"   : ["MEDIUM"],
        "notes"              : "Vague description should produce LOW confidence and escalate"
    },
    {
        "id"                 : "T20",
        "name"               : "Fridge cooling fault — VoltCare Complete high urgency",
        "fault_description"  : "Fridge stopped cooling entirely. Freezer still works but fridge compartment warm.",
        "product_type"       : "fridge_freezer",
        "product_age_months" : 20,
        "product_value"      : 700.0,
        "has_voltcare"       : True,
        "voltcare_tier"      : "complete",
        "is_accidental_damage": False,
        "expected_repair_path": "engineer",
        "expected_coverage"  : ["voltcare_complete"],
        "expected_ber"       : False,
        "expected_escalation": False,
        "expected_urgency"   : ["HIGH"],
        "notes"              : "Cooling fault on Complete = HIGH urgency 48hr SLA, engineer visit"
    },
]


# ─────────────────────────────────────────────
# SCORING FUNCTIONS
# ─────────────────────────────────────────────

def score_repair_path(actual: str, expected: str) -> int:
    return 1 if actual == expected else 0


def score_coverage(actual: str, expected_list: list) -> int:
    return 1 if any(exp in actual for exp in expected_list) else 0


def score_ber(actual: bool, expected: bool) -> int:
    return 1 if actual == expected else 0


def score_escalation(actual: bool, expected: bool) -> int:
    return 1 if actual == expected else 0


def score_urgency(actual: str, expected_list: list) -> int:
    return 1 if actual in expected_list else 0


# ─────────────────────────────────────────────
# MAIN EVALUATION LOOP
# ─────────────────────────────────────────────

def main():
    print("=" * 65)
    print("Voltex Repair Triage Agent — Evaluation Pipeline")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Scenarios: {len(TEST_SCENARIOS)}")
    print("=" * 65)

    agent   = RepairTriageAgent()
    results = []
    path_scores = {"tech_bar": [], "newark": [], "engineer": [], "replace": []}

    for i, test in enumerate(TEST_SCENARIOS, 1):
        print(f"\n[{i:02d}/{len(TEST_SCENARIOS)}] {test['id']} — {test['name'][:55]}...")

        try:
            result = agent.triage(
                fault_description    = test["fault_description"],
                product_type         = test["product_type"],
                product_age_months   = test["product_age_months"],
                product_value        = test["product_value"],
                has_voltcare         = test["has_voltcare"],
                voltcare_tier        = test["voltcare_tier"],
                is_accidental_damage = test["is_accidental_damage"],
            )

            brief = result["brief"]

            s_path     = score_repair_path(brief.repair_path, test["expected_repair_path"])
            s_coverage = score_coverage(brief.coverage_type, test["expected_coverage"])
            s_ber      = score_ber(brief.is_ber, test["expected_ber"])
            s_escalate = score_escalation(brief.escalate, test["expected_escalation"])
            s_urgency  = score_urgency(brief.urgency, test["expected_urgency"])
            total      = s_path + s_coverage + s_ber + s_escalate + s_urgency

            record = {
                "id"               : test["id"],
                "name"             : test["name"],
                "expected_path"    : test["expected_repair_path"],
                "actual_path"      : brief.repair_path,
                "expected_coverage": test["expected_coverage"],
                "actual_coverage"  : brief.coverage_type,
                "expected_ber"     : test["expected_ber"],
                "actual_ber"       : brief.is_ber,
                "expected_escalate": test["expected_escalation"],
                "actual_escalate"  : brief.escalate,
                "expected_urgency" : test["expected_urgency"],
                "actual_urgency"   : brief.urgency,
                "confidence"       : brief.confidence,
                "reasoning"        : brief.reasoning_summary,
                "s_path"           : s_path,
                "s_coverage"       : s_coverage,
                "s_ber"            : s_ber,
                "s_escalate"       : s_escalate,
                "s_urgency"        : s_urgency,
                "total"            : total,
                "notes"            : test["notes"],
            }

            results.append(record)
            path_scores[test["expected_repair_path"]].append(total)

            path_icon = {"tech_bar": "🏪", "newark": "🏭",
                         "engineer": "🔧", "replace": "📦"}.get(brief.repair_path, "?")
            path_match = "✓" if s_path else "✗"

            print(
                f"  Score: {total}/5 | "
                f"Path: {path_match}{path_icon} | "
                f"Coverage: {'✓' if s_coverage else '✗'} | "
                f"BER: {'✓' if s_ber else '✗'} | "
                f"Escalate: {'✓' if s_escalate else '✗'} | "
                f"Urgency: {'✓' if s_urgency else '✗'} | "
                f"Conf: {brief.confidence}"
            )

            if not s_path:
                print(f"  ⚠ Path mismatch: expected {test['expected_repair_path']}, "
                      f"got {brief.repair_path}")

        except Exception as e:
            print(f"  ERROR: {e}")
            results.append({
                "id": test["id"], "name": test["name"],
                "total": 0, "error": str(e),
            })

        time.sleep(1)

    # ─────────────────────────────────────────────
    # SUMMARY
    # ─────────────────────────────────────────────

    total_possible = len(TEST_SCENARIOS) * 5
    total_achieved = sum(r.get("total", 0) for r in results)
    overall_pct    = round(total_achieved / total_possible * 100, 1)

    print("\n" + "=" * 65)
    print("EVALUATION SUMMARY")
    print("=" * 65)
    print(f"Overall score: {total_achieved}/{total_possible} ({overall_pct}%)")

    # By repair path
    print("\nBy expected repair path:")
    for path, scores in path_scores.items():
        if scores:
            path_total = sum(scores)
            path_poss  = len(scores) * 5
            path_pct   = round(path_total / path_poss * 100, 1)
            icon       = {"tech_bar": "🏪", "newark": "🏭",
                          "engineer": "🔧", "replace": "📦"}.get(path, "?")
            bar        = "█" * int(path_pct / 5) + "░" * (20 - int(path_pct / 5))
            print(f"  {icon} {path:<12} {bar} {path_pct}% ({path_total}/{path_poss})")

    # By dimension
    print("\nBy scoring dimension:")
    dims = ["s_path", "s_coverage", "s_ber", "s_escalate", "s_urgency"]
    dim_names = ["Repair path", "Coverage type", "BER detection",
                 "Escalation", "Urgency level"]
    for dim, name in zip(dims, dim_names):
        dim_scores = [r.get(dim, 0) for r in results]
        dim_pct    = round(sum(dim_scores) / len(dim_scores) * 100, 1)
        print(f"  {name:<18} {dim_pct}% ({sum(dim_scores)}/{len(dim_scores)})")

    # Worst results
    worst = sorted(
        [r for r in results if "error" not in r],
        key=lambda x: x["total"]
    )[:5]
    print("\nWORST 5 RESULTS:")
    for w in worst:
        print(f"  {w['id']} — {w['name'][:50]} — score {w['total']}/5")
        if w["s_path"] == 0:
            print(f"    Path: expected {w['expected_path']}, got {w['actual_path']}")
        if w["s_coverage"] == 0:
            print(f"    Coverage: expected {w['expected_coverage']}, got {w['actual_coverage']}")

    # Confidence distribution
    confs = [r.get("confidence", "?") for r in results if "error" not in r]
    print(f"\nConfidence distribution:")
    for level in ["HIGH", "MEDIUM", "LOW"]:
        count = confs.count(level)
        print(f"  {level}: {count}/{len(confs)}")

    # Save results
    output_dir = Path("evaluation")
    output_dir.mkdir(exist_ok=True)

    results_path = output_dir / "eval_results.json"
    with open(results_path, "w") as f:
        json.dump({
            "metadata": {
                "timestamp"      : datetime.now().isoformat(),
                "total_scenarios": len(TEST_SCENARIOS),
                "overall_score"  : overall_pct,
                "total_achieved" : total_achieved,
                "total_possible" : total_possible,
            },
            "results": results,
        }, f, indent=2)

    print(f"\nResults saved to: {results_path}")
    print(f"\nEvaluation complete. Overall: {overall_pct}%")


if __name__ == "__main__":
    main()