import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_page_registry as registry
import doda_territory_rules as terr
import test_territory_rules as base


class MissionProgressionContractTests(unittest.TestCase):
    setUp = base.TerritoryTests.setUp
    tearDown = base.TerritoryTests.tearDown
    make_root = base.TerritoryTests.make_root
    validate = base.TerritoryTests.validate

    def test_compound_cost(self):
        costs = [terr.ordinary_lead_cost(100, 100000, n) for n in range(5)]
        self.assertEqual(costs, [100, 110, 121, 133, 146])

    def test_unconfigured_cost_is_not_zero(self):
        self.assertIsNone(terr.ordinary_lead_cost(None, 100000, 0))
        self.assertIsNone(terr.ordinary_lead_cost(100, None, 0))

    def test_invalid_cost_inputs(self):
        for values in [(0, 100000, 0), (100, 0, 0), (100, 100000, -1),
                       (True, 100000, 0), (100, 1000001, 0)]:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    terr.ordinary_lead_cost(*values)

    def test_editor_choices_include_new_settings(self):
        spec = registry.TABLE_METADATA["territory_settings"]
        choices = next(field.choices for field in spec.fields if field.name == "setting_id")
        self.assertTrue(set(terr.PROGRESSION_SETTING_UNITS).issubset(set(choices)))
        self.assertIn("LEAD_COST_GROWTH_PERCENT", choices)

    def test_draft_gate_stays_unconfigured(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        contract = data["missionProgression"]
        self.assertFalse(contract["ordinaryPricing"]["configured"])
        self.assertFalse(contract["finalGate"]["configured"])
        self.assertIn("REQUIRED_UPGRADE_REFERENCES", contract["finalGate"]["missingConfiguration"])

    def test_active_pricing_can_be_configured(self):
        rows = base.setting_rows()
        base.edit(rows, "setting_id", "LEAD_BASE_COST", value="100", active="true")
        base.edit(rows, "setting_id", "LEAD_COST_GROWTH_PERCENT", value="10", active="true")
        result, data = self.validate(settings=rows)
        self.assertTrue(result.valid, result.errors)
        pricing = data["missionProgression"]["ordinaryPricing"]
        self.assertTrue(pricing["configured"])
        self.assertEqual(pricing["baseCost"], 100)
        self.assertEqual(pricing["growthPercentScaled"], 100000)

    def test_zero_growth_rejected(self):
        rows = base.setting_rows()
        base.edit(rows, "setting_id", "LEAD_COST_GROWTH_PERCENT", value="0")
        result, _ = self.validate(settings=rows)
        self.assertTrue(any("above 0" in error for error in result.errors))

    def test_capstone_and_final_gate_contract(self):
        rules = terr.RULES["missionProgression"]
        self.assertEqual(rules["finalGate"]["readinessMetricId"], "PREPAREDNESS")
        self.assertEqual(rules["finalGate"]["requirementsCombine"], "ALL")
        self.assertFalse(rules["capstone"]["expires"])
        self.assertFalse(rules["capstone"]["redeploymentRequiresRepurchase"])
        self.assertTrue(rules["capstone"]["retainsMissionState"])
        self.assertTrue(rules["capstone"]["unlockIsPermanent"])
        self.assertEqual(rules["capstone"]["completion"], "AUTHORED_OBJECTIVES")

    def test_pricing_rule_is_compound(self):
        pricing = terr.RULES["missionProgression"]["ordinaryLeadPricing"]
        self.assertEqual(pricing["model"], "COMPOUND_PERCENT")


if __name__ == "__main__":
    unittest.main()
