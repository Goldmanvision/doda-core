import ast
import math
import sys
import unittest
from copy import deepcopy
from pathlib import Path

WORK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WORK))
from doda_foims_x_sandbox import FoimsXSandbox

parsed = ast.parse((WORK / "doda_foims_x_preview.py").read_text(encoding="utf-8-sig"))
number = next(n for n in parsed.body if isinstance(n, ast.FunctionDef) and n.name == "numeric_value")
klass = next(n for n in parsed.body if isinstance(n, ast.ClassDef) and n.name == "FoimsXPreview")
klass.body = [
    n for n in klass.body if isinstance(n, ast.FunctionDef)
    and n.name in ("_visible_metric_rows", "_tier_for_value")
]
subset = ast.Module(body=[number, klass], type_ignores=[])
exec(compile(subset, "preview_projection_methods", "exec"), globals())

class Clock:
    def __init__(self):
        self.now = 0.0
    def __call__(self):
        return self.now

class Variable:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value

class FoimsXMetricActivityTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.tables = {"metrics": [
            {"metric_id": "M" + str(i), "display_name": "Metric " + str(i),
             "default_value": "300", "internal_min": "0",
             "internal_max": "1000", "active": "true"}
            for i in range(5)
        ]}
        self.tables["metrics"].append({
            "metric_id": "OFF", "default_value": "10", "active": "false"
        })
        self.model = FoimsXSandbox(self.tables, self.clock)

    def test_valid_metric_change(self):
        self.assertTrue(self.model.set_metric("M0", "600"))
        self.assertEqual(self.model.metrics["M0"], 600)

    def test_inclusive_bounds(self):
        self.model.set_metric("M0", 0)
        self.model.set_metric("M0", 1000)
        self.assertEqual(self.model.metrics["M0"], 1000)

    def test_bad_values_are_atomic(self):
        baseline = self.model.snapshot()
        for value in (-1, 1001, "abc", "NaN", "Infinity", 1.5, True, ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.model.set_metric("M0", value)
                self.assertEqual(self.model.snapshot(), baseline)

    def test_unknown_and_inactive_rejected(self):
        for metric in ("UNKNOWN", "OFF"):
            with self.assertRaises(ValueError):
                self.model.set_metric(metric, 5)

    def test_timestamp_and_before_after(self):
        self.model.step(60)
        self.model.set_metric("M0", 500)
        self.assertEqual(self.model.snapshot()["activity"], [{
            "strategic_minutes": 60,
            "timestamp": "1992-02-01 01:00:00",
            "metric_id": "M0", "before": 300.0, "after": 500
        }])

    def test_running_action_settles_time(self):
        self.model.play()
        self.clock.now = 12
        self.model.set_metric("M0", 400)
        self.assertEqual(self.model.activity[0]["strategic_minutes"], 12)
        self.assertTrue(self.model.running)

    def test_noop_does_not_log(self):
        self.assertFalse(self.model.set_metric("M0", 300))
        self.assertEqual(self.model.activity, [])

    def test_reset_clears_history(self):
        self.model.set_metric("M0", 500)
        self.model.reset()
        self.assertEqual(self.model.activity, [])
        self.assertEqual(self.model.metrics["M0"], 300)

    def test_catalog_and_snapshot_detached(self):
        baseline = deepcopy(self.tables)
        self.model.set_metric("M0", 500)
        self.model.metric_rows()[0]["display_name"] = "Changed"
        self.model.snapshot()["activity"][0]["after"] = 12
        self.assertEqual(self.tables, baseline)
        self.assertEqual(self.model.activity[0]["after"], 500)

    def test_activity_history_is_bounded(self):
        for i in range(205):
            self.model.set_metric("M0", i)
        self.assertEqual(len(self.model.activity), 200)
        self.assertEqual(self.model.activity[-1]["after"], 204)

    def test_each_metric_can_be_shown_first(self):
        preview = FoimsXPreview.__new__(FoimsXPreview)
        preview.sandbox = self.model
        preview.selected_metric = Variable()
        for i in range(5):
            preview.selected_metric.set("M" + str(i))
            rows = preview._visible_metric_rows()
            self.assertEqual(rows[0]["metric_id"], "M" + str(i))
            self.assertEqual(len(rows), 3)

    def test_tier_projection_changes_at_boundaries(self):
        tiers = [
            {"metric_id": "M0", "min_inclusive": "0",
             "max_inclusive": "200", "tier_id": "LOW"},
            {"metric_id": "M0", "min_inclusive": "201",
             "max_inclusive": "1000", "tier_id": "HIGH"},
        ]
        for value, expected in ((200, "LOW"), (201, "HIGH"), (1000, "HIGH")):
            self.model.set_metric("M0", value)
            tier = FoimsXPreview._tier_for_value(
                "M0", self.model.metrics["M0"], tiers
            )
            self.assertEqual(tier["tier_id"], expected)

if __name__ == "__main__":
    unittest.main()
