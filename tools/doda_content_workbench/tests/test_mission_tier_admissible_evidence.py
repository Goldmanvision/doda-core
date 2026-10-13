import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT / "tools" / "doda_content_workbench"
OLD = "min_lifetime" + "_evidence"
NEW = "min_lifetime_admissible_evidence"

class MissionTierAdmissibleEvidenceTests(unittest.TestCase):
    def test_source_csv_header_uses_new_column(self):
        headers = []
        for path in (ROOT / "data_authoring" / "source").glob("*.csv"):
            first = path.read_text(encoding="utf-8-sig").splitlines()[:1]
            if first and NEW in first[0].split(","):
                headers.append(path.name)
        self.assertEqual(len(headers), 1)

    def test_no_stale_identifier_in_code(self):
        stale = []
        for path in list(WORK.glob("*.py")) + list((WORK / "tests").glob("*.py")):
            if OLD in path.read_text(encoding="utf-8-sig"):
                stale.append(path.name)
        self.assertEqual(stale, [])

if __name__ == "__main__":
    unittest.main()
