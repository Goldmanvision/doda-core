import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import test_recreation_content_rules as rcbase
import test_recreation_effect_scales as es

UNIT = "PERCENT_OF_INTOXICATION_RANGE"


def intox_levels():
    return [rcbase._lv("INTOXICATION_GAIN", lid, name, es.PERCENTS[i], UNIT, (i + 1) * 10)
            for i, (lid, name) in enumerate(rcbase.NAMES)]


class IntoxicationScaleTests(unittest.TestCase):
    setUp = es.EffectScaleTests.setUp
    tearDown = es.EffectScaleTests.tearDown
    validate = es.EffectScaleTests.validate

    def test_valid_and_scaled(self):
        res, data = self.validate(rcbase.base_levels() + intox_levels())
        self.assertEqual(res.errors, [])
        gain = {l["levelId"]: l for l in data["effectLevels"] if l["scaleId"] == "INTOXICATION_GAIN"}
        self.assertEqual(gain["LOW"]["valueScaled"], 200000)

    def test_over_100(self):
        rows = rcbase.patch(rcbase.base_levels() + intox_levels(), None, ("INTOXICATION_GAIN", "FULL"), value="101")
        res, _ = self.validate(rows)
        self.assertTrue(any("at most 100" in e for e in res.errors))

    def test_wrong_unit(self):
        rows = rcbase.patch(rcbase.base_levels() + intox_levels(), None, ("INTOXICATION_GAIN", "LOW"),
                            unit="PER_STRATEGIC_MINUTE")
        res, _ = self.validate(rows)
        self.assertTrue(any("must use unit PERCENT_OF_INTOXICATION_RANGE" in e for e in res.errors))

    def test_zero_rejected(self):
        rows = rcbase.patch(rcbase.base_levels() + intox_levels(), None, ("INTOXICATION_GAIN", "MINIMAL"), value="0")
        res, _ = self.validate(rows)
        self.assertTrue(any("above 0" in e for e in res.errors))


if __name__ == "__main__":
    unittest.main()