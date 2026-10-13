import sys
import unittest
from copy import deepcopy
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from doda_foims_x_personnel_catalog import PersonnelCatalog
from doda_foims_x_roster import SandboxRoster, AVAILABLE, UNAVAILABLE

def tables():
    return {
        "qualification_catalog": [
            {"qualification_id": q, "display_name": q.title(), "active": "TRUE"}
            for q in ("SIGNALS_ANALYSIS", "DATA_SYSTEMS",
                      "FIELD_RESPONSE", "OCCULT_RESPONSE")
        ],
        "capabilities": [
            {"capability_id": "ANALYSIS", "display_name": "Analysis", "active": "TRUE"}
        ],
        "capability_staffing_rules": [
            {"capability_id": "ANALYSIS", "qualification_id": "SIGNALS_ANALYSIS",
             "min_contributors": "1", "preferred_contributors": "2",
             "max_contributors": "3", "active": "TRUE"}
        ],
        "task_templates": [
            {"task_template_id": "SIGNAL_REVIEW", "display_name": "Signal Review",
             "capability_id": "ANALYSIS", "active": "TRUE", "sort_order": "10"}
        ],
    }

def build(t=None):
    t = t or tables()
    roster = SandboxRoster(t)
    return t, roster, PersonnelCatalog(t, roster)

class PersonnelCatalogTests(unittest.TestCase):
    def test_rows_show_availability(self):
        _, _, catalog = build()
        rows = {r["facility_id"]: r["display_name"] for r in catalog.facilities()}
        self.assertEqual(list(rows), ["AGENT_001", "AGENT_002", "AGENT_003", "AGENT_004"])
        self.assertTrue(rows["AGENT_001"].endswith("AVAIL"))
        self.assertTrue(rows["AGENT_004"].endswith("OFF"))

    def test_describe_roles_and_tasks(self):
        _, _, catalog = build()
        text = "\n".join(catalog.describe("AGENT_001"))
        self.assertIn("Signals_Analysis / SIGNALS_ANALYSIS [ACTIVE]", text)
        self.assertIn("Analysis / ANALYSIS [ACTIVE]", text)
        self.assertIn("1/2/3", text)
        self.assertIn("Signal Review / SIGNAL_REVIEW", text)
        self.assertIn("not an assignment", text)

    def test_toggle_is_live(self):
        _, roster, catalog = build()
        roster.set_availability("AGENT_001", UNAVAILABLE)
        self.assertIn("Availability: UNAVAILABLE", "\n".join(catalog.describe("AGENT_001")))
        self.assertTrue(catalog.facilities()[0]["display_name"].endswith("OFF"))

    def test_missing_qualification_reported(self):
        t = tables()
        t["qualification_catalog"] = t["qualification_catalog"][1:]
        _, _, catalog = build(t)
        text = "\n".join(catalog.describe("AGENT_001"))
        self.assertIn("MISSING OR DUPLICATE", text)
        self.assertIn("AUDIT", text)

    def test_unknown_agent(self):
        _, _, catalog = build()
        self.assertIn("missing", catalog.describe("NOPE")[0].lower())

    def test_tables_follow_refresh(self):
        t, roster, _ = build()
        fresh = deepcopy(t)
        fresh["qualification_catalog"] = []
        PersonnelCatalog(fresh, roster)
        self.assertIs(roster.tables, fresh)
        self.assertTrue(roster.audit())

    def test_read_only_and_pages(self):
        t, roster, catalog = build()
        before = deepcopy(t)
        pages = catalog.pages("AGENT_001", width=52, page_size=3)
        self.assertGreater(len(pages), 1)
        self.assertTrue(all(len(p) <= 3 for p in pages))
        self.assertTrue(all(len(line) <= 52 for p in pages for line in p))
        self.assertEqual(t, before)
        self.assertEqual(roster.get("AGENT_004").availability, UNAVAILABLE)

if __name__ == "__main__":
    unittest.main()
