import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_congressional_support_rules as cs
import doda_network_rules as net
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)
SRC = ROOT / "data_authoring/source"


def rows(name):
    with (SRC / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


LEVELS = [
    {"levelId": "L1", "sortOrder": 10, "grantTerritories": 2, "grantFunding": 100},
    {"levelId": "L2", "sortOrder": 20, "grantTerritories": 2, "grantFunding": 200},
    {"levelId": "L3", "sortOrder": 30, "grantTerritories": 3, "grantFunding": 300},
]


class BudgetAndSiteNameTests(unittest.TestCase):
    def test_site_is_renamed_everywhere(self):
        territory = next(r for r in rows("territories.csv") if r["territory_id"] == "TERR_SRS_NUCLEAR_FACILITY")
        self.assertIn("Serena River Site", territory["display_name"])
        self.assertEqual(territory["locality"], "Serena River")
        self.assertEqual(territory["hq_name"], "Serena River DoDA Office")
        for path in sorted(SRC.glob("*.csv")):
            with self.subTest(file=path.name):
                self.assertNotIn("Savannah", path.read_text(encoding="utf-8-sig"))

    def test_no_hq_naming_warnings(self):
        result = net.Result()
        terr.validate_territory(ROOT, result)
        self.assertTrue(result.valid, result.errors)
        self.assertFalse(any("does not follow" in w for w in result.warnings))

    def test_rounding_is_confirmed(self):
        pricing = terr.RULES["missionProgression"]["ordinaryLeadPricing"]
        self.assertEqual(pricing["rounding"], "ROUND_HALF_UP_WHOLE_EVIDENCE_POINTS")

    def test_budget_settings_exist_but_are_undecided(self):
        settings = {r["setting_id"]: r for r in rows("territory_settings.csv")}
        cycle = settings["BUDGET_CYCLE_MINUTES"]
        window = settings["SUCCESS_RATE_WINDOW_CYCLES"]
        self.assertEqual((cycle["unit"], cycle["value"], cycle["active"].lower()), ("STRATEGIC_MINUTES", "", "false"))
        self.assertEqual((window["unit"], window["value"], window["active"].lower()), ("COUNT", "", "false"))

    def test_strawman_values_are_inactive_and_in_range(self):
        inputs = {r["input_id"]: r for r in rows("congressional_support_inputs.csv")}
        self.assertEqual([inputs[k]["weight"] for k in ("CS_INPUT_EVIDENCE", "CS_INPUT_PREPAREDNESS", "CS_INPUT_SUCCESS_RATE")],
                         ["2", "1", "1"])
        levels = sorted(rows("congressional_support_levels.csv"), key=lambda r: int(r["sort_order"]))
        self.assertEqual([int(r["min_score"]) for r in levels], [15, 30, 45, 60, 75])
        granted = [int(r["grant_territories"]) for r in levels]
        low, high = terr.GENERATION_RULES["generatedOperationalTerritoryTargetRange"]
        self.assertTrue(low <= sum(granted) <= high, sum(granted))
        for row in list(inputs.values()) + levels:
            self.assertEqual(row["active"].lower(), "false")

    def test_territories_are_permanent_and_cumulative(self):
        self.assertEqual(cs.territories_granted(LEVELS, None), 0)
        self.assertEqual(cs.territories_granted(LEVELS, "L1"), 2)
        self.assertEqual(cs.territories_granted(LEVELS, "L3"), 7)
        with self.assertRaises(ValueError):
            cs.territories_granted(LEVELS, "L9")

    def test_budget_follows_the_current_level(self):
        self.assertEqual(cs.recurring_budget(LEVELS, "L3"), 300)
        self.assertEqual(cs.recurring_budget(LEVELS, "L1"), 100)
        self.assertEqual(cs.recurring_budget(LEVELS, None), 0)
        self.assertEqual(cs.territories_granted(LEVELS, "L3"), 7)

    def test_rules_record_the_models(self):
        rules = cs.RULES
        self.assertEqual(rules["fundingGrantModel"], "RECURRING_BUDGET_PER_CYCLE_FOLLOWS_CURRENT_LEVEL")
        self.assertEqual(rules["territoryGrantModel"], "PERMANENT_CUMULATIVE_BY_HIGHEST_LEVEL_REACHED")
        self.assertTrue(rules["fundingCanBeLost"])
        self.assertEqual(rules["levelReview"], "BUDGET_CYCLE_OR_HEARING")
        self.assertEqual(rules["preparednessScoring"], "HIGHER_IS_ALWAYS_BETTER")
        self.assertEqual(rules["successRateThreshold"], "SOFT_FLOOR")
        self.assertTrue(terr.GENERATION_RULES["tier6GateKeepsSeparateMinimums"])


if __name__ == "__main__":
    unittest.main()
