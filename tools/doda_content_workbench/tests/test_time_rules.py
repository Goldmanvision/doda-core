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
import doda_time_rules as tr


def _row(sid, name, cat, value, unit, editable, order):
    return {"setting_id": sid, "display_name": name, "category": cat, "value": value, "unit": unit,
            "editable": editable, "source_reference": "test", "description": "",
            "sort_order": str(order), "active": "false"}


def base_rows():
    return [
        _row("DOOM_TICS_PER_SECOND", "Doom Tics", "ENGINE", "35", "TICS_PER_SECOND", "false", 10),
        _row("SIM_TICK_STRATEGIC_MINUTES", "Sim Tick", "SIM_TICK", "1", "MINUTES", "true", 20),
        _row("DOOM_TICS_PER_SIM_TICK_FOIMSX_1X", "FOIMS-X Tics", "PACING", "35", "TICS", "true", 30),
        _row("STRATEGIC_SECONDS_PER_REAL_SECOND_OUTSIDE", "Outside", "PACING", "1", "RATIO", "true", 40),
        _row("FOIMSX_SPEED_1X", "Normal", "FOIMSX_SPEED", "1", "MULTIPLIER", "true", 50),
        _row("FOIMSX_SPEED_2X", "Fast", "FOIMSX_SPEED", "2", "MULTIPLIER", "true", 60),
        _row("FOIMSX_SPEED_3X", "Fastest", "FOIMSX_SPEED", "3", "MULTIPLIER", "true", 70),
    ]


def patch(rows, sid, **changes):
    for r in rows:
        if r["setting_id"] == sid:
            r.update(changes)
    return rows


class TimeRulesTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    def make_root(self, rows=None):
        rows = rows if rows is not None else base_rows()
        root = Path(tempfile.gettempdir()) / f"doda_time_test_{uuid.uuid4().hex}"
        src = root / "data_authoring" / "source"
        src.mkdir(parents=True)
        with (src / tr.SETTINGS_FILE).open("w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=tr.SETTING_COLUMNS, lineterminator="\r\n")
            w.writeheader()
            w.writerows(rows)
        self.roots.append(root)
        return root

    def validate(self, rows=None):
        root = self.make_root(rows)
        res = net.Result()
        data = tr.validate_time_settings(root, res)
        return res, data

    def test_valid_fixture_and_derived_values(self):
        res, data = self.validate()
        self.assertEqual(res.errors, [])
        self.assertEqual(data["derived"]["outsideFoimsx"]["doomTicsPerSimTick"], "2100")
        self.assertEqual(data["derived"]["outsideFoimsx"]["realSecondsPerSimTick"], "60")
        speeds = {s["settingId"]: s for s in data["derived"]["foimsxSpeeds"]}
        self.assertEqual(speeds["FOIMSX_SPEED_1X"]["strategicSecondsPerRealSecond"], "60")
        self.assertEqual(speeds["FOIMSX_SPEED_2X"]["strategicSecondsPerRealSecond"], "120")
        self.assertEqual(speeds["FOIMSX_SPEED_3X"]["doomTicsPerSimTick"], "11.6667")

    def test_scaled_values(self):
        res, data = self.validate()
        by_id = {s["settingId"]: s for s in data["settings"]}
        self.assertEqual(by_id["FOIMSX_SPEED_2X"]["valueScaled"], 20000)

    def test_missing_required_setting(self):
        rows = [r for r in base_rows() if r["setting_id"] != "SIM_TICK_STRATEGIC_MINUTES"]
        res, _ = self.validate(rows)
        self.assertTrue(any("SIM_TICK_STRATEGIC_MINUTES" in e for e in res.errors))

    def test_too_many_decimal_places(self):
        res, _ = self.validate(patch(base_rows(), "FOIMSX_SPEED_2X", value="1.23456"))
        self.assertTrue(any("decimal places" in e for e in res.errors))

    def test_speeds_must_ascend(self):
        rows = patch(base_rows(), "FOIMSX_SPEED_3X", value="2")
        res, _ = self.validate(rows)
        self.assertTrue(any("must ascend" in e for e in res.errors))

    def test_sim_tick_must_be_whole(self):
        res, _ = self.validate(patch(base_rows(), "SIM_TICK_STRATEGIC_MINUTES", value="1.5"))
        self.assertTrue(any("whole number" in e for e in res.errors))

    def test_engine_constant_not_editable(self):
        res, _ = self.validate(patch(base_rows(), "DOOM_TICS_PER_SECOND", editable="true"))
        self.assertTrue(any("cannot be editable" in e for e in res.errors))

    def test_duplicate_id(self):
        rows = base_rows() + [_row("FOIMSX_SPEED_1X", "Dup", "FOIMSX_SPEED", "4", "MULTIPLIER", "true", 80)]
        res, _ = self.validate(rows)
        self.assertTrue(any("duplicate" in e for e in res.errors))

    def test_export_is_deterministic_and_not_runtime(self):
        root = self.make_root()
        res1, out1 = tr.export(root)
        self.assertTrue(res1.valid)
        first = json.loads(out1.read_text(encoding="utf-8"))
        res2, out2 = tr.export(root)
        second = json.loads(out2.read_text(encoding="utf-8"))
        self.assertFalse(first["runtimeImplemented"])
        first.pop("generatedAtUtc")
        second.pop("generatedAtUtc")
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()