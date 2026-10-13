import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_authored_mission_rules as am
import doda_network_rules as net

ROOT = net.find_project_root(Path(__file__).resolve().parent)


def rows(name):
    with (ROOT / "data_authoring/source" / name).open(encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


class CapstoneSettingCorrectionTests(unittest.TestCase):
    def test_territory_uses_corrected_setting(self):
        row = next(r for r in rows("territories.csv") if r["territory_id"] == "TERR_SRS_NUCLEAR_FACILITY")
        self.assertEqual(row["region"], "GT_SOUTH_CAROLINA")
        self.assertIn("Savannah", row["display_name"])
        self.assertEqual(row["agents_allowed"].lower(), "true")

    def test_mission_uses_corrected_name(self):
        row = next(r for r in rows("authored_missions.csv") if r["mission_id"] == "MISSION_TIER5_CAPSTONE_01")
        self.assertEqual(row["display_name"], "Savannah River Site Nuclear Research Facility, South Carolina")

    def test_open_items_record_legal_review_and_undecided_rules(self):
        self.assertIn("Legal review", am.OPEN_ITEMS["CAP-OPEN-01"])
        self.assertEqual(am.RULES["tier6UnlockTrigger"], "ALL_REQUIREMENTS_MET_AUTOMATIC")
        self.assertIn("UNDECIDED", am.RULES["oneLeadPurchaseUnlocksWholeChain"])


if __name__ == "__main__":
    unittest.main()
