import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as rules
from doda_page_registry import TABLE_METADATA, page_for_tab_text

class ResourceRulesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "data_authoring/source"
        self.source.mkdir(parents=True)
        self.rows = [{
            "resource_id": "ADMISSIBLE_EVIDENCE",
            "display_name": "Admissible Evidence",
            "description": "Processed evidence.",
            "resource_kind": "STOCKPILE",
            "tracks_lifetime": "true", "sort_order": "10", "active": "true",
        }]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self):
        with (self.source / rules.RESOURCES_FILE).open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rules.RESOURCE_COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)

    def validate(self):
        self.write()
        result = net.Result()
        data = rules.validate_resources(self.root, result)
        return result, data

    def test_valid_typed_export(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertIs(data["resources"][0]["tracksLifetime"], True)
        self.assertEqual(data["resources"][0]["sortOrder"], 10)

    def test_duplicate_and_bad_id(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)
        self.rows = [dict(self.rows[0], resource_id="bad-id")]
        self.assertFalse(self.validate()[0].valid)

    def test_kind_and_lifetime(self):
        self.rows[0]["resource_kind"] = "HEADCOUNT"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["tracks_lifetime"] = "false"
        self.assertTrue(self.validate()[0].valid)
        self.rows[0]["resource_kind"] = "UNKNOWN"
        self.assertFalse(self.validate()[0].valid)

    def test_invalid_fields(self):
        for field, value in (
            ("active", "maybe"), ("sort_order", "-1"),
            ("tracks_lifetime", "maybe"), ("display_name", ""),
        ):
            with self.subTest(field=field):
                before = self.rows[0][field]
                self.rows[0][field] = value
                self.assertFalse(self.validate()[0].valid)
                self.rows[0][field] = before

    def test_export_and_failed_export_preserves_file(self):
        self.write()
        result, path = rules.export(self.root)
        self.assertTrue(result.valid)
        original = path.read_bytes()
        self.assertFalse(json.loads(original)["runtimeImplemented"])
        self.rows[0]["active"] = "maybe"
        self.write()
        result, failed_path = rules.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed_path)
        self.assertEqual(path.read_bytes(), original)

    def test_metadata(self):
        self.assertEqual(TABLE_METADATA["resources"].columns, rules.RESOURCE_COLUMNS)
        self.assertEqual(page_for_tab_text("Resources Editor").group, "Department")
