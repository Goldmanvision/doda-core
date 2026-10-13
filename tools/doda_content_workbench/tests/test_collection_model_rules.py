import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources
import doda_collection_rules as collection
import doda_collection_model_rules as models


class CollectionModelTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.parent_active = "true"
        self.rows = [dict(zip(models.MODEL_COLUMNS, (
            "M", "Model", "RECEPTACLE", "BAGS", "", "",
            "EVIDENCE_PHYSICAL;EVIDENCE_PHOTOGRAPHIC", "1",
            "Test model.", "10", "true",
        )))]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self):
        self.write(collection.RECEPTACLES_FILE, collection.COLUMNS, [
            dict(zip(collection.COLUMNS, ("BAGS", "Bags", "Test.", "10", self.parent_active)))
        ])
        self.write(models.DEVICES_FILE, models.DEVICE_COLUMNS, [
            dict(zip(models.DEVICE_COLUMNS, ("CAMERA", "Camera", "Test.", "10", "true")))
        ])
        self.write(resources.RESOURCES_FILE, resources.RESOURCE_COLUMNS, [
            dict(zip(resources.RESOURCE_COLUMNS, (rid, rid, "Test.", "STOCKPILE", "false", "10", "true")))
            for rid in ("EVIDENCE_PHYSICAL", "EVIDENCE_PHOTOGRAPHIC", "ADMISSIBLE_EVIDENCE")
        ])
        self.write(models.MODELS_FILE, models.MODEL_COLUMNS, self.rows)
        result = net.Result()
        data = models.validate_models(self.root, result)
        return result, data

    def test_valid_multiselect(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(len(data["models"][0]["evidenceTypes"]), 2)
        self.assertEqual(data["models"][0]["evidenceValueMultiplier"], "1")

    def test_device_model(self):
        self.rows[0].update(collection_kind="DEVICE", collection_type_id="CAMERA")
        self.assertTrue(self.validate()[0].valid)

    def test_type_references(self):
        self.rows[0]["collection_type_id"] = "MISSING"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0].update(collection_kind="DEVICE", collection_type_id="BAGS")
        self.assertFalse(self.validate()[0].valid)

    def test_duplicate_model(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)

    def test_invalid_evidence_selection(self):
        for raw in ("MISSING", "ADMISSIBLE_EVIDENCE", "EVIDENCE_PHYSICAL;EVIDENCE_PHYSICAL"):
            with self.subTest(raw=raw):
                self.rows[0]["evidence_types"] = raw
                self.assertFalse(self.validate()[0].valid)

    def test_invalid_multiplier(self):
        for raw in ("0", "-1", "NaN", "Infinity", "abc", "1e2"):
            with self.subTest(raw=raw):
                self.rows[0]["evidence_value_multiplier"] = raw
                self.assertFalse(self.validate()[0].valid)

    def test_active_properties_required(self):
        for name in ("evidence_types", "evidence_value_multiplier"):
            old = self.rows[0][name]
            self.rows[0][name] = ""
            self.assertFalse(self.validate()[0].valid)
            self.rows[0][name] = old

    def test_draft_blanks(self):
        self.rows[0].update(active="false", evidence_types="", evidence_value_multiplier="")
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertTrue(result.warnings)
        self.assertIsNone(data["models"][0]["evidenceValueMultiplier"])

    def test_active_parent_required(self):
        self.parent_active = "false"
        self.assertFalse(self.validate()[0].valid)

    def test_half_up(self):
        self.assertEqual(models.piece_value("1.25", "2"), 3)
        self.assertEqual(models.piece_value("1.5", "3"), 5)
        self.assertEqual(models.piece_value("2.5", "1"), 3)
        self.assertEqual(models.piece_value("0", "3"), 0)

    def test_per_piece_before_total(self):
        self.assertEqual(sum(models.piece_value("1.25", "2") for _ in range(2)), 6)

    def test_invalid_base_value(self):
        for raw in ("-1", "NaN", "Infinity"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    models.piece_value(raw, "2")

    def test_export_failure_preserves(self):
        self.validate()
        result, path = models.export(self.root)
        self.assertTrue(result.valid, result.errors)
        old = path.read_bytes()
        data = json.loads(old)
        self.assertFalse(data["runtimeImplemented"])
        self.assertEqual(data["rules"]["rounding"], "ROUND_HALF_UP_PER_PIECE")
        self.rows[0]["evidence_value_multiplier"] = "0"
        self.validate()
        result, failed = models.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)
