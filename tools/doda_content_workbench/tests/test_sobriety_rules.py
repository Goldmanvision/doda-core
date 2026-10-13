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
import doda_sobriety_rules as sob

REF = "User decision 2026-10-08 (alcohol and sobriety)"


def _stage(sid, name, low, mult, drive, uncon, note, order):
    return {"stage_id": sid, "display_name": name, "min_intoxication": low, "skill_multiplier": mult,
            "can_drive": drive, "unconscious": uncon, "driving_note": note, "source_reference": REF,
            "description": "", "sort_order": str(order), "active": "false"}


def stage_rows():
    return [_stage("SOBER", "Sober", "0", "1", "true", "false", "", 10),
            _stage("BUZZED", "Buzzed", "15", "0.5", "false", "false", "Asks a friend to drive.", 20),
            _stage("DRUNK", "Drunk", "45", "0.25", "false", "false", "Asks a friend to drive.", 30),
            _stage("HEAVILY_INTOXICATED", "Heavily Intoxicated", "75", "", "false", "true", "", 40)]


def _setting(sid, name, value, unit, order):
    return {"setting_id": sid, "display_name": name, "value": value, "unit": unit,
            "source_reference": REF, "description": "", "sort_order": str(order), "active": "false"}


def setting_rows():
    return [_setting(sob.DECAY_ID, "Decay", "0.2", "POINTS_PER_STRATEGIC_MINUTE", 10),
            _setting(sob.WAKE_ID, "Wake", "60", "POINTS", 20)]


def _rule(rid, low, stage, order):
    return {"rule_id": rid, "loyalty_min": low, "max_stage_id": stage, "source_reference": REF,
            "description": "", "sort_order": str(order), "active": "false"}


def shift_rows():
    return [_rule("LOW", "0", "DRUNK", 10), _rule("MID", "25", "BUZZED", 20), _rule("HIGH", "50", "SOBER", 30)]


def edit(rows, field, match, **changes):
    for r in rows:
        if r[field] == match:
            r.update(changes)
    return rows


class SobrietyTests(unittest.TestCase):
    def setUp(self):
        self.roots = []

    def tearDown(self):
        for root in self.roots:
            shutil.rmtree(root, ignore_errors=True)

    def make_root(self, stages=None, settings=None, shift=None, stats=None):
        root = Path(tempfile.gettempdir()) / f"doda_sob_test_{uuid.uuid4().hex}"
        src = root / "data_authoring" / "source"
        src.mkdir(parents=True)
        for name, cols, rows in (
                (sob.STAGES_FILE, sob.STAGE_COLUMNS, stages if stages is not None else stage_rows()),
                (sob.SETTINGS_FILE, sob.SETTING_COLUMNS, settings if settings is not None else setting_rows()),
                (sob.SHIFT_RULES_FILE, sob.SHIFT_COLUMNS, shift if shift is not None else shift_rows())):
            with (src / name).open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=cols, lineterminator="\r\n")
                w.writeheader()
                w.writerows(rows)
        if stats is not None:
            (src / "condition_stats.csv").write_text(stats, encoding="utf-8")
        self.roots.append(root)
        return root

    def validate(self, **kw):
        root = self.make_root(**kw)
        res = net.Result()
        return res, sob.validate_sobriety(root, res)

    def has(self, res, text):
        return any(text in e for e in res.errors)

    def test_valid_and_scaled(self):
        res, data = self.validate()
        self.assertEqual(res.errors, [])
        stages = {s["stageId"]: s for s in data["stages"]}
        self.assertEqual(len(stages), 4)
        self.assertEqual(stages["BUZZED"]["minIntoxicationScaled"], 150000)
        self.assertEqual(stages["BUZZED"]["skillMultiplierScaled"], 5000)
        self.assertIsNone(stages["HEAVILY_INTOXICATED"]["skillMultiplier"])

    def test_missing_stage(self):
        res, _ = self.validate(stages=[r for r in stage_rows() if r["stage_id"] != "DRUNK"])
        self.assertTrue(self.has(res, "must define exactly the four stages"))

    def test_unknown_stage_id(self):
        res, _ = self.validate(stages=stage_rows() + [_stage("TIPSY", "Tipsy", "5", "0.9", "true", "false", "", 50)])
        self.assertTrue(self.has(res, "stage_id must be one of"))

    def test_min_must_increase(self):
        res, _ = self.validate(stages=edit(stage_rows(), "stage_id", "DRUNK", min_intoxication="10"))
        self.assertTrue(self.has(res, "must strictly increase"))

    def test_sober_starts_at_zero(self):
        res, _ = self.validate(stages=edit(stage_rows(), "stage_id", "SOBER", min_intoxication="5"))
        self.assertTrue(self.has(res, "SOBER must start at 0"))

    def test_only_top_stage_unconscious(self):
        res, _ = self.validate(stages=edit(stage_rows(), "stage_id", "BUZZED", unconscious="true"))
        self.assertTrue(self.has(res, "only HEAVILY_INTOXICATED can be unconscious"))

    def test_top_stage_must_be_unconscious(self):
        res, _ = self.validate(stages=edit(stage_rows(), "stage_id", "HEAVILY_INTOXICATED", unconscious="false"))
        self.assertTrue(self.has(res, "HEAVILY_INTOXICATED must be unconscious"))

    def test_skill_must_not_rise(self):
        res, _ = self.validate(stages=edit(stage_rows(), "stage_id", "DRUNK", skill_multiplier="0.6"))
        self.assertTrue(self.has(res, "skill_multiplier must not rise"))

    def test_sober_multiplier_is_one(self):
        res, _ = self.validate(stages=edit(stage_rows(), "stage_id", "SOBER", skill_multiplier="0.9"))
        self.assertTrue(self.has(res, "SOBER skill_multiplier must be 1"))

    def test_no_drive_needs_note(self):
        res, _ = self.validate(stages=edit(stage_rows(), "stage_id", "BUZZED", driving_note=""))
        self.assertTrue(self.has(res, "needs a driving_note"))

    def test_wake_threshold_below_unconscious_start(self):
        res, _ = self.validate(settings=edit(setting_rows(), "setting_id", sob.WAKE_ID, value="80"))
        self.assertTrue(self.has(res, "must be above 0 and below"))

    def test_decay_must_be_positive(self):
        res, _ = self.validate(settings=edit(setting_rows(), "setting_id", sob.DECAY_ID, value="0"))
        self.assertTrue(self.has(res, "value must be above 0"))

    def test_shift_rules(self):
        res, _ = self.validate(shift=edit(shift_rows(), "rule_id", "LOW", loyalty_min="5"))
        self.assertTrue(self.has(res, "must start at loyalty_min 0"))
        res, _ = self.validate(shift=edit(shift_rows(), "rule_id", "MID", max_stage_id="TIPSY"))
        self.assertTrue(self.has(res, "unknown max_stage_id"))
        res, _ = self.validate(shift=edit(shift_rows(), "rule_id", "LOW", max_stage_id="HEAVILY_INTOXICATED"))
        self.assertTrue(self.has(res, "cannot arrive at a shift"))
        res, _ = self.validate(shift=edit(shift_rows(), "rule_id", "HIGH", max_stage_id="DRUNK"))
        self.assertTrue(self.has(res, "cannot allow a more intoxicated arrival"))

    def test_missing_stat_warns(self):
        res, _ = self.validate(stats="stat_id,maximum_value\nLOYALTY,100\n")
        self.assertEqual(res.errors, [])
        self.assertTrue(any("INTOXICATION" in w for w in res.warnings))

    def test_stat_maximum_is_used(self):
        res, _ = self.validate(stats="stat_id,maximum_value\nINTOXICATION,70\n")
        self.assertTrue(self.has(res, "must be below the INTOXICATION maximum"))

    def test_export_not_runtime(self):
        root = self.make_root()
        res, out = sob.export(root)
        self.assertTrue(res.valid, res.errors)
        payload = json.loads(out.read_text(encoding="utf-8"))
        self.assertFalse(payload["runtimeImplemented"])
        self.assertEqual(len(payload["shiftRules"]), 3)
        self.assertEqual(len(payload["stages"]), 4)


if __name__ == "__main__":
    unittest.main()