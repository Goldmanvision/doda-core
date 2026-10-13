import csv
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_network_rules as net
import doda_recreation_content_rules as rc
from test_recreation_content_rules import NAMES, _lv, base_books, base_levels, patch

PERCENTS = ["5", "10", "20", "35", "50", "80", "100"]


def new_scale_levels():
    rows = []
    for scale, unit in (("ENERGY_RESTORE", "PERCENT_OF_ENERGY_RANGE"),
                        ("STRESS_GAIN", "PERCENT_OF_STRESS_RANGE")):
        for i, (lid, name) in enumerate(NAMES):
            rows.append(_lv(scale, lid, name, PERCENTS[i], unit, (i + 1) * 10))
    return rows


class EffectScaleTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    def validate(self, levels):
        root = Path(tempfile.gettempdir()) / f"doda_rc_scale_test_{uuid.uuid4().hex}"
        src = root / "data_authoring" / "source"
        src.mkdir(parents=True)
        for name, cols, rows in ((rc.LEVELS_FILE, rc.LEVEL_COLUMNS, levels),
                                 (rc.BOOKS_FILE, rc.BOOK_COLUMNS, base_books())):
            with (src / name).open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
        self.roots.append(root)
        res = net.Result()
        data = rc.validate_recreation_content(root, res)
        return res, data

    def test_new_scales_valid(self):
        res, data = self.validate(base_levels() + new_scale_levels())
        self.assertEqual(res.errors, [])
        energy = {l["levelId"]: l for l in data["effectLevels"] if l["scaleId"] == "ENERGY_RESTORE"}
        self.assertEqual(energy["LOW"]["valueScaled"], 200000)

    def test_new_scale_over_100(self):
        rows = patch(base_levels() + new_scale_levels(), None, ("ENERGY_RESTORE", "FULL"), value="101")
        res, _ = self.validate(rows)
        self.assertTrue(any("at most 100" in e for e in res.errors))

    def test_new_scale_wrong_unit(self):
        rows = patch(base_levels() + new_scale_levels(), None, ("STRESS_GAIN", "LOW"),
                     unit="PER_STRATEGIC_MINUTE")
        res, _ = self.validate(rows)
        self.assertTrue(any("must use unit" in e for e in res.errors))

    def test_stress_reduction_must_be_per_minute(self):
        rows = patch(base_levels(), None, ("STRESS_REDUCTION", "LOW"), unit="PER_TICK")
        res, _ = self.validate(rows)
        self.assertTrue(any("must use unit PER_STRATEGIC_MINUTE" in e for e in res.errors))

    def test_negative_stress_reduction_rejected(self):
        rows = patch(base_levels(), None, ("STRESS_REDUCTION", "LOW"), value="-1")
        res, _ = self.validate(rows)
        self.assertTrue(any("cannot be negative" in e for e in res.errors))


if __name__ == "__main__":
    unittest.main()