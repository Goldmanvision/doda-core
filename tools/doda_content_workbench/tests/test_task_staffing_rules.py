import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_task_staffing_rules as staffing


class TaskStaffingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.parent_active = "true"
        self.parents = None
        self.columns = staffing.COLUMNS
        self.rows = [dict(zip(staffing.COLUMNS, ("T", "ANALYST", "3", "", "", "10", "true")))]

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, columns, rows):
        with (self.src / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    def validate(self):
        self.write("task_templates.csv", ["task_template_id", "active"],
                   self.parents or [{"task_template_id": "T", "active": self.parent_active}])
        self.write(staffing.STAFFING_FILE, self.columns, self.rows)
        result = staffing.Result()
        data = staffing.validate_staffing(self.root, result)
        return result, data

    def test_valid_minimum(self):
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(data["staffingRules"][0]["minContributors"], 3)
        self.assertIsNone(data["staffingRules"][0]["maxContributors"])

    def test_draft_blank(self):
        self.rows[0].update(active="false", min_contributors="")
        self.parent_active = "false"
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertTrue(result.warnings)
        self.assertIsNone(data["staffingRules"][0]["minContributors"])

    def test_active_minimum_required(self):
        self.rows[0]["min_contributors"] = ""
        self.assertFalse(self.validate()[0].valid)

    def test_active_parent_required(self):
        self.parent_active = "false"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0]["active"] = "false"
        self.assertTrue(self.validate()[0].valid)

    def test_unknown_parent(self):
        self.rows[0]["task_template_id"] = "MISSING"
        self.assertFalse(self.validate()[0].valid)

    def test_unknown_role(self):
        self.rows[0]["personnel_role"] = "MISSING"
        self.assertFalse(self.validate()[0].valid)

    def test_duplicate_rule(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)

    def test_invalid_counts(self):
        for value in ("0", "-1", "2.5", "abc"):
            with self.subTest(value=value):
                self.rows[0]["min_contributors"] = value
                self.assertFalse(self.validate()[0].valid)

    def test_count_ordering(self):
        for preferred, maximum in (("2", ""), ("", "2"), ("5", "4")):
            with self.subTest(preferred=preferred, maximum=maximum):
                self.rows[0].update(preferred_contributors=preferred,
                                    max_contributors=maximum)
                self.assertFalse(self.validate()[0].valid)

    def test_bad_header(self):
        self.columns = list(reversed(staffing.COLUMNS))
        self.assertFalse(self.validate()[0].valid)

    def test_bad_active_and_sort(self):
        self.rows[0]["active"] = "maybe"
        self.assertFalse(self.validate()[0].valid)
        self.rows[0].update(active="true", sort_order="-1")
        self.assertFalse(self.validate()[0].valid)

    def test_export_preserves_on_failure(self):
        self.validate()
        result, path = staffing.export(self.root)
        self.assertTrue(result.valid)
        old = path.read_bytes()
        self.assertFalse(json.loads(old)["runtimeImplemented"])
        self.rows[0]["personnel_role"] = "MISSING"
        self.validate()
        result, failed = staffing.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)
