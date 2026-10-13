import csv
import unittest
from pathlib import Path


class EvidenceGatheringSourceTests(unittest.TestCase):
    def rows(self):
        root = Path(__file__).resolve().parents[3]
        with (root / "data_authoring/source/task_template_flows.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            return list(csv.DictReader(handle))

    def test_field_surveillance_output_categories(self):
        rows = [
            row for row in self.rows()
            if row["task_template_id"] == "FIELD_SURVEILLANCE"
            and row["direction"] == "OUT"
        ]
        self.assertEqual(len(rows), 3)
        self.assertEqual(
            {row["resource_id"] for row in rows},
            {"EVIDENCE_PHOTOGRAPHIC", "EVIDENCE_AUDIO", "EVIDENCE_VIDEO"},
        )
        self.assertTrue(all(row["flow_mode"] == "WEIGHTED" for row in rows))

    def test_investigate_has_physical_evidence_choice(self):
        rows = [
            row for row in self.rows()
            if row["task_template_id"] == "INVESTIGATE"
            and row["direction"] == "OUT"
            and row["resource_id"] == "EVIDENCE_PHYSICAL"
        ]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["flow_mode"], "WEIGHTED")
