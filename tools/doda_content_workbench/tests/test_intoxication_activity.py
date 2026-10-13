import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_personal_care_effects as eff
import test_personal_care_rules as base

LEVELS = eff.LEVELS_HEADER + "INTOXICATION_GAIN,LOW,Low,15,PERCENT_OF_INTOXICATION_RANGE,,,30,false\n"


class IntoxicationActivityTests(unittest.TestCase):
    run_rows = base.T.run_rows
    has = base.T.has

    def setUp(self):
        self.dirs = []

    def tearDown(self):
        import shutil
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def check(self, row):
        return self.run_rows(activities=row, extra={"effect_levels.csv": LEVELS})

    def test_valid_and_exported(self):
        r, data = self.check(eff.act_row(intoxication_gain_level_id="LOW", off_duty_only="true"))
        self.assertTrue(r.valid, r.errors)
        a = data["recreationActivities"][0]
        self.assertEqual(a["intoxicationGainLevelId"], "LOW")
        self.assertTrue(a["offDutyOnly"])

    def test_defaults_when_blank(self):
        r, data = self.check(eff.act_row())
        self.assertTrue(r.valid, r.errors)
        a = data["recreationActivities"][0]
        self.assertIsNone(a["intoxicationGainLevelId"])
        self.assertFalse(a["offDutyOnly"])

    def test_gain_requires_off_duty_only(self):
        r, _ = self.check(eff.act_row(intoxication_gain_level_id="LOW"))
        self.assertTrue(self.has(r, "must set off_duty_only to true"))

    def test_unknown_level(self):
        r, _ = self.check(eff.act_row(intoxication_gain_level_id="NOPE", off_duty_only="true"))
        self.assertTrue(self.has(r, "is not a level of scale INTOXICATION_GAIN"))

    def test_bad_flag(self):
        r, _ = self.check(eff.act_row(off_duty_only="maybe"))
        self.assertTrue(self.has(r, "off_duty_only must be true or false"))

    def test_vacation_warning(self):
        r, _ = self.check(eff.act_row(duration_minutes="2880", energy_required_to_start="",
                                      intoxication_gain_level_id="LOW", off_duty_only="true"))
        self.assertTrue(r.valid, r.errors)
        self.assertTrue(any("intoxication gain is ignored" in w for w in r.warnings))


if __name__ == "__main__":
    unittest.main()