import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources
import doda_task_flow_rules as flows


class PhysicalEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.write(
            "resources.csv", resources.RESOURCE_COLUMNS,
            [dict(zip(resources.RESOURCE_COLUMNS, (
                "EVIDENCE_PHYSICAL", "Physical Evidence",
                "Weapons, clothing and miscellaneous objects.",
                "STOCKPILE", "false", "65", "true",
            )))],
        )
        self.write(
            "task_templates.csv", ["task_template_id", "active"],
            [{"task_template_id": "T", "active": "false"}],
        )
        self.write(
            flows.FLOWS_FILE, flows.FLOW_COLUMNS,
            [dict(zip(flows.FLOW_COLUMNS, (
                "T", "OUT", "EVIDENCE_PHYSICAL", "WEIGHTED",
                "", "", "10", "false",
            )))],
        )

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def test_physical_resource(self):
        result = net.Result()
        data = resources.validate_resources(self.root, result)
        self.assertTrue(result.valid, result.errors)
        item = data["resources"][0]
        self.assertEqual(item["resourceId"], "EVIDENCE_PHYSICAL")
        self.assertEqual(item["resourceKind"], "STOCKPILE")
        self.assertFalse(item["tracksLifetime"])
        self.assertTrue(item["active"])

    def test_inactive_weighted_choice(self):
        result = net.Result()
        data = flows.validate_flows(self.root, result)
        self.assertTrue(result.valid, result.errors)
        item = data["flows"][0]
        self.assertEqual(item["resourceId"], "EVIDENCE_PHYSICAL")
        self.assertFalse(item["active"])
        self.assertIsNone(item["amount"])
        self.assertIsNone(item["weight"])
        self.assertTrue(result.warnings)

    def test_exports_keep_runtime_boundary(self):
        result, resource_path = resources.export(self.root)
        self.assertTrue(result.valid, result.errors)
        result, flow_path = flows.export(self.root)
        self.assertTrue(result.valid, result.errors)
        resource_data = json.loads(resource_path.read_text(encoding="utf-8"))
        flow_data = json.loads(flow_path.read_text(encoding="utf-8"))
        self.assertFalse(resource_data["runtimeImplemented"])
        self.assertFalse(flow_data["runtimeImplemented"])
        self.assertEqual(resource_data["resources"][0]["resourceId"],
                         "EVIDENCE_PHYSICAL")
        self.assertFalse(flow_data["flows"][0]["active"])
