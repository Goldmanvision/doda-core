import csv
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_task_prerequisite_rules as prerequisites


class TaskPrerequisiteTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.parent_active = "false"
        self.rows = [dict(zip(prerequisites.COLUMNS, (
            "PRE_PISTOL", "INVESTIGATE", "WEAPON_TYPE", "PER_ASSIGNED_AGENT",
            "AGENT", "PISTOL", "1", "One pistol per assigned agent.", "10", "false",
        )))]

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self):
        (self.src / "task_templates.csv").write_text(
            "task_template_id,active\nINVESTIGATE," + self.parent_active + "\n",
            encoding="utf-8",
        )
        with (self.src / prerequisites.PREREQUISITES_FILE).open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=prerequisites.COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)
        result = net.Result()
        data = prerequisites.validate_prerequisites(self.root, result)
        return result, data

    def test_valid_per_agent(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(data["prerequisites"][0]["minQuantity"], 1)

    def test_parent_and_active(self):
        self.rows[0]["active"] = "true"
        self.assertFalse(self.validate()[0].valid)
        self.parent_active = "true"
        self.assertTrue(self.validate()[0].valid)
        self.rows[0]["task_template_id"] = "MISSING"
        self.assertFalse(self.validate()[0].valid)

    def test_weapon_type(self):
        self.rows[0]["requirement_value"] = "WPN_BERETTA_M92"
        self.assertFalse(self.validate()[0].valid)

    def test_receptacle_and_scope(self):
        self.rows[0].update(requirement_kind="APPLICABLE_COLLECTION_RECEPTACLE",
                            requirement_value="")
        self.assertTrue(self.validate()[0].valid)
        self.rows[0]["scope"] = "TASK"
        self.assertFalse(self.validate()[0].valid)

    def test_vehicle_draft_quantity(self):
        self.rows[0].update(requirement_kind="MOTOR_VEHICLE", scope="TASK",
                            personnel_role="", requirement_value="", min_quantity="")
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertTrue(result.warnings)
        self.assertIsNone(data["prerequisites"][0]["minQuantity"])
        self.rows[0]["min_quantity"] = "0"
        self.assertFalse(self.validate()[0].valid)

    def test_export_failure_preserves(self):
        self.validate()
        result, path = prerequisites.export(self.root)
        self.assertTrue(result.valid, result.errors)
        old = path.read_bytes()
        self.rows[0]["min_quantity"] = "-1"
        self.validate()
        result, failed = prerequisites.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)
