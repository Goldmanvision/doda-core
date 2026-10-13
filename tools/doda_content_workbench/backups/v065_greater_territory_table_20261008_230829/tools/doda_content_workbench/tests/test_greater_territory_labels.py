import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net

ROOT = net.find_project_root(Path(__file__).resolve().parent)


def territories():
    path = ROOT / "data_authoring/source/territories.csv"
    with path.open(encoding="utf-8-sig", newline="") as fh:
        return {row["territory_id"]: row for row in csv.DictReader(fh)}


class GreaterTerritoryLabelTests(unittest.TestCase):
    def test_greater_territory_names(self):
        rows = territories()
        self.assertEqual(rows["TERR_EBON_FALLS"]["region"], "Upstate New York")
        self.assertEqual(rows["TERR_ROSEWELL"]["region"], "New Mexico")
        self.assertEqual(rows["TERR_SRS_NUCLEAR_FACILITY"]["region"], "South Carolina")
        self.assertEqual(rows["TERR_UNKNOWN_KADDATH"]["region"], "The Dreamlands")

    def test_descriptions_are_not_stale(self):
        for row in territories().values():
            with self.subTest(territory=row["territory_id"]):
                self.assertNotIn("HQ name is blank", row["description"])
                self.assertNotIn("HQ name and", row["description"])


if __name__ == "__main__":
    unittest.main()
