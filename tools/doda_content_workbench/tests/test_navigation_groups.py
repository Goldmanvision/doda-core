import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_page_registry as reg


class NavigationGroupTests(unittest.TestCase):
    def test_every_personnel_page_has_a_subgroup(self):
        missing = [p.page_id for p in reg.PAGES if p.group == "Personnel and Care" and not p.subgroup]
        self.assertEqual(missing, [])

    def test_subgroup_mapping_has_no_unknown_pages(self):
        ids = {p.page_id for p in reg.PAGES}
        self.assertEqual([k for k in reg.PAGE_SUBGROUPS if k not in ids], [])


if __name__ == "__main__":
    unittest.main()