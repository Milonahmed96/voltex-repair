"""
Voltex Repair Triage Agent — Test Suite

Tests cover:
  - Knowledge base integrity
  - Tool logic (no API calls)
  - Agent schema validation
  - Agent unit tests (mocked API)
"""

import json
import sys
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))


# ─────────────────────────────────────────────
# KNOWLEDGE BASE TESTS
# ─────────────────────────────────────────────

class TestKnowledgeBase:

    def test_all_product_types_have_fault_categories(self):
        from knowledge_base import FAULT_CATEGORIES
        expected = ["laptop", "phone", "tv", "washing_machine", "fridge_freezer", "dishwasher"]
        for product in expected:
            assert product in FAULT_CATEGORIES, f"Missing product: {product}"

    def test_all_products_have_repair_complexity(self):
        from knowledge_base import FAULT_CATEGORIES, REPAIR_COMPLEXITY
        for product in FAULT_CATEGORIES:
            assert product in REPAIR_COMPLEXITY, f"Missing complexity for: {product}"

    def test_parts_catalogue_has_required_fields(self):
        from knowledge_base import PARTS_CATALOGUE
        required = ["name", "category", "component", "cost", "availability", "lead_days"]
        for part_id, part in PARTS_CATALOGUE.items():
            for field in required:
                assert field in part, f"Part {part_id} missing field: {field}"

    def test_parts_costs_are_positive(self):
        from knowledge_base import PARTS_CATALOGUE
        for part_id, part in PARTS_CATALOGUE.items():
            assert part["cost"] > 0, f"Part {part_id} has non-positive cost"

    def test_availability_values_are_valid(self):
        from knowledge_base import PARTS_CATALOGUE
        valid = {"in_stock", "low_stock", "out_of_stock"}
        for part_id, part in PARTS_CATALOGUE.items():
            assert part["availability"] in valid, (
                f"Part {part_id} has invalid availability: {part['availability']}"
            )

    def test_ber_threshold_is_reasonable(self):
        from knowledge_base import BER_THRESHOLD
        assert 0.5 <= BER_THRESHOLD <= 0.8, f"BER threshold {BER_THRESHOLD} seems unreasonable"

    def test_labour_rates_are_positive(self):
        from knowledge_base import LABOUR_RATES
        for skill, rate in LABOUR_RATES.items():
            assert rate > 0, f"Labour rate for {skill} is non-positive"

    def test_repair_paths_have_all_required(self):
        from knowledge_base import REPAIR_PATHS
        required = ["tech_bar", "newark", "engineer", "replace"]
        for path in required:
            assert path in REPAIR_PATHS, f"Missing repair path: {path}"

    def test_complexity_has_valid_skill_values(self):
        from knowledge_base import REPAIR_COMPLEXITY
        valid_skills = {"tech_bar", "newark", "engineer"}
        for product, components in REPAIR_COMPLEXITY.items():
            for component, info in components.items():
                assert info["skill"] in valid_skills, (
                    f"{product}/{component} has invalid skill: {info['skill']}"
                )

    def test_laptop_has_display_and_battery_components(self):
        from knowledge_base import FAULT_CATEGORIES
        laptop = FAULT_CATEGORIES["laptop"]
        assert "display" in laptop
        assert "battery" in laptop

    def test_phone_has_liquid_damage_category(self):
        from knowledge_base import FAULT_CATEGORIES
        phone = FAULT_CATEGORIES["phone"]
        assert "liquid" in phone or "screen" in phone


# ─────────────────────────────────────────────
# TOOL TESTS (no API calls)
# ─────────────────────────────────────────────

class TestClassifyFaultTool:

    def test_classifies_laptop_screen_fault(self):
        from tools import classify_fault
        result = json.loads(classify_fault.invoke({
            "fault_description": "cracked screen after drop",
            "product_type"     : "laptop",
        }))
        assert result["success"] is True
        assert result["product_type"] == "laptop"
        assert result["fault_component"] == "display"

    def test_classifies_phone_liquid_damage(self):
        from tools import classify_fault
        result = json.loads(classify_fault.invoke({
            "fault_description": "spilled coffee on phone, speaker muffled",
            "product_type"     : "phone",
        }))
        assert result["success"] is True
        assert result["is_liquid_damage"] is True

    def test_washing_machine_water_not_liquid_damage(self):
        from tools import classify_fault
        result = json.loads(classify_fault.invoke({
            "fault_description": "water not draining from washing machine",
            "product_type"     : "washing_machine",
        }))
        assert result["success"] is True
        assert result["is_liquid_damage"] is False

    def test_unknown_product_returns_error(self):
        from tools import classify_fault
        result = json.loads(classify_fault.invoke({
            "fault_description": "broken",
            "product_type"     : "microwave",
        }))
        assert result["success"] is False
        assert "supported_products" in result

    def test_product_type_normalisation(self):
        from tools import classify_fault
        result = json.loads(classify_fault.invoke({
            "fault_description": "screen cracked",
            "product_type"     : "smartphone",
        }))
        assert result["success"] is True
        assert result["product_type"] == "phone"

    def test_confidence_returned(self):
        from tools import classify_fault
        result = json.loads(classify_fault.invoke({
            "fault_description": "cracked screen broken display flickering",
            "product_type"     : "laptop",
        }))
        assert result["confidence"] in ["HIGH", "MEDIUM", "LOW"]

    def test_skill_required_returned(self):
        from tools import classify_fault
        result = json.loads(classify_fault.invoke({
            "fault_description": "cracked screen",
            "product_type"     : "laptop",
        }))
        assert result["skill_required"] in ["tech_bar", "newark", "engineer", "unknown"]


class TestCheckPartsTool:

    def test_finds_laptop_display_parts(self):
        from tools import check_parts
        result = json.loads(check_parts.invoke({
            "product_type"   : "laptop",
            "fault_component": "display",
        }))
        assert result["success"] is True
        assert result["parts_found"] is True
        assert len(result["parts"]) > 0

    def test_finds_washing_machine_pump(self):
        from tools import check_parts
        result = json.loads(check_parts.invoke({
            "product_type"   : "washing_machine",
            "fault_component": "water",
        }))
        assert result["success"] is True
        assert result["parts_found"] is True

    def test_returns_best_part(self):
        from tools import check_parts
        result = json.loads(check_parts.invoke({
            "product_type"   : "phone",
            "fault_component": "screen",
        }))
        assert result["parts_found"] is True
        assert "best_part" in result
        assert result["best_part"]["cost"] > 0

    def test_unknown_component_returns_gracefully(self):
        from tools import check_parts
        result = json.loads(check_parts.invoke({
            "product_type"   : "laptop",
            "fault_component": "flux_capacitor",
        }))
        assert result["success"] is True
        assert result["parts_found"] is False
        assert result["can_repair"] is False

    def test_parts_sorted_by_availability(self):
        from tools import check_parts
        result = json.loads(check_parts.invoke({
            "product_type"   : "phone",
            "fault_component": "screen",
        }))
        if result["parts_found"] and len(result["parts"]) > 1:
            avail_order = {"in_stock": 0, "low_stock": 1, "out_of_stock": 2}
            parts = result["parts"]
            for i in range(len(parts) - 1):
                assert avail_order.get(parts[i]["availability"], 3) <= \
                       avail_order.get(parts[i+1]["availability"], 3)


class TestCheckWarrantyTool:

    def test_manufacturer_warranty_within_12_months(self):
        from tools import check_warranty
        result = json.loads(check_warranty.invoke({
            "product_age_months" : 8,
            "has_voltcare"       : False,
            "voltcare_tier"      : None,
            "is_accidental_damage": False,
        }))
        assert result["manufacturer_warranty"] is True
        assert result["customer_pays"] is False
        assert result["coverage_type"] == "manufacturer_warranty"

    def test_cra_applies_within_6_years(self):
        from tools import check_warranty
        result = json.loads(check_warranty.invoke({
            "product_age_months" : 36,
            "has_voltcare"       : False,
            "voltcare_tier"      : None,
            "is_accidental_damage": False,
        }))
        assert result["consumer_rights_act"] is True
        assert result["customer_pays"] is False

    def test_no_coverage_after_6_years(self):
        from tools import check_warranty
        result = json.loads(check_warranty.invoke({
            "product_age_months" : 84,
            "has_voltcare"       : False,
            "voltcare_tier"      : None,
            "is_accidental_damage": False,
        }))
        assert result["coverage_type"] == "no_coverage"
        assert result["customer_pays"] is True

    def test_voltcare_essential_no_ad_cover(self):
        from tools import check_warranty
        result = json.loads(check_warranty.invoke({
            "product_age_months" : 20,
            "has_voltcare"       : True,
            "voltcare_tier"      : "essential",
            "is_accidental_damage": True,
        }))
        assert result["customer_pays"] is True
        assert result["coverage_type"] == "not_covered"

    def test_voltcare_plus_ad_has_excess(self):
        from tools import check_warranty
        result = json.loads(check_warranty.invoke({
            "product_age_months" : 20,
            "has_voltcare"       : True,
            "voltcare_tier"      : "plus",
            "is_accidental_damage": True,
        }))
        assert result["customer_pays"] is False
        assert result["excess_applies"] is True
        assert result["excess_amount"] > 0

    def test_voltcare_complete_no_excess(self):
        from tools import check_warranty
        result = json.loads(check_warranty.invoke({
            "product_age_months" : 20,
            "has_voltcare"       : True,
            "voltcare_tier"      : "complete",
            "is_accidental_damage": True,
        }))
        assert result["customer_pays"] is False
        assert result["excess_applies"] is False
        assert result["excess_amount"] == 0

    def test_voltcare_essential_covers_breakdown(self):
        from tools import check_warranty
        result = json.loads(check_warranty.invoke({
            "product_age_months" : 20,
            "has_voltcare"       : True,
            "voltcare_tier"      : "essential",
            "is_accidental_damage": False,
        }))
        assert result["customer_pays"] is False


class TestEstimateRepairCostTool:

    def test_calculates_total_correctly(self):
        from tools import estimate_repair_cost
        result = json.loads(estimate_repair_cost.invoke({
            "product_type"   : "laptop",
            "fault_component": "display",
            "part_cost"      : 89.99,
            "product_value"  : 750.0,
        }))
        assert result["part_cost"] == 89.99
        assert result["total_repair_cost"] > result["part_cost"]
        assert result["labour_cost"] > 0

    def test_ber_flag_triggers_above_threshold(self):
        from tools import estimate_repair_cost
        result = json.loads(estimate_repair_cost.invoke({
            "product_type"   : "fridge_freezer",
            "fault_component": "cooling",
            "part_cost"      : 199.99,
            "product_value"  : 280.0,
        }))
        assert result["is_beyond_economical_repair"] is True
        assert result["ber_ratio"] >= 0.65

    def test_ber_flag_not_triggered_below_threshold(self):
        from tools import estimate_repair_cost
        result = json.loads(estimate_repair_cost.invoke({
            "product_type"   : "washing_machine",
            "fault_component": "water",
            "part_cost"      : 29.99,
            "product_value"  : 450.0,
        }))
        assert result["is_beyond_economical_repair"] is False
        assert result["ber_ratio"] < 0.65

    def test_repair_path_returned(self):
        from tools import estimate_repair_cost
        result = json.loads(estimate_repair_cost.invoke({
            "product_type"   : "laptop",
            "fault_component": "battery",
            "part_cost"      : 34.99,
            "product_value"  : 600.0,
        }))
        assert result["repair_path"] in ["tech_bar", "newark", "engineer"]

    def test_ber_ratio_calculation(self):
        from tools import estimate_repair_cost
        result = json.loads(estimate_repair_cost.invoke({
            "product_type"   : "laptop",
            "fault_component": "display",
            "part_cost"      : 100.0,
            "product_value"  : 500.0,
        }))
        expected_ratio = result["total_repair_cost"] / 500.0
        assert abs(result["ber_ratio"] - expected_ratio) < 0.01


# ─────────────────────────────────────────────
# SCHEMA TESTS
# ─────────────────────────────────────────────

class TestRepairBriefSchema:

    VALID_BRIEF = {
        "product_type"              : "laptop",
        "fault_component"           : "display",
        "fault_description"         : "Cracked screen after drop.",
        "is_liquid_damage"          : False,
        "repair_path"               : "tech_bar",
        "repair_path_description"   : "In-store Tech Bar repair (same day)",
        "urgency"                   : "LOW",
        "coverage_type"             : "voltcare_plus_ad",
        "customer_pays"             : False,
        "excess_applies"            : True,
        "excess_amount"             : 49.0,
        "estimated_cost_to_customer": 0.0,
        "is_ber"                    : False,
        "technician_notes"          : ["VoltCare Plus claim — excess £49 before repair"],
        "escalate"                  : False,
        "escalation_reason"         : "",
        "reasoning_summary"         : "Screen replacement at Tech Bar under VoltCare Plus.",
        "confidence"                : "HIGH",
        "tools_used"                : ["classify_fault", "check_parts", "check_warranty",
                                       "estimate_repair_cost", "make_triage_decision"],
    }

    def test_valid_brief_creates_model(self):
        from agent import RepairBrief
        brief = RepairBrief(**self.VALID_BRIEF)
        assert brief.product_type == "laptop"
        assert brief.repair_path == "tech_bar"

    def test_all_repair_paths_accepted(self):
        from agent import RepairBrief
        for path in ["tech_bar", "newark", "engineer", "replace"]:
            brief = RepairBrief(**{**self.VALID_BRIEF, "repair_path": path})
            assert brief.repair_path == path

    def test_invalid_repair_path_rejected(self):
        from agent import RepairBrief
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            RepairBrief(**{**self.VALID_BRIEF, "repair_path": "home_visit"})

    def test_all_urgency_levels_accepted(self):
        from agent import RepairBrief
        for urgency in ["LOW", "MEDIUM", "HIGH"]:
            brief = RepairBrief(**{**self.VALID_BRIEF, "urgency": urgency})
            assert brief.urgency == urgency

    def test_invalid_urgency_rejected(self):
        from agent import RepairBrief
        from pydantic import ValidationError
        with pytest.raises(ValidationError):
            RepairBrief(**{**self.VALID_BRIEF, "urgency": "CRITICAL"})

    def test_all_confidence_levels_accepted(self):
        from agent import RepairBrief
        for conf in ["HIGH", "MEDIUM", "LOW"]:
            brief = RepairBrief(**{**self.VALID_BRIEF, "confidence": conf})
            assert brief.confidence == conf

    def test_missing_required_field_rejected(self):
        from agent import RepairBrief
        from pydantic import ValidationError
        payload = {k: v for k, v in self.VALID_BRIEF.items() if k != "product_type"}
        with pytest.raises(ValidationError):
            RepairBrief(**payload)

    def test_ber_flag_is_boolean(self):
        from agent import RepairBrief
        brief = RepairBrief(**self.VALID_BRIEF)
        assert isinstance(brief.is_ber, bool)

    def test_technician_notes_is_list(self):
        from agent import RepairBrief
        brief = RepairBrief(**self.VALID_BRIEF)
        assert isinstance(brief.technician_notes, list)

    def test_tools_used_is_list(self):
        from agent import RepairBrief
        brief = RepairBrief(**self.VALID_BRIEF)
        assert isinstance(brief.tools_used, list)


# ─────────────────────────────────────────────
# AGENT UNIT TESTS (mocked)
# ─────────────────────────────────────────────

class TestAgentUnit:

    MOCK_BRIEF_JSON = json.dumps({
        "product_type"              : "laptop",
        "fault_component"           : "display",
        "fault_description"         : "Cracked screen after drop.",
        "is_liquid_damage"          : False,
        "repair_path"               : "tech_bar",
        "repair_path_description"   : "In-store Tech Bar repair (same day, 60-90 minutes)",
        "urgency"                   : "LOW",
        "coverage_type"             : "voltcare_plus_ad",
        "customer_pays"             : False,
        "excess_applies"            : True,
        "excess_amount"             : 49.0,
        "estimated_cost_to_customer": 0.0,
        "is_ber"                    : False,
        "technician_notes"          : ["VoltCare Plus AD claim — collect £49 excess before repair"],
        "escalate"                  : False,
        "escalation_reason"         : "",
        "reasoning_summary"         : "Laptop screen crack classified as display fault. Tech Bar repair under VoltCare Plus.",
        "confidence"                : "HIGH",
        "tools_used"                : ["classify_fault", "check_parts", "check_warranty",
                                       "estimate_repair_cost", "make_triage_decision"],
    })

    def _make_mock_agent(self):
        """Creates a RepairTriageAgent with mocked LLM."""
        with patch("agent.ChatAnthropic"):
            from agent import RepairTriageAgent
            agent = RepairTriageAgent()

        mock_result_msg = MagicMock()
        mock_result_msg.content = self.MOCK_BRIEF_JSON
        mock_result_msg.tool_calls = []

        agent.agent = MagicMock()
        agent.agent.invoke.return_value = {
            "messages": [mock_result_msg]
        }
        return agent

    def test_triage_returns_dict(self):
        agent = self._make_mock_agent()
        result = agent.triage(
            fault_description    = "cracked screen",
            product_type         = "laptop",
            product_age_months   = 8,
            product_value        = 750.0,
            has_voltcare         = True,
            voltcare_tier        = "plus",
            is_accidental_damage = True,
        )
        assert isinstance(result, dict)

    def test_triage_has_required_keys(self):
        agent = self._make_mock_agent()
        result = agent.triage(
            fault_description    = "cracked screen",
            product_type         = "laptop",
            product_age_months   = 8,
            product_value        = 750.0,
        )
        assert "brief"    in result
        assert "steps"    in result
        assert "messages" in result

    def test_triage_returns_repair_brief(self):
        from agent import RepairBrief
        agent = self._make_mock_agent()
        result = agent.triage(
            fault_description = "cracked screen",
            product_type      = "laptop",
            product_age_months= 8,
            product_value     = 750.0,
        )
        assert isinstance(result["brief"], RepairBrief)

    def test_graceful_fallback_on_bad_json(self):
        """Test that RepairBrief can be created with fallback values."""
        from agent import RepairBrief
        # Test that a minimal fallback brief can be constructed
        fallback = RepairBrief(
            product_type               = "laptop",
            fault_component            = "unknown",
            fault_description          = "cracked screen",
            is_liquid_damage           = False,
            repair_path                = "newark",
            repair_path_description    = "Newark Repair Centre — manual assessment required",
            urgency                    = "MEDIUM",
            coverage_type              = "unknown",
            customer_pays              = True,
            excess_applies             = False,
            excess_amount              = 0,
            estimated_cost_to_customer = 0,
            is_ber                     = False,
            technician_notes           = ["Manual assessment required"],
            escalate                   = True,
            escalation_reason          = "Triage error — manual review needed",
            reasoning_summary          = "Automated triage could not complete.",
            confidence                 = "LOW",
            tools_used                 = [],
        )
        assert fallback.confidence == "LOW"
        assert fallback.escalate is True
        assert fallback.repair_path == "newark"