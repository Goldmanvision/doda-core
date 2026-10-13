import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)


class MissionTierFoundationTests(unittest.TestCase):
    def rows(self):
        path = ROOT / "data_authoring" / "source" / terr.TIERS_FILE
        with path.open(encoding="utf-8-sig", newline="") as fh:
            return list(csv.DictReader(fh))

    def test_six_stable_tier_ids(self):
        rows = self.rows()
        ordered = sorted(rows, key=lambda row: int(row["sort_order"]))
        self.assertEqual(
            [row["tier_id"] for row in ordered],
            [f"TIER_{number}" for number in range(1, 7)],
        )

    def test_only_final_tier_is_authored(self):
        authored = [
            row["tier_id"] for row in self.rows()
            if row["authored_content"].strip().lower() == "true"
        ]
        self.assertEqual(authored, ["TIER_6"])

    def test_first_threshold_is_zero(self):
        rows = {row["tier_id"]: row for row in self.rows()}
        self.assertEqual(int(rows["TIER_1"]["min_lifetime_evidence"]), 0)

    def test_validated_payload_contains_all_tiers(self):
        result = net.Result()
        payload = terr.validate_territory(ROOT, result)
        self.assertEqual(result.errors, [])
        self.assertEqual(len(payload["missionTiers"]), 6)
        self.assertEqual(payload["missionTiers"][-1]["tierId"], "TIER_6")
        self.assertTrue(payload["missionTiers"][-1]["authoredContent"])


if __name__ == "__main__":
    unittest.main()
