import csv
import json
import shutil
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_network_rules as net
import doda_personal_care_rules as pc
import doda_sobriety_rules as sob
import test_personal_care_rules as base
import test_sobriety_rules as sobt

ROOT = net.find_project_root(Path(__file__).resolve().parent)


class VacationReturnTests(unittest.TestCase):
    run_rows = base.T.run_rows
    make_root = sobt.SobrietyTests.make_root

    def setUp(self):
        self.dirs = []
        self.roots = []

    def tearDown(self):
        for p in self.dirs + self.roots:
            shutil.rmtree(p, ignore_errors=True)

    def reset_list(self):
        r, _ = self.run_rows()
        self.assertTrue(r.valid, r.errors)
        res, out = pc.export(self.dirs[-1])
        self.assertTrue(res.valid, res.errors)
        payload = json.loads(out.read_text(encoding="utf-8"))
        return payload["placeRule"]["vacation"]["setToBestOnReturn"]

    def test_exports_agree_on_vacation_return(self):
        reset = self.reset_list()
        res, out = sob.export(self.make_root())
        self.assertTrue(res.valid, res.errors)
        vacation = json.loads(out.read_text(encoding="utf-8"))["rules"]["vacation"]
        self.assertIn(sob.INTOXICATION_STAT, reset)
        self.assertFalse(vacation["intoxicationTracked"])
        self.assertEqual(vacation["onReturn"], "SOBER")

    def test_reset_stats_exist(self):
        reset = self.reset_list()
        path = ROOT / "data_authoring" / "source" / "condition_stats.csv"
        with path.open(encoding="utf-8-sig", newline="") as fh:
            known = {(r.get("stat_id") or "").strip() for r in csv.DictReader(fh)}
        self.assertEqual([s for s in reset if s not in known], [])


if __name__ == "__main__":
    unittest.main()