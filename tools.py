"""
Voltex Repair Triage Agent
tools.py — Agent Tool Definitions

Five tools the LangGraph agent can call:
  1. classify_fault       — identifies product type and fault component
  2. check_parts          — looks up parts availability and cost
  3. check_warranty       — determines VoltCare/warranty status
  4. estimate_repair_cost — calculates total repair cost
  5. make_triage_decision — final routing decision

Each tool is a plain Python function wrapped for LangGraph tool use.
"""

import json
import re
from typing import Optional
from langchain_core.tools import tool
from knowledge_base import (
    FAULT_CATEGORIES,
    PARTS_CATALOGUE,
    REPAIR_COMPLEXITY,
    LABOUR_RATES,
    BER_THRESHOLD,
    REPAIR_PATHS,
    SKILL_DESCRIPTIONS,
)


# ─────────────────────────────────────────────
# TOOL 1 — FAULT CLASSIFIER
# ─────────────────────────────────────────────

@tool
def classify_fault(fault_description: str, product_type: str) -> str:
    """
    Classifies a customer fault description into a product category and
    fault component. Returns structured classification data.

    Args:
        fault_description: What the customer described as the fault
        product_type: The product category (laptop, phone, tv, washing_machine,
                      fridge_freezer, dishwasher)

    Returns:
        JSON string with classification results
    """
    fault_lower = fault_description.lower()
    product_lower = product_type.lower().replace(" ", "_").replace("-", "_")

    # Normalise product type
    product_map = {
        "laptop"        : "laptop",
        "notebook"      : "laptop",
        "computer"      : "laptop",
        "phone"         : "phone",
        "smartphone"    : "phone",
        "mobile"        : "phone",
        "iphone"        : "phone",
        "samsung"       : "phone",
        "tv"            : "tv",
        "television"    : "tv",
        "telly"         : "tv",
        "washing_machine": "washing_machine",
        "washer"        : "washing_machine",
        "fridge"        : "fridge_freezer",
        "freezer"       : "fridge_freezer",
        "fridge_freezer": "fridge_freezer",
        "dishwasher"    : "dishwasher",
    }

    normalised_product = product_map.get(product_lower, product_lower)

    if normalised_product not in FAULT_CATEGORIES:
        return json.dumps({
            "success"          : False,
            "error"            : f"Unknown product type: {product_type}",
            "supported_products": list(FAULT_CATEGORIES.keys()),
        })

    # Match fault to component
    best_component  = None
    best_match_count = 0
    matched_symptoms = []

    for component, symptoms in FAULT_CATEGORIES[normalised_product].items():
        match_count = sum(1 for symptom in symptoms if symptom.lower() in fault_lower)
        symptom_matches = [s for s in symptoms if s.lower() in fault_lower]

        if match_count > best_match_count:
            best_match_count = match_count
            best_component   = component
            matched_symptoms = symptom_matches

    # Detect liquid damage as override
    liquid_keywords = ["spill", "liquid", "water", "wet", "flood", "coffee", "drink"]
    is_liquid_damage = any(kw in fault_lower for kw in liquid_keywords)

    if is_liquid_damage and "liquid" in FAULT_CATEGORIES.get(normalised_product, {}):
        best_component = "liquid"

    # Get complexity info
    complexity_info = {}
    if best_component and normalised_product in REPAIR_COMPLEXITY:
        complexity_info = REPAIR_COMPLEXITY[normalised_product].get(best_component, {})

    result = {
        "success"         : True,
        "product_type"    : normalised_product,
        "fault_component" : best_component or "unknown",
        "matched_symptoms": matched_symptoms,
        "is_liquid_damage": is_liquid_damage,
        "complexity"      : complexity_info.get("complexity", "unknown"),
        "skill_required"  : complexity_info.get("skill", "unknown"),
        "labour_hours"    : complexity_info.get("labour_hours", 0),
        "confidence"      : "HIGH" if best_match_count >= 2 else "MEDIUM" if best_match_count == 1 else "LOW",
    }

    return json.dumps(result)


# ─────────────────────────────────────────────
# TOOL 2 — PARTS CHECKER
# ─────────────────────────────────────────────

@tool
def check_parts(product_type: str, fault_component: str) -> str:
    """
    Looks up available parts for a given product type and fault component.
    Returns parts availability, cost, and lead time.

    Args:
        product_type: Normalised product type (laptop, phone, tv, etc.)
        fault_component: The component that needs repair (display, battery, etc.)

    Returns:
        JSON string with parts information
    """
    matching_parts = []

    for part_id, part in PARTS_CATALOGUE.items():
        if (part["category"] == product_type or
                product_type in part.get("fits", [])):
            if part["component"] == fault_component:
                matching_parts.append({
                    "part_id"     : part_id,
                    "name"        : part["name"],
                    "cost"        : part["cost"],
                    "availability": part["availability"],
                    "lead_days"   : part["lead_days"],
                })

    if not matching_parts:
        # Check if we have parts for a related component
        return json.dumps({
            "success"         : True,
            "parts_found"     : False,
            "product_type"    : product_type,
            "fault_component" : fault_component,
            "parts"           : [],
            "recommendation"  : "No standard parts found. May require specialist assessment.",
            "can_repair"      : False,
        })

    # Sort by availability then cost
    availability_order = {"in_stock": 0, "low_stock": 1, "out_of_stock": 2}
    matching_parts.sort(key=lambda x: (availability_order.get(x["availability"], 3), x["cost"]))

    best_part    = matching_parts[0]
    in_stock     = any(p["availability"] == "in_stock" for p in matching_parts)
    min_lead_days = min(p["lead_days"] for p in matching_parts)

    return json.dumps({
        "success"          : True,
        "parts_found"      : True,
        "product_type"     : product_type,
        "fault_component"  : fault_component,
        "parts"            : matching_parts,
        "best_part"        : best_part,
        "in_stock"         : in_stock,
        "min_lead_days"    : min_lead_days,
        "can_repair"       : True,
        "total_parts_found": len(matching_parts),
    })


# ─────────────────────────────────────────────
# TOOL 3 — WARRANTY CHECKER
# ─────────────────────────────────────────────

@tool
def check_warranty(
    product_age_months: int,
    has_voltcare: bool,
    voltcare_tier: Optional[str] = None,
    is_accidental_damage: bool = False,
) -> str:
    """
    Determines warranty and VoltCare coverage status for a repair.

    Args:
        product_age_months: How old the product is in months
        has_voltcare: Whether the customer has a VoltCare plan
        voltcare_tier: VoltCare tier if applicable (essential, plus, complete)
        is_accidental_damage: Whether the fault is accidental damage

    Returns:
        JSON string with coverage determination
    """
    coverage = {
        "manufacturer_warranty": product_age_months <= 12,
        "consumer_rights_act"  : product_age_months <= 72,  # 6 years
        "voltcare_active"      : has_voltcare,
        "voltcare_tier"        : voltcare_tier,
        "is_accidental_damage" : is_accidental_damage,
        "customer_pays"        : True,
        "coverage_type"        : None,
        "excess_applies"       : False,
        "excess_amount"        : 0,
        "notes"                : [],
    }

    # Determine coverage
    if product_age_months <= 12:
        coverage["coverage_type"] = "manufacturer_warranty"
        coverage["customer_pays"] = False
        coverage["notes"].append(
            "Product is within 12-month manufacturer warranty — repair at no charge to customer"
        )

    elif has_voltcare and voltcare_tier:
        tier = voltcare_tier.lower()

        if is_accidental_damage:
            if tier == "essential":
                coverage["coverage_type"] = "not_covered"
                coverage["customer_pays"] = True
                coverage["notes"].append(
                    "VoltCare Essential does not cover accidental damage — customer pays"
                )
            elif tier == "plus":
                coverage["coverage_type"] = "voltcare_plus_ad"
                coverage["customer_pays"] = False
                coverage["excess_applies"] = True
                coverage["excess_amount"]  = 49  # standard excess
                coverage["notes"].append(
                    "VoltCare Plus covers accidental damage — excess applies before repair proceeds"
                )
            elif tier == "complete":
                coverage["coverage_type"] = "voltcare_complete"
                coverage["customer_pays"] = False
                coverage["excess_applies"] = False
                coverage["notes"].append(
                    "VoltCare Complete covers accidental damage — no excess, 48-hour SLA applies"
                )
        else:
            # Breakdown / mechanical fault
            coverage["coverage_type"] = f"voltcare_{tier}"
            coverage["customer_pays"] = False
            coverage["notes"].append(
                f"VoltCare {tier.title()} covers mechanical breakdown — repair at no charge"
            )
            if tier == "complete":
                coverage["notes"].append("48-hour repair or replace SLA applies for Complete tier")

    elif product_age_months <= 72:
        coverage["coverage_type"] = "consumer_rights_act"
        coverage["customer_pays"] = False
        coverage["notes"].append(
            f"Product is {product_age_months} months old — statutory rights apply under Consumer Rights Act 2015"
        )
        if product_age_months > 6:
            coverage["notes"].append(
                "After 6 months, customer may need to demonstrate fault was present at purchase — "
                "engineer assessment will establish this"
            )
    else:
        coverage["coverage_type"] = "no_coverage"
        coverage["customer_pays"] = True
        coverage["notes"].append(
            "No active warranty or VoltCare — customer will be quoted for paid repair"
        )

    return json.dumps(coverage)


# ─────────────────────────────────────────────
# TOOL 4 — REPAIR COST ESTIMATOR
# ─────────────────────────────────────────────

@tool
def estimate_repair_cost(
    product_type   : str,
    fault_component: str,
    part_cost      : float,
    product_value  : float,
) -> str:
    """
    Calculates total repair cost and determines if BER threshold is exceeded.

    Args:
        product_type: Normalised product type
        fault_component: Component being repaired
        part_cost: Cost of the required part(s)
        product_value: Current market value of the product

    Returns:
        JSON string with cost breakdown and BER determination
    """
    complexity_info = {}
    if product_type in REPAIR_COMPLEXITY:
        complexity_info = REPAIR_COMPLEXITY[product_type].get(fault_component, {})

    skill        = complexity_info.get("skill", "newark")
    labour_hours = complexity_info.get("labour_hours", 1.5)
    labour_rate  = LABOUR_RATES.get(skill, 45.0)
    labour_cost  = labour_hours * labour_rate
    total_cost   = part_cost + labour_cost
    ber_ratio    = total_cost / product_value if product_value > 0 else 1.0
    is_ber       = ber_ratio >= BER_THRESHOLD

    result = {
        "part_cost"          : round(part_cost, 2),
        "labour_hours"       : labour_hours,
        "labour_rate_per_hour": labour_rate,
        "labour_cost"        : round(labour_cost, 2),
        "total_repair_cost"  : round(total_cost, 2),
        "product_value"      : round(product_value, 2),
        "ber_ratio"          : round(ber_ratio, 3),
        "ber_threshold"      : BER_THRESHOLD,
        "is_beyond_economical_repair": is_ber,
        "repair_path"        : skill,
        "repair_path_description": REPAIR_PATHS.get(skill, "Unknown"),
        "skill_description"  : SKILL_DESCRIPTIONS.get(skill, ""),
        "recommendation"     : (
            "REPLACE — repair cost exceeds 65% of product value"
            if is_ber else
            f"REPAIR — economical at £{total_cost:.2f} vs product value £{product_value:.2f}"
        ),
    }

    return json.dumps(result)


# ─────────────────────────────────────────────
# TOOL 5 — TRIAGE DECISION MAKER
# ─────────────────────────────────────────────

@tool
def make_triage_decision(
    product_type          : str,
    fault_component       : str,
    fault_description     : str,
    skill_required        : str,
    is_ber                : bool,
    customer_pays         : bool,
    excess_applies        : bool,
    excess_amount         : float,
    coverage_type         : str,
    parts_available       : bool,
    parts_lead_days       : int,
    total_repair_cost     : float,
    voltcare_tier         : Optional[str] = None,
    is_liquid_damage      : bool = False,
) -> str:
    """
    Makes the final triage routing decision and generates the repair brief.

    Args:
        All the information gathered from previous tool calls.

    Returns:
        JSON string with the final RepairBrief data.
    """
    # Determine repair path
    if is_ber:
        repair_path    = "replace"
        path_desc      = REPAIR_PATHS["replace"]
        escalate       = True
        escalate_reason = "Product is beyond economical repair — replacement process required"
        urgency        = "HIGH"

    elif not parts_available:
        repair_path    = skill_required
        path_desc      = REPAIR_PATHS.get(skill_required, "Newark Repair Centre")
        escalate       = True
        escalate_reason = f"Parts not in stock — lead time {parts_lead_days} days. Check with customer re: urgency"
        urgency        = "MEDIUM"

    elif skill_required == "tech_bar":
        repair_path    = "tech_bar"
        path_desc      = REPAIR_PATHS["tech_bar"]
        escalate       = False
        escalate_reason = ""
        urgency        = "LOW"

    elif skill_required == "engineer":
        repair_path    = "engineer"
        path_desc      = REPAIR_PATHS["engineer"]
        escalate       = False
        escalate_reason = ""
        urgency        = "MEDIUM"

    else:
        repair_path    = "newark"
        path_desc      = REPAIR_PATHS["newark"]
        escalate       = is_liquid_damage  # liquid damage always escalates
        escalate_reason = "Liquid damage — extent of corrosion requires specialist assessment" if is_liquid_damage else ""
        urgency        = "HIGH" if is_liquid_damage else "MEDIUM"

    # Build technician brief
    technician_notes = []

    if is_liquid_damage:
        technician_notes.append(
            "LIQUID DAMAGE — do not power on the device before inspection. "
            "Check for corrosion on main board before quoting repair."
        )

    if coverage_type and "voltcare" in coverage_type.lower():
        technician_notes.append(f"VoltCare {voltcare_tier or ''} claim — no charge to customer")
        if excess_applies:
            technician_notes.append(f"Excess of £{excess_amount:.0f} must be collected before repair begins")

    if coverage_type == "manufacturer_warranty":
        technician_notes.append("Manufacturer warranty repair — process via warranty portal")

    if coverage_type == "consumer_rights_act":
        technician_notes.append(
            "Consumer Rights Act repair — document fault clearly. "
            "If fault not obvious at inspection, customer may need to demonstrate pre-existing condition."
        )

    if not parts_available and parts_lead_days > 0:
        technician_notes.append(
            f"Parts on order — estimated {parts_lead_days} day lead time. "
            "Contact customer before proceeding."
        )

    result = {
        "repair_path"         : repair_path,
        "repair_path_description": path_desc,
        "coverage_type"       : coverage_type,
        "customer_pays"       : customer_pays,
        "excess_applies"      : excess_applies,
        "excess_amount"       : excess_amount,
        "estimated_cost_to_customer": total_repair_cost if customer_pays else 0,
        "is_ber"              : is_ber,
        "urgency"             : urgency,
        "escalate"            : escalate,
        "escalation_reason"   : escalate_reason,
        "technician_notes"    : technician_notes,
        "product_type"        : product_type,
        "fault_component"     : fault_component,
        "fault_description"   : fault_description,
    }

    return json.dumps(result)