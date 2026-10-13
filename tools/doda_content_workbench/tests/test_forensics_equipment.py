import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_equipment_rules as equipment
import doda_network_rules as net
from doda_page_registry import TABLE_METADATA

class ForensicsEquipmentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "data_authoring/source"
        self.source.mkdir(parents=True)
        self.families = [
            dict(zip(equipment.FAMILY_COLUMNS, (
                fid, fid, "PERSONAL", "2",
                "NONE" if fid == "PHONE" else "HDD" if fid != "PDA" else "SC",
                "PHONE_LINE" if fid == "PHONE" else "NETWORK",
                "Test family", str(i * 10), "true",
            )))
            for i, fid in enumerate(("DESKTOP", "LAPTOP", "PDA", "PHONE"), 1)
        ]
        self.families.append(dict(zip(equipment.FAMILY_COLUMNS, (
            "TEST_LAB", "Lab", "LOCATION", "", "NONE", "NONE",
            "Physical examination lab.", "50", "true",
        ))))
        self.models = [dict(zip(equipment.MODEL_COLUMNS, (
            "TEST_LAB_BASE", "Lab Baseline", "TEST_LAB", "", "", "",
            "1", "No inventory implied.", "10", "true",
        )))]
        self.write(net.TIERS_FILE, net.TIER_COLUMNS, [])

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, filename, columns, rows):
        with (self.source / filename).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self):
        self.write(equipment.FAMILIES_FILE, equipment.FAMILY_COLUMNS, self.families)
        self.write(equipment.MODELS_FILE, equipment.MODEL_COLUMNS, self.models)
        result = net.Result()
        data = equipment.validate_equipment(self.root, result)
        return result, data

    def test_location_lab_and_personal_limits(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        lab = next(f for f in data["families"] if f["familyId"] == "TEST_LAB")
        self.assertEqual(lab["ownership"], "LOCATION")
        self.assertEqual(lab["connectionKind"], "NONE")
        self.assertIsNone(lab["perTaskLimit"])
        self.assertEqual(sum(
            f["perTaskLimit"] for f in data["families"]
            if f["ownership"] == "PERSONAL"
        ), 8)

    def test_connection_none_rejects_connection_fields(self):
        for key, value in (
            ("network_tier_id", "UNKNOWN"),
            ("phone_line_kind", "LANDLINE"),
            ("connection_override", "MOBILE_INTERNET"),
        ):
            with self.subTest(key=key):
                self.models[0][key] = value
                result, _ = self.validate()
                self.assertFalse(result.valid)
                self.assertTrue(any("NONE-connected" in e for e in result.errors))
                self.models[0][key] = ""

    def test_connection_none_rejects_storage(self):
        self.families[-1]["storage_kind"] = "HDD"
        self.assertFalse(self.validate()[0].valid)

    def test_metadata_uses_new_connection_choice(self):
        field = next(
            f for f in TABLE_METADATA["equipment_families"].fields
            if f.name == "connection_kind"
        )
        self.assertIn("NONE", field.choices)

    def test_export_contains_location_model(self):
        self.validate()
        result, path = equipment.export(self.root)
        self.assertTrue(result.valid, result.errors)
        payload = json.loads(path.read_text())
        lab = next(m for m in payload["models"] if m["modelId"] == "TEST_LAB_BASE")
        self.assertIsNone(lab["networkTierId"])
        self.assertIsNone(lab["phoneLineKind"])
        self.assertFalse(payload["runtimeImplemented"])
