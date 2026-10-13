import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_collection_rules as collection


class CollectionReceptacleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.columns = collection.COLUMNS
        self.rows = [dict(zip(collection.COLUMNS, (
            "EVIDENCE_BAGS", "Evidence Bags", "Baggable evidence collection.",
            "10", "true",
        )))]

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self):
        with (self.src / collection.RECEPTACLES_FILE).open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(self.rows)
        result = net.Result()
        data = collection.validate_collection(self.root, result)
        return result, data

    def test_valid_definition(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(data["receptacles"][0]["receptacleId"], "EVIDENCE_BAGS")
        self.assertTrue(data["receptacles"][0]["active"])

    def test_duplicate(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)

    def test_invalid_id(self):
        self.rows[0]["receptacle_id"] = "bad id"
        self.assertFalse(self.validate()[0].valid)

    def test_required_text(self):
        for field in ("display_name", "description"):
            with self.subTest(field=field):
                original = self.rows[0][field]
                self.rows[0][field] = ""
                self.assertFalse(self.validate()[0].valid)
                self.rows[0][field] = original

    def test_invalid_active(self):
        self.rows[0]["active"] = "maybe"
        self.assertFalse(self.validate()[0].valid)

    def test_invalid_sort(self):
        for value in ("-1", "abc"):
            with self.subTest(value=value):
                self.rows[0]["sort_order"] = value
                self.assertFalse(self.validate()[0].valid)

    def test_missing_header_column(self):
        self.columns = collection.COLUMNS[:-1]
        self.rows = [{k: v for k, v in self.rows[0].items() if k != "active"}]
        self.assertFalse(self.validate()[0].valid)

    def test_export_preserved_on_failure(self):
        self.validate()
        result, path = collection.export(self.root)
        self.assertTrue(result.valid, result.errors)
        old = path.read_bytes()
        payload = json.loads(old)
        self.assertFalse(payload["runtimeImplemented"])
        self.assertTrue(payload["rules"]["definitionsCreateNoInventory"])
        self.assertFalse(payload["rules"]["personalDeviceSlotAccountingApplies"])
        self.rows[0]["active"] = "maybe"
        self.validate()
        result, failed = collection.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)
