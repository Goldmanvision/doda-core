import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_sandbox import FoimsXSandbox

class Clock:
    def __init__(self):
        self.now = 0.0
    def __call__(self):
        return self.now

class FoimsXEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.clock = Clock()
        self.tables = {
            "metrics": [{
                "metric_id": "PREPAREDNESS", "default_value": "300",
                "internal_min": "0", "internal_max": "1000", "active": "true"
            }],
            "territory_settings": [{
                "setting_id": "STARTING_EVIDENCE", "value": "900", "active": "true"
            }],
            "mission_tiers": [
                {"tier_id": "TIER_1", "min_lifetime_admissible_evidence": "1000", "active": "false"},
                {"tier_id": "TIER_2", "min_lifetime_admissible_evidence": "10000", "active": "false"},
            ],
        }
        self.model = FoimsXSandbox(self.tables, self.clock)

    def test_gather_increases_both(self):
        self.model.gather_evidence("100")
        self.assertEqual(
            (self.model.available_evidence, self.model.lifetime_evidence),
            (1000, 1000)
        )

    def test_spend_changes_only_available(self):
        self.model.spend_evidence(100)
        self.assertEqual(
            (self.model.available_evidence, self.model.lifetime_evidence),
            (800, 900)
        )

    def test_spend_all_is_allowed(self):
        self.model.spend_evidence(900)
        self.assertEqual(self.model.available_evidence, 0)
        self.assertEqual(self.model.lifetime_evidence, 900)

    def test_overspending_is_atomic(self):
        before = self.model.snapshot()
        with self.assertRaises(ValueError):
            self.model.spend_evidence(901)
        self.assertEqual(self.model.snapshot(), before)

    def test_invalid_amounts_are_atomic(self):
        before = self.model.snapshot()
        for value in (0, -1, True, 1.5, "NaN", "Infinity", "", "bad"):
            for method in (self.model.gather_evidence, self.model.spend_evidence):
                with self.subTest(value=value, method=method.__name__):
                    with self.assertRaises(ValueError):
                        method(value)
                    self.assertEqual(self.model.snapshot(), before)

    def test_history_includes_both_balances(self):
        self.model.step(60)
        self.model.gather_evidence(100)
        self.model.spend_evidence(50)
        events = self.model.snapshot()["activity"]
        self.assertEqual(events[0]["timestamp"], "1992-02-01 01:00:00")
        self.assertEqual(
            (events[0]["before"], events[0]["after"],
             events[0]["lifetime_before"], events[0]["lifetime_after"]),
            (900, 1000, 900, 1000)
        )
        self.assertEqual(events[1]["action"], "SPEND")
        self.assertEqual(events[1]["lifetime_after"], 1000)
        columns = self.model.activity_columns(events[1])
        self.assertIn("Life 1,000", columns[3])

    def test_shared_history_preserves_metric_events(self):
        self.model.set_metric("PREPAREDNESS", 500)
        self.model.gather_evidence(100)
        events = self.model.activity
        self.assertEqual(events[0]["metric_id"], "PREPAREDNESS")
        self.assertEqual(events[1]["metric_id"], "EVIDENCE_GATHER")
        self.assertEqual(
            self.model.activity_columns(events[0])[1:],
            ("PREPAREDNESS", "300", "500")
        )

    def test_reset_restores_both_and_clears_history(self):
        self.model.gather_evidence(100)
        self.model.spend_evidence(500)
        self.model.reset()
        self.assertEqual(
            (self.model.available_evidence, self.model.lifetime_evidence),
            (900, 900)
        )
        self.assertEqual(self.model.activity, [])
        self.assertFalse(self.model.running)

    def test_threshold_progress_does_not_unlock(self):
        progress = self.model.evidence_progress()
        self.assertEqual(progress["remaining"], 100)
        self.assertIsNone(progress["highest_evidence_threshold_met"])
        self.model.gather_evidence(100)
        progress = self.model.evidence_progress()
        self.assertEqual(
            progress["highest_evidence_threshold_met"]["tier_id"], "TIER_1"
        )
        self.assertTrue(progress["highest_evidence_threshold_met"]["draft"])
        self.assertEqual(progress["remaining"], 9000)
        self.assertFalse(progress["other_requirements_evaluated"])
        self.assertFalse(progress["unlocks_tiers"])
        self.model.spend_evidence(1000)
        self.assertEqual(self.model.evidence_progress()["remaining"], 9000)

    def test_missing_thresholds_remain_explicit(self):
        tables = deepcopy(self.tables)
        tables["mission_tiers"] = [{
            "tier_id": "TIER_1", "min_lifetime_admissible_evidence": "", "active": "false"
        }]
        self.model.reset(tables)
        progress = self.model.evidence_progress()
        self.assertEqual(progress["unconfigured_tiers"], ["TIER_1"])
        self.assertIsNone(progress["next_evidence_threshold"])
        self.assertIn("unconfigured", self.model.evidence_progress_text())

    def test_catalog_and_snapshots_are_detached(self):
        before = deepcopy(self.tables)
        self.model.gather_evidence(100)
        self.model.snapshot()["activity"][0]["lifetime_after"] = 0
        self.assertEqual(self.tables, before)
        self.assertEqual(self.model.activity[0]["lifetime_after"], 1000)

    def test_running_transaction_records_elapsed_time(self):
        self.model.play()
        self.clock.now = 15
        self.model.gather_evidence(100)
        self.assertEqual(self.model.activity[-1]["strategic_minutes"], 15)
        self.assertTrue(self.model.running)

if __name__ == "__main__":
    unittest.main()
