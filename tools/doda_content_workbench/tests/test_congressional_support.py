import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_congressional_support_rules as cs
import doda_network_rules as net
import doda_page_registry as registry
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)


def validate(root):
    result = net.Result()
    data = terr.validate_territory(root, result)
    return result, data


class CongressionalSupportTests(unittest.TestCase):
    def copy_source(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "data_authoring" / "source"
        shutil.copytree(ROOT / "data_authoring" / "source", target)
        return Path(temp.name), target

    def test_seeded_tables_and_export(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        block = data["congressionalSupport"]
        self.assertEqual([i["inputId"] for i in block["inputs"]],
                         ["CS_INPUT_EVIDENCE", "CS_INPUT_PREPAREDNESS", "CS_INPUT_SUCCESS_RATE"])
        self.assertEqual(len(block["levels"]), 5)
        self.assertFalse(block["implemented"])
        self.assertFalse(block["rules"]["departmentFundingIsMetric"])

    def test_linear_component_score(self):
        self.assertEqual(cs.component_score(50, 0, 100), 50.0)
        self.assertEqual(cs.component_score(-5, 0, 100), 0.0)
        self.assertEqual(cs.component_score(500, 0, 100), 100.0)
        self.assertIsNone(cs.component_score(50, None, 100))

    def test_log_component_score(self):
        self.assertAlmostEqual(cs.component_score(100000, 1000, 100000000, "LOG10"), 40.0)
        with self.assertRaises(ValueError):
            cs.component_score(10, 0, 100, "LOG10")

    def test_strong_input_makes_up_for_weak_ones(self):
        weights = {"a": 1, "b": 1, "c": 1}
        spiky = cs.combined_score({"a": 100.0, "b": 0.0, "c": 0.0}, weights)
        balanced = cs.combined_score({"a": 30.0, "b": 30.0, "c": 30.0}, weights)
        self.assertGreater(spiky, balanced)
        self.assertIsNone(cs.combined_score({"a": None}, weights))

    def test_level_for_score(self):
        levels = [{"levelId": "L1", "minScore": 20}, {"levelId": "L2", "minScore": 40},
                  {"levelId": "L3", "minScore": None}]
        self.assertIsNone(cs.level_for_score(10, levels))
        self.assertEqual(cs.level_for_score(25, levels)["levelId"], "L1")
        self.assertEqual(cs.level_for_score(95, levels)["levelId"], "L2")

    def test_unknown_metric_is_an_error(self):
        temp_root, source = self.copy_source()
        path = source / "congressional_support_inputs.csv"
        text = path.read_text(encoding="utf-8-sig")
        self.assertIn("METRIC,PREPAREDNESS,", text)
        path.write_text(text.replace("METRIC,PREPAREDNESS,", "METRIC,BOGUS,"), encoding="utf-8", newline="")
        result, _ = validate(temp_root)
        self.assertTrue(any("is not a known metric" in e for e in result.errors))

    def test_level_scores_must_increase(self):
        temp_root, source = self.copy_source()
        path = source / "congressional_support_levels.csv"
        with path.open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
            columns = list(rows[0].keys())
        rows[0]["min_score"] = "50"
        rows[1]["min_score"] = "40"
        with path.open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=columns, lineterminator="\r\n")
            writer.writeheader()
            writer.writerows(rows)
        result, _ = validate(temp_root)
        self.assertTrue(any("min_score must strictly increase" in e for e in result.errors))

    def test_editor_registers_tables(self):
        inputs = registry.TABLE_METADATA["congressional_support_inputs"]
        levels = registry.TABLE_METADATA["congressional_support_levels"]
        self.assertEqual(inputs.columns, cs.INPUT_COLUMNS)
        self.assertEqual(levels.columns, cs.LEVEL_COLUMNS)


if __name__ == "__main__":
    unittest.main()
