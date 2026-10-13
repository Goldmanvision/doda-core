import csv
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)


class RoswellSpellingTests(unittest.TestCase):
    def test_no_misspelling_in_source_data(self):
        for path in sorted((ROOT / "data_authoring/source").glob("*.csv")):
            with self.subTest(file=path.name):
                self.assertNotIn("Rosewell", path.read_text(encoding="utf-8-sig"))

    def test_real_data_has_no_hq_naming_warnings(self):
        result = net.Result()
        terr.validate_territory(ROOT, result)
        self.assertTrue(result.valid, result.errors)
        self.assertFalse(any("does not follow" in warning for warning in result.warnings))


if __name__ == "__main__":
    unittest.main()
