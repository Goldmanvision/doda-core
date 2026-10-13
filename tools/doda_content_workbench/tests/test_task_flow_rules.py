import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_resource_rules as resources
import doda_task_flow_rules as flows
from doda_page_registry import TABLE_METADATA, page_for_tab_text

class TaskFlowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.parent_active = "true"
        self.resource_active = "true"
        self.resource_kind = "STOCKPILE"
        self.rows = [
            dict(zip(flows.FLOW_COLUMNS,
                     ("T", "OUT", "R", "FIXED", "1", "", "10", "true")))
        ]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, filename, columns, rows):
        with (self.src / filename).open("w", newline="") as handle:
            w = csv.DictWriter(handle, fieldnames=columns)
            w.writeheader()
            w.writerows(rows)

    def validate(self):
        self.write("task_templates.csv", ["task_template_id", "active"],
                   [{"task_template_id": "T", "active": self.parent_active}])
        self.write("resources.csv", resources.RESOURCE_COLUMNS, [
            dict(zip(resources.RESOURCE_COLUMNS,
                     ("R", "Resource", "Test resource.", self.resource_kind,
                      "false", "10", self.resource_active))),
            dict(zip(resources.RESOURCE_COLUMNS,
                     ("S", "Second", "Test resource.", "STOCKPILE",
                      "false", "20", "true"))),
        ])
        self.write(flows.FLOWS_FILE, flows.FLOW_COLUMNS, self.rows)
        result = net.Result()
        data = flows.validate_flows(self.root, result)
        return result, data

    def test_valid_fixed(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(data["flows"][0]["amount"], 1)

    def test_draft_blanks(self):
        self.rows[0].update(active="false", amount="", flow_mode="WEIGHTED", weight="")
        self.parent_active = "false"
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertIsNone(data["flows"][0]["amount"])
        self.assertTrue(result.warnings)

    def test_active_requires_values_and_parent(self):
        self.rows[0]["amount"] = ""
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["amount"] = "1"
        self.parent_active = "false"
        self.assertFalse(self.validate()[0].valid)

    def test_resource_references(self):
        self.rows[0]["resource_id"] = "MISSING"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["resource_id"] = "R"
        self.resource_active = "false"
        self.assertFalse(self.validate()[0].valid)
        self.resource_active = "true"
        self.resource_kind = "HEADCOUNT"
        self.assertFalse(self.validate()[0].valid)

    def test_inputs_fixed_and_fixed_weight_blank(self):
        self.rows[0].update(direction="IN", flow_mode="WEIGHTED", weight="2")
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["flow_mode"] = "FIXED"
        self.assertFalse(self.validate()[0].valid)

    def test_weighted_positive_weights(self):
        self.rows[0].update(flow_mode="WEIGHTED", weight="2", amount="10")
        self.assertTrue(self.validate()[0].valid)
        self.rows[0]["weight"] = "0"
        self.assertFalse(self.validate()[0].valid)

    def test_weighted_amounts_and_modes_agree(self):
        self.rows[0].update(flow_mode="WEIGHTED", weight="2", amount="10")
        self.rows.append(dict(self.rows[0], resource_id="S", weight="3", amount="11"))
        self.assertFalse(self.validate()[0].valid)
        self.rows[1]["amount"] = "10"
        self.assertTrue(self.validate()[0].valid)
        self.rows[1].update(flow_mode="FIXED", weight="")
        self.assertFalse(self.validate()[0].valid)

    def test_duplicate_and_bad_amount(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)
        self.rows.pop()
        self.rows[0]["amount"] = "-1"
        self.assertFalse(self.validate()[0].valid)

    def test_export_failure_preserves_output(self):
        self.validate()
        result, path = flows.export(self.root)
        self.assertTrue(result.valid)
        old = path.read_bytes()
        self.assertFalse(json.loads(old)["runtimeImplemented"])
        self.rows[0]["resource_id"] = "MISSING"
        self.validate()
        result, failed = flows.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)

    def test_metadata(self):
        self.assertEqual(TABLE_METADATA["task_template_flows"].columns, flows.FLOW_COLUMNS)
        self.assertEqual(TABLE_METADATA["task_template_flows"].key_columns,
                         ("task_template_id", "direction", "resource_id"))
        self.assertEqual(page_for_tab_text("Task Resource Flows Editor").group, "Tasks")
