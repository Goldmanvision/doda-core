"""Registry/metadata consistency tests (no GUI)."""
import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import doda_page_registry as reg

TAB_TEXTS = ["Dashboard", "Department Tracks — Editor", "Metrics — Editor", "Metric Tiers — Editor",
             "Facilities — Editor", "Flavor Text — Editor", "Qualifications — Editor", "Capabilities — Editor",
             "Facility Capabilities — Editor", "Capability Staffing Rules — Editor",
             "Facility Staffing Overrides — Editor", "Task Templates — Editor", "Activity Log",
             "Enum Catalog — Admin", "Network Tiers — Editor", "Modems and Routers — Editor",
             "Transfer and Interruption Rules — Reference", "Equipment Families — Editor", "Equipment Models — Editor",
             "Care Services — Editor", "Care Locations — Editor", "Care Service Locations — Editor",
             "Condition Stats — Editor", "Condition Bands — Editor"]

class T(unittest.TestCase):
    def test_registry_consistent(self):
        self.assertEqual(reg.check_registry(), [])
    def test_every_known_tab_maps_uniquely(self):
        ids = [reg.page_for_tab_text(t).page_id for t in TAB_TEXTS]
        self.assertEqual(len(ids), len(set(ids)))
    def test_longest_prefix(self):
        self.assertEqual(reg.page_for_tab_text("Facility Capabilities — Editor").page_id, "facility_capabilities")
        self.assertEqual(reg.page_for_tab_text("Facilities — Editor").page_id, "facilities")
        self.assertEqual(reg.page_for_tab_text("Metric Tiers — Editor").page_id, "metric_tiers")
    def test_unknown_tab(self):
        self.assertIsNone(reg.page_for_tab_text("Something New"))

if __name__ == "__main__": unittest.main()
