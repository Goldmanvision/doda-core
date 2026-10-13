import csv
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_weapon_rules as wpn


def _w(wid, wtype="PISTOL", ec="", tags="", order=10, active="false"):
    return {"weapon_id": wid, "display_name": wid, "weapon_type": wtype, "engine_class": ec, "tags": tags,
            "source_reference": "test", "description": "", "sort_order": str(order), "active": active}


class WeaponTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    def make_root(self, rows):
        root = Path(tempfile.gettempdir()) / f"doda_wpn_test_{uuid.uuid4().hex}"
        src = root / "data_authoring" / "source"
        src.mkdir(parents=True)
        with (src / wpn.WEAPONS_FILE).open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=wpn.WEAPON_COLUMNS, lineterminator="\r\n")
            w.writeheader()
            w.writerows(rows)
        self.roots.append(root)
        return root

    def run_rows(self, rows):
        res = net.Result()
        data = wpn.validate_weapons(self.make_root(rows), res)
        return res, data

    def has(self, res, text):
        return any(text in e for e in res.errors)

    def test_valid(self):
        res, data = self.run_rows([_w("A", tags="SUPPRESSED;X"), _w("B", "SMG", order=20)])
        self.assertEqual(res.errors, [])
        self.assertEqual(data["weapons"][0]["tags"], ["SUPPRESSED", "X"])

    def test_bad_type_and_duplicates(self):
        res, _ = self.run_rows([_w("A", "BOW")])
        self.assertTrue(self.has(res, "weapon_type must be one of"))
        res, _ = self.run_rows([_w("A"), _w("A")])
        self.assertTrue(self.has(res, "duplicate weapon_id"))

    def test_class_rules(self):
        res, _ = self.run_rows([_w("A", ec="Bad Name")])
        self.assertTrue(self.has(res, "engine_class must be a class name"))
        res, _ = self.run_rows([_w("A", ec="Gun"), _w("B", ec="gun")])
        self.assertTrue(self.has(res, "duplicate engine_class"))

    def test_tags(self):
        res, _ = self.run_rows([_w("A", tags="lower")])
        self.assertTrue(self.has(res, "tags must be uppercase"))
        res, _ = self.run_rows([_w("A", tags="X;X")])
        self.assertTrue(self.has(res, "tags has repeats"))

    def test_active_without_class_warns(self):
        res, _ = self.run_rows([_w("A", active="true")])
        self.assertEqual(res.errors, [])
        self.assertTrue(any("no engine_class yet" in x for x in res.warnings))

    def test_export_not_runtime(self):
        res, out = wpn.export(self.make_root([_w("A")]))
        self.assertTrue(res.valid, res.errors)
        self.assertFalse(json.loads(out.read_text(encoding="utf-8"))["runtimeImplemented"])

    def test_shipped_data(self):
        res = net.Result()
        wpn.validate_weapons(net.find_project_root(Path(__file__).resolve().parent), res)
        self.assertEqual(res.errors, [])


if __name__ == "__main__":
    unittest.main()