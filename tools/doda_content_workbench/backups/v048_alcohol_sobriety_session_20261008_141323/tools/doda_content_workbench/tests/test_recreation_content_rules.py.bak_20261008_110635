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
import doda_recreation_content_rules as rc

NAMES = [("MINIMAL", "Minimal"), ("VERY_LOW", "Very Low"), ("LOW", "Low"), ("MODERATE", "Moderate"),
         ("HIGH", "High"), ("VERY_HIGH", "Very High"), ("FULL", "Full")]
HUNGER = ["5", "10", "20", "35", "50", "80", "100"]


def _lv(scale, level, name, value, unit, order, active="false"):
    return {"scale_id": scale, "level_id": level, "display_name": name, "value": value, "unit": unit,
            "source_reference": "test", "description": "", "sort_order": str(order), "active": active}


def base_levels():
    rows = []
    for i, (lid, name) in enumerate(NAMES):
        rows.append(_lv("HUNGER_RESTORE", lid, name, HUNGER[i], "PERCENT_OF_NUTRITION_RANGE", (i + 1) * 10))
    for i, (lid, name) in enumerate(NAMES):
        rows.append(_lv("STRESS_REDUCTION", lid, name, "", "PER_TICK", (i + 1) * 10))
    for i, (lid, name) in enumerate(NAMES):
        rows.append(_lv("FATIGUE_COST", lid, name, "", "PER_TICK", (i + 1) * 10))
    return rows


def base_books():
    return [{"book_id": "BOOK_001", "title": "Spooky Car", "author": "Keaton Sting", "notes": "",
             "sort_order": "10", "active": "false"},
            {"book_id": "BOOK_002", "title": "Jules, I Think My Leg is On Fire", "author": "Hector Rinaldo",
             "notes": "", "sort_order": "20", "active": "false"}]


def patch(rows, key, target, **changes):
    for r in rows:
        if r.get("level_id") == target[1] and r.get("scale_id") == target[0]:
            r.update(changes)
    return rows


class RecreationContentTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    def make_root(self, levels=None, books=None):
        levels = levels if levels is not None else base_levels()
        books = books if books is not None else base_books()
        root = Path(tempfile.gettempdir()) / f"doda_rc_test_{uuid.uuid4().hex}"
        src = root / "data_authoring" / "source"
        src.mkdir(parents=True)
        for name, cols, rows in ((rc.LEVELS_FILE, rc.LEVEL_COLUMNS, levels), (rc.BOOKS_FILE, rc.BOOK_COLUMNS, books)):
            with (src / name).open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
        self.roots.append(root)
        return root

    def validate(self, levels=None, books=None):
        root = self.make_root(levels, books)
        res = net.Result()
        data = rc.validate_recreation_content(root, res)
        return res, data

    def test_valid_fixture(self):
        res, data = self.validate()
        self.assertEqual(res.errors, [])
        hunger = {l["levelId"]: l for l in data["effectLevels"] if l["scaleId"] == "HUNGER_RESTORE"}
        self.assertEqual(hunger["LOW"]["valueScaled"], 200000)
        self.assertEqual(len(data["bookTitles"]), 2)

    def test_hunger_above_100(self):
        res, _ = self.validate(patch(base_levels(), None, ("HUNGER_RESTORE", "FULL"), value="101"))
        self.assertTrue(any("at most 100" in e for e in res.errors))

    def test_values_must_increase(self):
        res, _ = self.validate(patch(base_levels(), None, ("HUNGER_RESTORE", "LOW"), value="4"))
        self.assertTrue(any("strictly increase" in e for e in res.errors))

    def test_unit_mismatch(self):
        res, _ = self.validate(patch(base_levels(), None, ("HUNGER_RESTORE", "LOW"), unit="PER_TICK"))
        self.assertTrue(any("must use unit" in e for e in res.errors))

    def test_active_level_needs_value(self):
        res, _ = self.validate(patch(base_levels(), None, ("STRESS_REDUCTION", "MODERATE"), active="true"))
        self.assertTrue(any("needs a value" in e for e in res.errors))

    def test_duplicate_level(self):
        rows = base_levels() + [_lv("HUNGER_RESTORE", "LOW", "Low again", "21", "PERCENT_OF_NUTRITION_RANGE", 99)]
        res, _ = self.validate(rows)
        self.assertTrue(any("duplicate level" in e for e in res.errors))

    def test_too_many_decimals(self):
        res, _ = self.validate(patch(base_levels(), None, ("STRESS_REDUCTION", "LOW"), value="0.12345"))
        self.assertTrue(any("decimal places" in e for e in res.errors))

    def test_duplicate_book_id(self):
        books = base_books() + [dict(base_books()[0])]
        res, _ = self.validate(books=books)
        self.assertTrue(any("duplicate book_id" in e for e in res.errors))

    def test_missing_title(self):
        books = base_books()
        books[0]["title"] = ""
        res, _ = self.validate(books=books)
        self.assertTrue(any("title is required" in e for e in res.errors))

    def test_export_deterministic_and_not_runtime(self):
        root = self.make_root()
        res1, out1 = rc.export(root)
        self.assertTrue(res1.valid)
        first = json.loads(out1.read_text(encoding="utf-8"))
        res2, out2 = rc.export(root)
        second = json.loads(out2.read_text(encoding="utf-8"))
        self.assertFalse(first["runtimeImplemented"])
        titles = [b["title"] for b in first["bookTitles"]]
        self.assertIn("Jules, I Think My Leg is On Fire", titles)
        first.pop("generatedAtUtc")
        second.pop("generatedAtUtc")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()