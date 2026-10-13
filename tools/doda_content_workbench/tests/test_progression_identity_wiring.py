import ast
import csv
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_network_editor as editor
import doda_page_registry as registry
import doda_progression_identity_rules as pid

WORK = Path(__file__).resolve().parents[1]
ROOT = net.find_project_root(WORK)


class ProgressionIdentityWiringTests(unittest.TestCase):
    def test_metadata_columns_match(self):
        for name, columns in [
            ("upgrades", pid.UPGRADE_COLUMNS),
            ("plot_milestones", pid.MILESTONE_COLUMNS),
            ("plot_items", pid.ITEM_COLUMNS),
            ("mission_tier_requirements", pid.REQUIREMENT_COLUMNS),
        ]:
            with self.subTest(table=name):
                self.assertEqual(registry.TABLE_METADATA[name].columns, columns)

    def test_pages_registered(self):
        tables = {table for page in registry.PAGES for table in page.tables}
        self.assertTrue({
            "upgrades", "plot_milestones", "plot_items", "mission_tier_requirements"
        }.issubset(tables))

    def test_track_reference_reads_current_source(self):
        path = Path(tempfile.gettempdir()) / ("pid_track_" + uuid.uuid4().hex)
        path.mkdir()
        try:
            field = next(
                field for field in registry.TABLE_METADATA["upgrades"].fields
                if field.name == "track_id"
            )
            self.assertEqual(field.kind, "track_ref")
            self.assertEqual(editor.reference_keys(path, field), [])
            with (path / "department_tracks.csv").open("w", newline="", encoding="utf-8") as fh:
                writer = csv.writer(fh)
                writer.writerow(["track_id", "active"])
                writer.writerow(["TRACK_A", "true"])
                writer.writerow(["TRACK_B", "false"])
            self.assertEqual(editor.reference_keys(path, field), ["TRACK_A", "TRACK_B"])
        finally:
            shutil.rmtree(path, ignore_errors=True)

    def test_draft_track_dependency_is_staged(self):
        row = {column: "" for column in pid.UPGRADE_COLUMNS}
        row.update(
            upgrade_id="TEST_DRAFT_UPGRADE", display_name="Test draft",
            track_id="TECHNICAL_INFRASTRUCTURE", sort_order="10", active="false",
        )
        result = editor.validate_candidate(ROOT, "upgrades", [row])
        self.assertTrue(result.valid, result.errors)

    def test_gui_validation_and_export_calls_present(self):
        source = (WORK / "doda_content_gui.py").read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        methods = {
            node.func.attr for node in ast.walk(tree)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id == "doda_progression_identity_rules"
        }
        self.assertTrue({"validate_identities", "export"}.issubset(methods))


if __name__ == "__main__":
    unittest.main()
