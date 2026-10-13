import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_reference_catalog import TaskCatalog, QualificationCatalog

class ReferenceCatalogTests(unittest.TestCase):
    def setUp(self):
        self.tables = {
            "task_templates": [
                {"task_template_id": "T", "display_name": "Signal Review",
                 "capability_id": "C", "default_target_effort_minutes": "240",
                 "default_deadline_minutes": "120", "auto_allocate": "true",
                 "active": "true", "sort_order": "20"},
                {"task_template_id": "D", "display_name": "Draft Task",
                 "capability_id": "C", "active": "false", "sort_order": "10"}
            ],
            "capabilities": [
                {"capability_id": "C", "display_name": "Analysis", "active": "true"}
            ],
            "qualification_catalog": [
                {"qualification_id": "Q", "display_name": "Analyst",
                 "description": "Interprets signals.", "active": "true"},
                {"qualification_id": "R", "display_name": "Other",
                 "active": "false"}
            ],
            "capability_staffing_rules": [
                {"capability_id": "C", "qualification_id": "Q",
                 "min_contributors": "1", "preferred_contributors": "2",
                 "max_contributors": "3", "active": "true"}
            ],
            "facilities": [
                {"facility_id": "F", "display_name": "Lab", "active": "true"}
            ],
            "facility_capabilities": [
                {"facility_id": "F", "capability_id": "C", "active": "true"}
            ],
            "facility_capability_staffing_overrides": [
                {"facility_id": "F", "capability_id": "C", "qualification_id": "Q",
                 "min_contributors": "2", "preferred_contributors": "3",
                 "max_contributors": "4", "active": "false"}
            ],
        }

    def task(self):
        return "\n".join(TaskCatalog(self.tables).describe("T"))

    def qualification(self):
        return "\n".join(QualificationCatalog(self.tables).describe("Q"))

    def test_task_order_and_drafts(self):
        rows = TaskCatalog(self.tables).facilities()
        self.assertEqual([r["facility_id"] for r in rows], ["D", "T"])
        self.assertEqual(rows[0]["active"], "false")

    def test_effort_and_deadline_separate(self):
        self.assertIn("default target effort minutes: 240", self.task())
        self.assertIn("default deadline minutes: 120", self.task())

    def test_capability_reference(self):
        self.assertIn("Analysis / C [ACTIVE]", self.task())

    def test_qualification_via_staffing(self):
        self.assertIn("QUALIFICATIONS VIA GLOBAL STAFFING RULES", self.task())
        self.assertIn("Analyst / Q [ACTIVE]", self.task())
        self.assertIn("1/2/3", self.task())

    def test_facility_link_is_not_readiness(self):
        self.assertIn("Lab / F [ACTIVE]", self.task())
        self.assertIn("do not prove construction", self.task())

    def test_missing_reference_explicit(self):
        self.tables["capabilities"] = []
        self.assertIn("C [MISSING OR DUPLICATE]", self.task())

    def test_qualification_definition(self):
        self.assertIn("Interprets signals.", self.qualification())

    def test_qualification_reverse_references(self):
        text = self.qualification()
        self.assertIn("Signal Review / T", text)
        self.assertIn("Draft Task / D [DRAFT]", text)

    def test_overrides_separate(self):
        text = self.qualification()
        self.assertIn("GLOBAL CAPABILITY STAFFING REFERENCES", text)
        self.assertIn("FACILITY-SPECIFIC STAFFING OVERRIDES", text)
        self.assertIn("2/3/4 [DRAFT]", text)

    def test_empty_and_duplicate(self):
        self.assertEqual(TaskCatalog({}).facilities(), [])
        self.assertIn(
            "missing", QualificationCatalog({}).describe("Q")[0].lower()
        )
        self.tables["task_templates"].append(dict(self.tables["task_templates"][0]))
        self.assertIn("duplicated", self.task())

    def test_pages_preserve_content(self):
        pages = TaskCatalog(self.tables).pages("T", width=52, page_size=3)
        self.assertGreater(len(pages), 1)
        self.assertTrue(all(len(page) <= 3 for page in pages))
        self.assertTrue(all(len(line) <= 52 for page in pages for line in page))

    def test_read_only_detached(self):
        before = deepcopy(self.tables)
        catalog = TaskCatalog(self.tables)
        catalog.facilities()[0]["display_name"] = "Changed"
        catalog.describe("T")
        catalog.pages("T")
        self.assertEqual(self.tables, before)

if __name__ == "__main__":
    unittest.main()
