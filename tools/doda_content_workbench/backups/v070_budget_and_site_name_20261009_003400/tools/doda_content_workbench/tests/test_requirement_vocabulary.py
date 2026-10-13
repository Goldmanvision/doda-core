import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_network_rules as net
import doda_territory_rules as terr
import test_territory_rules as base

ROOT = net.find_project_root(Path(__file__).resolve().parent)


def rows(name):
    with (ROOT / "data_authoring/source" / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def real_data():
    result = net.Result()
    data = terr.validate_territory(ROOT, result)
    return result, data


class RequirementVocabularyTests(unittest.TestCase):
    setUp = base.TerritoryTests.setUp
    tearDown = base.TerritoryTests.tearDown
    make_root = base.TerritoryTests.make_root
    validate = base.TerritoryTests.validate

    def test_necronomicon_milestones_seeded(self):
        ids = {row["milestone_id"] for row in rows("plot_milestones.csv")}
        self.assertEqual(ids, {"PLOT_NECRONOMICON_COLLECTED", "PLOT_NECRONOMICON_PROCESSED"})
        items = {row["plot_item_id"] for row in rows("plot_items.csv")}
        self.assertIn("PLOT_ITEM_NECRONOMICON", items)

    def test_requirements_target_tier6_and_stay_inactive(self):
        requirements = rows("mission_tier_requirements.csv")
        self.assertEqual(len(requirements), 2)
        for row in requirements:
            self.assertEqual(row["tier_id"], "TIER_6")
            self.assertEqual(row["active"].lower(), "false")
            self.assertFalse(row["upgrade_id"] or row["plot_item_id"])
        self.assertEqual({row["milestone_id"] for row in requirements},
                         {"PLOT_NECRONOMICON_COLLECTED", "PLOT_NECRONOMICON_PROCESSED"})

    def test_final_gate_still_unconfigured(self):
        result, data = real_data()
        self.assertTrue(result.valid, result.errors)
        gate = data["missionProgression"]["finalGate"]
        self.assertFalse(gate["configured"])
        self.assertIn("REQUIRED_UPGRADE_REFERENCES", gate["missingConfiguration"])
        self.assertIn("REQUIRED_PLOT_MILESTONE_OR_ITEM_REFERENCES", gate["missingConfiguration"])

    def test_ordinary_pricing_configured_with_starting_values(self):
        result, data = real_data()
        self.assertTrue(result.valid, result.errors)
        pricing = data["missionProgression"]["ordinaryPricing"]
        self.assertTrue(pricing["configured"])
        self.assertEqual(pricing["baseCost"], 100)
        self.assertEqual(pricing["growthPercentScaled"], 100000)
        self.assertEqual(terr.ordinary_lead_cost(pricing["baseCost"], pricing["growthPercentScaled"], 2), 121)

    def test_headquarters_names(self):
        by_id = {row["territory_id"]: row for row in rows("territories.csv")}
        self.assertEqual(by_id["TERR_EBON_FALLS"]["hq_name"], "Ebon Falls DoDA Office")
        self.assertEqual(by_id["TERR_ROSEWELL"]["hq_name"], "Roswell DoDA Office")
        self.assertEqual(by_id["TERR_SRS_NUCLEAR_FACILITY"]["hq_name"], "Savannah River DoDA Office")
        kaddath = by_id["TERR_UNKNOWN_KADDATH"]
        self.assertEqual(kaddath["hq_name"], "DoDA Unknown Kaddath Satellite Operations Center")
        self.assertIn("DUKSOC", kaddath["description"])

    def test_hq_naming_pattern_warning(self):
        territories = base.territory_rows()
        territories[0]["locality"] = "Start"
        territories[0]["hq_name"] = "Wrong Name"
        result, _ = self.validate(territories=territories)
        self.assertTrue(result.valid, result.errors)
        self.assertTrue(any("does not follow" in warning for warning in result.warnings))
        territories[0]["hq_name"] = "Start DoDA Office"
        result, _ = self.validate(territories=territories)
        self.assertFalse(any("does not follow" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
