import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_network_rules as net
import doda_territory_rules as terr
import doda_page_registry as registry
import test_territory_rules as base


class MissionProgressionContractTests(unittest.TestCase):
    setUp = base.TerritoryTests.setUp
    tearDown = base.TerritoryTests.tearDown
    make_root = base.TerritoryTests.make_root
    validate = base.TerritoryTests.validate
    test_valid_and_warnings = None
    test_exactly_one_starting = None
    test_player_only_agents = None
    test_starting_needs_hq = None
    test_population = None
    test_settings = None
    test_tiers = None
    test_maps = None
    test_export_not_runtime = None
    test_shipped_data = None

    def test_linear_cost(self):
        self.assertEqual(terr.ordinary_lead_cost(10, 2, 0), 10)
        self.assertEqual(terr.ordinary_lead_cost(10, 2, 3), 16)

    def test_unconfigured_cost_is_not_zero(self):
        self.assertIsNone(terr.ordinary_lead_cost(None, 2, 0))
        self.assertIsNone(terr.ordinary_lead_cost(10, None, 0))

    def test_invalid_cost_inputs(self):
        for values in [(0, 2, 0), (10, 0, 0), (10, 2, -1), (True, 2, 0)]:
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    terr.ordinary_lead_cost(*values)

    def test_editor_choices_include_new_settings(self):
        spec = registry.TABLE_METADATA["territory_settings"]
        choices = next(field.choices for field in spec.fields if field.name == "setting_id")
        self.assertTrue(set(terr.PROGRESSION_SETTING_UNITS).issubset(set(choices)))

    def test_draft_gate_stays_unconfigured(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        contract = data["missionProgression"]
        self.assertFalse(contract["ordinaryPricing"]["configured"])
        self.assertFalse(contract["finalGate"]["configured"])
        self.assertIn("REQUIRED_UPGRADE_REFERENCES",
                      contract["finalGate"]["missingConfiguration"])

    def test_active_pricing_can_be_configured(self):
        rows = base.setting_rows()
        base.edit(rows, "setting_id", "LEAD_BASE_COST", value="10", active="true")
        base.edit(rows, "setting_id", "LEAD_COST_INCREMENT", value="2", active="true")
        result, data = self.validate(settings=rows)
        self.assertTrue(result.valid, result.errors)
        self.assertTrue(data["missionProgression"]["ordinaryPricing"]["configured"])

    def test_zero_increment_rejected(self):
        rows = base.setting_rows()
        base.edit(rows, "setting_id", "LEAD_COST_INCREMENT", value="0")
        result, _ = self.validate(settings=rows)
        self.assertTrue(any("value must be at least 1" in error for error in result.errors))

    def test_capstone_and_final_gate_contract(self):
        rules = terr.RULES["missionProgression"]
        self.assertEqual(rules["finalGate"]["readinessMetricId"], "PREPAREDNESS")
        self.assertEqual(rules["finalGate"]["requirementsCombine"], "ALL")
        self.assertFalse(rules["capstone"]["expires"])
        self.assertFalse(rules["capstone"]["redeploymentRequiresRepurchase"])
        self.assertTrue(rules["capstone"]["retainsMissionState"])
        self.assertTrue(rules["capstone"]["unlockIsPermanent"])
        self.assertEqual(rules["capstone"]["completion"], "AUTHORED_OBJECTIVES")


if __name__ == "__main__":
    unittest.main()
