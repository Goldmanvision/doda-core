import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_personal_care_rules as base

LEVELS_HEADER = "scale_id,level_id,display_name,value,unit,source_reference,description,sort_order,active\n"
LEVELS = (LEVELS_HEADER
          + "FATIGUE_COST,LOW,Low,0.1,PER_STRATEGIC_MINUTE,,,30,false\n"
          + "FATIGUE_COST,HIGH,High,0.35,PER_STRATEGIC_MINUTE,,,50,false\n"
          + "STRESS_REDUCTION,LOW,Low,0.2,PER_STRATEGIC_MINUTE,,,30,false\n"
          + "STRESS_GAIN,LOW,Low,10,PERCENT_OF_STRESS_RANGE,,,30,false\n"
          + "ENERGY_RESTORE,LOW,Low,20,PERCENT_OF_ENERGY_RANGE,,,30,false\n")


def act_row(**kw):
    cols = base.pc.ACTIVITY_COLUMNS
    vals = {c: "" for c in cols}
    vals.update(activity_id="REC_T", place_type_id="PLACE_GYM", display_name="Test", duration_minutes="60",
                company_options="ALONE", energy_required_to_start="40", sort_order="10", active="true")
    vals.update(kw)
    return ",".join(vals[c] for c in cols) + "\n"


class EffectTests(unittest.TestCase):
    run_rows = base.T.run_rows
    has = base.T.has

    def setUp(self):
        self.dirs = []

    def tearDown(self):
        import shutil
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def check(self, row, **kw):
        extra = {"effect_levels.csv": LEVELS}
        extra.update(kw.pop("extra", {}))
        return self.run_rows(activities=row, extra=extra)

    def test_energy_rule_error(self):
        r, _ = self.check(act_row(fatigue_cost_level_id="HIGH", energy_required_to_start="10"))
        self.assertTrue(self.has(r, "must be at least the fatigue this activity uses"))

    def test_energy_rule_passes_when_covered(self):
        r, _ = self.check(act_row(fatigue_cost_level_id="HIGH", energy_required_to_start="21"))
        self.assertTrue(r.valid, r.errors)

    def test_energy_blank_counts_as_zero(self):
        r, _ = self.check(act_row(fatigue_cost_level_id="LOW", energy_required_to_start=""))
        self.assertTrue(self.has(r, "must be at least the fatigue this activity uses"))

    def test_variable_length_uses_longest(self):
        row = dict(duration_minutes="20", duration_step_minutes="20", duration_max_minutes="300",
                   fatigue_cost_level_id="LOW")
        r, _ = self.check(act_row(energy_required_to_start="10", **row))
        self.assertTrue(self.has(r, "must be at least the fatigue this activity uses"))
        r, _ = self.check(act_row(energy_required_to_start="30", **row))
        self.assertTrue(r.valid, r.errors)

    def test_vacation_warning_and_export_flag(self):
        rows = (act_row(activity_id="REC_VAC", duration_minutes="2880", fatigue_cost_level_id="LOW",
                        energy_required_to_start="", sort_order="10")
                + act_row(activity_id="REC_DAY", duration_minutes="60", sort_order="20"))
        r, data = self.check(rows)
        self.assertTrue(r.valid, r.errors)
        self.assertTrue(any("vacation" in w for w in r.warnings))
        acts = {a["activityId"]: a for a in data["recreationActivities"]}
        self.assertTrue(acts["REC_VAC"]["vacation"])
        self.assertFalse(acts["REC_DAY"]["vacation"])

    def test_stress_gain_delay_valid_and_exported(self):
        r, data = self.check(act_row(stress_gain_level_id="LOW", stress_gain_delay_min_minutes="120",
                                     stress_gain_delay_max_minutes="240"))
        self.assertTrue(r.valid, r.errors)
        a = data["recreationActivities"][0]
        self.assertEqual(a["stressGainLevelId"], "LOW")
        self.assertEqual(a["stressGainDelayMinMinutes"], 120)
        self.assertEqual(a["stressGainDelayMaxMinutes"], 240)

    def test_stress_gain_delay_errors(self):
        r, _ = self.check(act_row(stress_gain_level_id="LOW", stress_gain_delay_min_minutes="120"))
        self.assertTrue(self.has(r, "must be set together"))
        r, _ = self.check(act_row(stress_gain_delay_min_minutes="120", stress_gain_delay_max_minutes="240"))
        self.assertTrue(self.has(r, "needs stress_gain_level_id"))
        r, _ = self.check(act_row(stress_gain_level_id="LOW", stress_gain_delay_min_minutes="240",
                                  stress_gain_delay_max_minutes="120"))
        self.assertTrue(self.has(r, "0 <= minimum <= maximum"))
        tick5 = {"time_settings.csv": "setting_id,value\nSIM_TICK_STRATEGIC_MINUTES,5\n"}
        r, _ = self.check(act_row(stress_gain_level_id="LOW", stress_gain_delay_min_minutes="122",
                                  stress_gain_delay_max_minutes="240"), extra=tick5)
        self.assertTrue(self.has(r, "multiple of the sim tick (5 minutes)"))

    def test_unknown_energy_restore_level(self):
        r, _ = self.check(act_row(energy_restore_level_id="NOPE"))
        self.assertTrue(self.has(r, "is not a level of scale ENERGY_RESTORE"))


if __name__ == "__main__":
    unittest.main()