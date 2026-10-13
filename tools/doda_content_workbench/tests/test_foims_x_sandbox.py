import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_sandbox import FoimsXSandbox

class FakeClock:
    def __init__(self): self.now = 0.0
    def __call__(self): return self.now
    def advance(self, seconds): self.now += seconds

class FoimsXSandboxTests(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.tables = {"metrics": [{"metric_id": "PREPAREDNESS", "default_value": "300", "active": "true"}],
                       "territory_settings": [{"setting_id": "STARTING_EVIDENCE", "value": "900", "active": "true"}]}
        self.model = FoimsXSandbox(self.tables, self.clock)
    def test_opens_paused(self):
        self.clock.advance(120); self.model.tick()
        self.assertFalse(self.model.running)
        self.assertEqual(self.model.snapshot()["strategic_minutes"], 0)
    def test_play_rate(self):
        self.model.play(); self.clock.advance(60); self.model.tick()
        self.assertEqual(self.model.snapshot()["time"], "01:00:00")
    def test_pause_resume_discards_wait(self):
        self.model.play(); self.clock.advance(10); self.model.pause()
        self.clock.advance(500); self.model.play(); self.clock.advance(5); self.model.tick()
        self.assertEqual(self.model.snapshot()["strategic_minutes"], 15)
    def test_fractional_time_survives_pause(self):
        self.model.play(); self.clock.advance(.6); self.model.pause()
        self.clock.advance(100); self.model.play(); self.clock.advance(.6); self.model.tick()
        self.assertEqual(self.model.snapshot()["strategic_minutes"], 1)
    def test_step(self):
        self.model.step(60)
        self.assertFalse(self.model.running)
        self.assertEqual(self.model.snapshot()["strategic_minutes"], 60)
    def test_bad_steps(self):
        for value in (0, -1, True, 1.5, "1"):
            with self.assertRaises(ValueError): self.model.step(value)
        self.model.play()
        with self.assertRaises(ValueError): self.model.step(1)
    def test_reset(self):
        self.model.metrics["PREPAREDNESS"] = 999
        self.model.available_evidence = 1
        self.model.play(); self.clock.advance(99); self.model.tick(); self.model.reset()
        state = self.model.snapshot()
        self.assertFalse(state["running"])
        self.assertEqual((state["strategic_minutes"], state["available_evidence"], state["metrics"]["PREPAREDNESS"]), (0, 900, 300))
    def test_initial_state(self):
        state = self.model.snapshot()
        self.assertEqual((state["date"], state["time"], state["day"]), ("1992-02-01", "00:00:00", 1))
        self.assertEqual(state["available_evidence"], state["lifetime_evidence"])
        self.assertIsNone(state["department_funding"])
    def test_day_rollover(self):
        self.model.step(1440)
        self.assertEqual(self.model.snapshot()["date"], "1992-02-02")
        self.assertEqual(self.model.snapshot()["day"], 2)
    def test_catalog_is_not_mutated(self):
        baseline = deepcopy(self.tables)
        self.model.metrics["PREPAREDNESS"] = 0
        self.model.step(10); self.model.reset()
        self.assertEqual(self.tables, baseline)
    def test_snapshot_is_detached_and_read_only_in_time(self):
        self.model.play(); self.clock.advance(50)
        snapshot = self.model.snapshot()
        snapshot["metrics"]["PREPAREDNESS"] = 9
        self.assertEqual(self.model.snapshot()["strategic_minutes"], 0)
        self.assertEqual(self.model.metrics["PREPAREDNESS"], 300)
    def test_reset_can_reload_defaults(self):
        updated = deepcopy(self.tables)
        updated["metrics"][0]["default_value"] = "500"
        self.model.reset(updated)
        self.assertEqual(self.model.metrics["PREPAREDNESS"], 500)

if __name__ == "__main__": unittest.main()
