import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_condition_rules as cond
import doda_network_rules as net
import doda_personal_care_rules as pc
import doda_recreation_content_rules as rc
import doda_sobriety_rules as sob

ROOT = net.find_project_root(Path(__file__).resolve().parent)


class ShippedDataTests(unittest.TestCase):
    def check(self, fn):
        res = net.Result()
        fn(ROOT, res)
        self.assertEqual(res.errors, [])

    def test_personal_care(self):
        self.check(pc.validate_personal_care)

    def test_recreation_content(self):
        self.check(rc.validate_recreation_content)

    def test_sobriety(self):
        self.check(sob.validate_sobriety)

    def test_conditions(self):
        self.check(cond.validate_conditions)


if __name__ == "__main__":
    unittest.main()