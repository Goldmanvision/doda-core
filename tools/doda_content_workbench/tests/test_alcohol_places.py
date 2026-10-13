import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_personal_care_effects as eff
import test_personal_care_rules as base
import test_recreation_content_rules as rcbase
import test_recreation_effect_scales as es

NUTR = "PERCENT_OF_NUTRITION_RANGE"


def loss_levels():
    return [rcbase._lv("HUNGER_LOSS", lid, name, es.PERCENTS[i], NUTR, (i + 1) * 10)
            for i, (lid, name) in enumerate(rcbase.NAMES)]


class HungerLossScaleTests(unittest.TestCase):
    setUp = es.EffectScaleTests.setUp
    tearDown = es.EffectScaleTests.tearDown
    validate = es.EffectScaleTests.validate

    def test_valid_and_scaled(self):
        res, data = self.validate(rcbase.base_levels() + loss_levels())
        self.assertEqual(res.errors, [])
        loss = {l["levelId"]: l for l in data["effectLevels"] if l["scaleId"] == "HUNGER_LOSS"}
        self.assertEqual(loss["LOW"]["valueScaled"], 200000)

    def test_over_100(self):
        rows = rcbase.patch(rcbase.base_levels() + loss_levels(), None, ("HUNGER_LOSS", "FULL"), value="101")
        res, _ = self.validate(rows)
        self.assertTrue(any("at most 100" in e for e in res.errors))

    def test_wrong_unit(self):
        rows = rcbase.patch(rcbase.base_levels() + loss_levels(), None, ("HUNGER_LOSS", "LOW"),
                            unit="PER_STRATEGIC_MINUTE")
        res, _ = self.validate(rows)
        self.assertTrue(any("must use unit PERCENT_OF_NUTRITION_RANGE" in e for e in res.errors))


LEVELS = (eff.LEVELS_HEADER
          + "INTOXICATION_GAIN,LOW,Low,15,PERCENT_OF_INTOXICATION_RANGE,,,30,false\n"
          + "HUNGER_LOSS,LOW,Low,10,PERCENT_OF_NUTRITION_RANGE,,,30,false\n")
FEATURES = base.FOOD + "CAP_ALCOHOL,Alcohol Service,,,40,true\n"
LINKS = base.PF + "PLACE_SAFE_HOUSE,CAP_ALCOHOL,30,true\n"


class AlcoholPlaceTests(unittest.TestCase):
    run_rows = base.T.run_rows
    has = base.T.has

    def setUp(self):
        self.dirs = []

    def tearDown(self):
        import shutil
        for d in self.dirs:
            shutil.rmtree(d, ignore_errors=True)

    def check(self, row, links=LINKS):
        return self.run_rows(activities=row, features=FEATURES, place_features=links,
                             extra={"effect_levels.csv": LEVELS})

    def test_alcohol_activity_allowed_at_alcohol_place(self):
        r, _ = self.check(eff.act_row(place_type_id="PLACE_SAFE_HOUSE", intoxication_gain_level_id="LOW",
                                      off_duty_only="true"))
        self.assertTrue(r.valid, r.errors)

    def test_alcohol_activity_needs_alcohol_feature(self):
        r, _ = self.check(eff.act_row(place_type_id="PLACE_SAFE_HOUSE", intoxication_gain_level_id="LOW",
                                      off_duty_only="true"), links=base.PF)
        self.assertTrue(self.has(r, "does not offer CAP_RECREATION"))

    def test_non_alcohol_activity_still_needs_recreation(self):
        r, _ = self.check(eff.act_row(place_type_id="PLACE_SAFE_HOUSE"))
        self.assertTrue(self.has(r, "does not offer CAP_RECREATION"))

    def test_hunger_loss_level_checked(self):
        r, data = self.check(eff.act_row(hunger_loss_level_id="LOW"))
        self.assertTrue(r.valid, r.errors)
        self.assertEqual(data["recreationActivities"][0]["hungerLossLevelId"], "LOW")
        r, _ = self.check(eff.act_row(hunger_loss_level_id="NOPE"))
        self.assertTrue(self.has(r, "is not a level of scale HUNGER_LOSS"))


if __name__ == "__main__":
    unittest.main()