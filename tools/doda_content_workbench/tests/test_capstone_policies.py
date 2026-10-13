import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import doda_territory_rules as terr
import test_territory_rules as base


class CapstonePolicyTests(unittest.TestCase):
    setUp = base.TerritoryTests.setUp
    tearDown = base.TerritoryTests.tearDown
    make_root = base.TerritoryTests.make_root
    validate = base.TerritoryTests.validate

    def test_special_purchase_does_not_raise_ordinary_price(self):
        capstone = terr.RULES["missionProgression"]["capstone"]
        self.assertIs(capstone["advancesOrdinaryPurchaseCounter"], False)

    def test_purchase_latches_eligibility(self):
        rules = terr.RULES["missionProgression"]
        self.assertIs(rules["capstone"]["eligibilityRechecksAfterPurchase"], False)
        self.assertTrue(rules["capstone"]["offerRequiresAllFinalGateRequirements"])
        self.assertTrue(rules["capstone"]["unlockIsPermanent"])

    def test_resolved_policies_absent_from_export_blockers(self):
        import json
        result, output = terr.export(self.make_root())
        self.assertTrue(result.valid, result.errors)
        payload = json.loads(output.read_text(encoding="utf-8"))
        missing = payload["missionProgression"]["finalGate"]["missingConfiguration"]
        self.assertNotIn("CAPSTONE_PURCHASE_COUNTER_POLICY", missing)
        self.assertNotIn("POST_PURCHASE_ELIGIBILITY_RECHECK_POLICY", missing)
        self.assertIn("REQUIRED_UPGRADE_REFERENCES", missing)
        self.assertFalse(payload["missionProgression"]["finalGate"]["configured"])
        capstone = payload["rules"]["missionProgression"]["capstone"]
        self.assertIs(capstone["advancesOrdinaryPurchaseCounter"], False)
        self.assertIs(capstone["eligibilityRechecksAfterPurchase"], False)
        self.assertFalse(payload["runtimeImplemented"])


if __name__ == "__main__":
    unittest.main()
