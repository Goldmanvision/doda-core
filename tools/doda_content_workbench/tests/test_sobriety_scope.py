import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_sobriety_rules as sob


class SobrietyScopeTests(unittest.TestCase):
    def test_multiplier_applies_to_all_skills_and_attributes(self):
        self.assertEqual(sob.RULES["skills"]["appliesTo"], "ALL_SKILLS_AND_ATTRIBUTES")

    def test_open_item_is_narrowed(self):
        self.assertIn("applies to all skills and attributes", sob.OPEN_ITEMS["SOBR-OPEN-01"])


if __name__ == "__main__":
    unittest.main()