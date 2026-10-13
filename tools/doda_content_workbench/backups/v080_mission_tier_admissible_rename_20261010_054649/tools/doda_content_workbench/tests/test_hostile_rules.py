import csv
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_hostile_rules as host
import doda_network_rules as net
import doda_territory_rules as terr
import doda_weapon_rules as wpn


def _h(hid, ec="", weapon="", tier="", authored="false", active="false", order=10):
    return {"hostile_id": hid, "display_name": hid, "engine_class": ec, "weapon_id": weapon, "tier_id": tier,
            "authored_only": authored, "placeholder": "true", "source_reference": "test", "description": "",
            "sort_order": str(order), "active": active}


def _weapon(active="false"):
    return {"weapon_id": "W1", "display_name": "W1", "weapon_type": "PISTOL", "engine_class": "",
            "tags": "", "source_reference": "test", "description": "", "sort_order": "10", "active": active}


def _tier():
    return {"tier_id": "T1", "display_name": "T1", "min_lifetime_evidence": "0", "authored_content": "true",
            "source_reference": "test", "description": "", "sort_order": "10", "active": "false"}


def _write(src, name, cols, rows):
    with (src / name).open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        w.writerows(rows)


class HostileTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    def make_root(self, rows, weapons=None, tiers=None):
        root = Path(tempfile.gettempdir()) / f"doda_host_test_{uuid.uuid4().hex}"
        src = root / "data_authoring" / "source"
        src.mkdir(parents=True)
        _write(src, host.HOSTILES_FILE, host.HOSTILE_COLUMNS, rows)
        _write(src, wpn.WEAPONS_FILE, wpn.WEAPON_COLUMNS, [_weapon()] if weapons is None else weapons)
        _write(src, terr.TIERS_FILE, terr.TIER_COLUMNS, [_tier()] if tiers is None else tiers)
        self.roots.append(root)
        return root

    def run_rows(self, rows, **kw):
        res = net.Result()
        data = host.validate_hostiles(self.make_root(rows, **kw), res)
        return res, data

    def has(self, res, text):
        return any(text in e for e in res.errors)

    def test_valid(self):
        res, data = self.run_rows([_h("A", ec="Foo", weapon="W1", tier="T1"), _h("B", authored="true", order=20)])
        self.assertEqual(res.errors, [])
        self.assertEqual(len(data["hostiles"]), 2)

    def test_unknown_references(self):
        res, _ = self.run_rows([_h("A", weapon="NOPE")])
        self.assertTrue(self.has(res, "unknown weapon_id 'NOPE'"))
        res, _ = self.run_rows([_h("A", tier="NOPE")])
        self.assertTrue(self.has(res, "unknown tier_id 'NOPE'"))

    def test_authored_only_has_no_tier(self):
        res, _ = self.run_rows([_h("A", tier="T1", authored="true")])
        self.assertTrue(self.has(res, "authored_only hostile must not have a tier_id"))

    def test_active_needs_active_weapon(self):
        res, _ = self.run_rows([_h("A", weapon="W1", active="true")])
        self.assertTrue(self.has(res, "active hostile uses inactive weapon"))
        res, _ = self.run_rows([_h("A", weapon="W1", active="true")], weapons=[_weapon("true")])
        self.assertFalse(self.has(res, "inactive weapon"))

    def test_class_rules(self):
        res, _ = self.run_rows([_h("A", ec="Bad Name")])
        self.assertTrue(self.has(res, "engine_class must be a class name"))
        res, _ = self.run_rows([_h("A", ec="Foo"), _h("B", ec="foo", order=20)])
        self.assertTrue(self.has(res, "duplicate engine_class"))

    def test_duplicate_id(self):
        res, _ = self.run_rows([_h("A"), _h("A", order=20)])
        self.assertTrue(self.has(res, "duplicate hostile_id"))

    def test_active_warnings(self):
        res, _ = self.run_rows([_h("A", active="true")])
        self.assertEqual(res.errors, [])
        self.assertTrue(any("no engine_class yet" in x for x in res.warnings))
        self.assertTrue(any("no tier_id yet" in x for x in res.warnings))

    def test_export_not_runtime(self):
        res, out = host.export(self.make_root([_h("A")]))
        self.assertTrue(res.valid, res.errors)
        self.assertFalse(json.loads(out.read_text(encoding="utf-8"))["runtimeImplemented"])

    def test_shipped_data(self):
        res = net.Result()
        host.validate_hostiles(net.find_project_root(Path(__file__).resolve().parent), res)
        self.assertEqual(res.errors, [])


if __name__ == "__main__":
    unittest.main()