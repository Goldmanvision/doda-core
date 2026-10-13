import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_authored_mission_rules as am
import doda_network_rules as net
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)


def validate(root):
    result = net.Result()
    data = terr.validate_territory(root, result)
    return result, data


class TierThresholdAndGenerationTests(unittest.TestCase):
    def test_tier_thresholds(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        values = [t["minLifetimeAdmissibleEvidence"] for t in data["missionTiers"]]
        self.assertEqual(values, [1000, 10000, 100000, 1000000, 10000000, 100000000])

    def test_tutorial_summary(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        tutorial = data["missionProgression"]["tutorial"]
        self.assertEqual(tutorial["startingEvidence"], 900)
        self.assertEqual(tutorial["firstTierThreshold"], 1000)
        self.assertEqual(tutorial["evidenceToFirstTier"], 100)
        self.assertTrue(tutorial["configured"])

    def test_thresholds_must_still_increase(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "data_authoring" / "source"
        shutil.copytree(ROOT / "data_authoring" / "source", target)
        path = target / "mission_tiers.csv"
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
            columns = list(rows[0].keys())
        rows[1]["min_lifetime_admissible_evidence"] = "1000"
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(rows)
        result, _ = validate(Path(temp.name))
        self.assertTrue(any("must strictly increase" in e for e in result.errors))

    def test_generation_rules(self):
        rules = terr.GENERATION_RULES
        self.assertEqual(rules["tierUnlock"], "ALL_REQUIREMENTS_MET_AUTOMATIC")
        self.assertEqual(rules["missionTierPool"], "ALL_TIERS_UP_TO_HIGHEST_ACHIEVED")
        self.assertEqual(rules["missionMixWeights"], "EQUAL_ACROSS_UNLOCKED_TIERS")
        self.assertEqual(rules["operationalTerritoryPlacement"], "RANDOM_ACROSS_GREATER_TERRITORIES")
        self.assertTrue(rules["authoredTerritoriesExcludedUntilUnlocked"])
        self.assertEqual(rules["territoryUnlockMechanism"], "CONGRESSIONAL_SUPPORT")
        self.assertEqual(rules["congressionalSupportScoring"], "COMPENSATORY_COMBINED_SCORE")
        self.assertTrue(rules["lifetimeEvidenceIncludesStartingEvidence"])
        self.assertFalse(rules["spendingReducesLifetimeEvidence"])
        self.assertFalse(rules["congressionalSupportImplemented"])
        self.assertEqual(am.RULES["tier6UnlockTrigger"], "ALL_REQUIREMENTS_MET_AUTOMATIC")

    def test_starting_evidence_setting(self):
        path = ROOT / "data_authoring/source/territory_settings.csv"
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = {row["setting_id"]: row for row in csv.DictReader(fh)}
        row = rows["STARTING_EVIDENCE"]
        self.assertEqual(row["value"], "900")
        self.assertEqual(row["unit"], "EVIDENCE_POINTS")
        self.assertEqual(row["active"].lower(), "true")


if __name__ == "__main__":
    unittest.main()
