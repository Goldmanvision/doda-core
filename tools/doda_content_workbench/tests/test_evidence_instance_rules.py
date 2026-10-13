import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources
import doda_evidence_instance_rules as evidence


class EvidenceInstanceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.resource_active = "true"
        self.columns = evidence.COLUMNS
        self.rows = [dict(zip(evidence.COLUMNS, (
            "EVI_NOTE", "Note", "EVIDENCE_PAPER", "1", "1", "Test.", "10", "true",
        )))]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self):
        self.write(resources.RESOURCES_FILE, resources.RESOURCE_COLUMNS, [
            dict(zip(resources.RESOURCE_COLUMNS, (
                "EVIDENCE_PAPER", "Paper", "Test.", "STOCKPILE",
                "false", "10", self.resource_active,
            )))
        ])
        self.write(evidence.INSTANCES_FILE, self.columns, self.rows)
        result = net.Result()
        data = evidence.validate_instances(self.root, result)
        return result, data

    def test_fixed_value(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(data["definitions"][0]["baseValueMin"], 1)
        self.assertEqual(data["definitions"][0]["baseValueMax"], 1)

    def test_editable_range(self):
        self.rows[0].update(base_value_min="4", base_value_max="6")
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(data["definitions"][0]["baseValueMax"], 6)

    def test_reversed_range(self):
        self.rows[0].update(base_value_min="6", base_value_max="4")
        self.assertFalse(self.validate()[0].valid)

    def test_invalid_bounds(self):
        for field in ("base_value_min", "base_value_max"):
            for raw in ("", "-1", "1.5", "NaN", "1e2"):
                with self.subTest(field=field, raw=raw):
                    old = self.rows[0][field]
                    self.rows[0][field] = raw
                    self.assertFalse(self.validate()[0].valid)
                    self.rows[0][field] = old

    def test_duplicate_and_invalid_id(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)
        self.rows.pop()
        self.rows[0]["evidence_instance_id"] = "bad id"
        self.assertFalse(self.validate()[0].valid)

    def test_resource_reference(self):
        for rid in ("MISSING", "ADMISSIBLE_EVIDENCE", "LEADS"):
            with self.subTest(rid=rid):
                self.rows[0]["evidence_resource_id"] = rid
                self.assertFalse(self.validate()[0].valid)

    def test_active_parent(self):
        self.resource_active = "false"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["active"] = "false"
        self.assertTrue(self.validate()[0].valid)

    def test_text_boolean_sort(self):
        for field, raw in (
            ("display_name", ""), ("description", ""),
            ("active", "maybe"), ("sort_order", "-1"),
        ):
            with self.subTest(field=field):
                old = self.rows[0][field]
                self.rows[0][field] = raw
                self.assertFalse(self.validate()[0].valid)
                self.rows[0][field] = old

    def test_missing_header(self):
        self.columns = evidence.COLUMNS[:-1]
        self.rows[0].pop("active")
        self.assertFalse(self.validate()[0].valid)

    def test_export_failure_preserves(self):
        self.validate()
        result, path = evidence.export(self.root)
        self.assertTrue(result.valid, result.errors)
        old = path.read_bytes()
        payload = json.loads(old)
        self.assertFalse(payload["runtimeImplemented"])
        self.assertTrue(payload["rules"]["exportSamplesNoValues"])
        self.rows[0]["base_value_max"] = "-1"
        self.validate()
        result, failed = evidence.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)
