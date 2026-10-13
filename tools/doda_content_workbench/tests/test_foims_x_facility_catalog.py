import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_facility_catalog import FacilityCatalog, status

class FacilityCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tables = {
            "facilities": [
                {"facility_id": "F", "display_name": "Laboratory",
                 "personnel_capacity": "10", "active": "true", "sort_order": "20"},
                {"facility_id": "G", "display_name": "Draft Office",
                 "active": "false", "sort_order": "10"}
            ],
            "capabilities": [
                {"capability_id": "C", "display_name": "Analysis", "active": "true"}
            ],
            "facility_capabilities": [
                {"facility_id": "F", "capability_id": "C",
                 "display_name_override": "Local Analysis",
                 "active": "true", "max_concurrent_personnel": "4"}
            ],
            "capability_staffing_rules": [
                {"capability_id": "C", "qualification_id": "Q",
                 "min_contributors": "1", "preferred_contributors": "2",
                 "max_contributors": "3", "active": "true"}
            ],
            "facility_capability_staffing_overrides": [
                {"facility_id": "F", "capability_id": "C", "qualification_id": "Q",
                 "min_contributors": "2", "preferred_contributors": "3",
                 "max_contributors": "4", "active": "false"}
            ],
            "qualification_catalog": [
                {"qualification_id": "Q", "display_name": "Analyst", "active": "true"}
            ],
        }
        self.catalog = FacilityCatalog(self.tables)

    def description(self):
        return "\n".join(self.catalog.describe("F"))

    def test_facilities_sorted(self):
        self.assertEqual(
            [r["facility_id"] for r in self.catalog.facilities()], ["G", "F"]
        )

    def test_drafts_are_visible(self):
        self.assertEqual(status(self.catalog.facilities()[0]), "DRAFT")

    def test_facility_fields_displayed(self):
        self.assertIn("personnel capacity: 10", self.description())

    def test_capability_override_name(self):
        self.assertIn("Local Analysis / C", self.description())

    def test_staffing_baseline(self):
        self.assertIn("GLOBAL STAFFING BASELINES", self.description())
        self.assertIn("1/2/3", self.description())

    def test_override_separate_and_labeled(self):
        self.assertIn("FACILITY-SPECIFIC OVERRIDES", self.description())
        self.assertIn("2/3/4", self.description())
        self.assertIn("Analyst / Q [DRAFT]", self.description())

    def test_missing_reference_explicit(self):
        self.tables["capabilities"] = []
        text = "\n".join(FacilityCatalog(self.tables).describe("F"))
        self.assertIn("MISSING OR DUPLICATE", text)

    def test_no_links_explicit(self):
        self.assertIn(
            "No capability links authored",
            "\n".join(self.catalog.describe("G"))
        )

    def test_unknown_facility(self):
        self.assertIn("no longer present", self.catalog.describe("UNKNOWN")[0])

    def test_catalog_and_returns_detached(self):
        baseline = deepcopy(self.tables)
        self.catalog.facilities()[0]["active"] = "true"
        self.catalog.describe("F")
        self.catalog.pages("F")
        self.assertEqual(self.tables, baseline)
        self.tables["facilities"][0]["display_name"] = "New"
        self.assertIn("Laboratory", self.description())

    def test_pagination_preserves_details(self):
        pages = self.catalog.pages("F", width=52, page_size=3)
        self.assertGreater(len(pages), 1)
        self.assertTrue(all(len(page) <= 3 for page in pages))
        self.assertTrue(all(len(line) <= 52 for page in pages for line in page))

    def test_duplicates_and_empty_catalog(self):
        self.tables["facilities"].append(dict(self.tables["facilities"][0]))
        self.assertIn(
            "Duplicate", FacilityCatalog(self.tables).describe("F")[0]
        )
        self.assertEqual(FacilityCatalog({}).facilities(), [])

if __name__ == "__main__":
    unittest.main()
