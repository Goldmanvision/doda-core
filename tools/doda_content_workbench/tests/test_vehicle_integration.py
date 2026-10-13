"""Vehicle integration checks; no live source edits or GUI window creation."""
import ast
import csv
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import doda_network_editor as editor
import doda_network_rules as net
import doda_page_registry as registry
import doda_content_workbench as workbench
import doda_task_templates_editor as tasks
import doda_vehicle_rules as vehicles

W = Path(__file__).resolve().parents[1]
ROOT = W.parents[1]

class VehicleIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="vehicle-integration-")
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        shutil.copytree(ROOT / "data_authoring/source", self.src)
        self.rows = editor.read_rows(self.src / vehicles.VEHICLE_TYPES_FILE,
                                     registry.TABLE_METADATA["vehicle_types"])

    def tearDown(self):
        self.tmp.cleanup()

    def invalidate(self):
        self.rows[0]["max_team_members"] = "0"
        with (self.src / vehicles.VEHICLE_TYPES_FILE).open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=vehicles.COLUMNS)
            writer.writeheader()
            writer.writerows(self.rows)

    def test_metadata(self):
        spec = registry.TABLE_METADATA["vehicle_types"]
        self.assertEqual(spec.columns, vehicles.COLUMNS)
        self.assertEqual(spec.key_columns, ("vehicle_type_id",))
        self.assertEqual(registry.check_registry(), [])

    def test_navigation(self):
        page = registry.page_for_tab_text("Vehicle Types — Editor")
        self.assertEqual(page.page_id, "vehicle_types")
        self.assertEqual(page.group, "Equipment")

    def test_editor_installation(self):
        source = (W / "doda_network_editor.py").read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "install_network_editor")
        calls = [n for n in ast.walk(node) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "NetworkTableEditor"]
        self.assertTrue(any(len(n.args) > 2 and isinstance(n.args[2], ast.Constant) and n.args[2].value == "vehicle_types" for n in calls))

    def test_candidate_valid(self):
        result = editor.validate_candidate(self.root, "vehicle_types", self.rows)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(result.stats["vehicle_types"], 2)

    def test_candidate_invalid_preserves_source(self):
        path = self.src / vehicles.VEHICLE_TYPES_FILE
        before = path.read_bytes()
        self.rows[0]["max_team_members"] = "0"
        result = editor.validate_candidate(self.root, "vehicle_types", self.rows)
        self.assertFalse(result.valid)
        self.assertTrue(any("max_team_members" in e for e in result.errors))
        self.assertEqual(path.read_bytes(), before)

    def test_other_candidate_stages_vehicle_catalog(self):
        self.invalidate()
        spec = registry.TABLE_METADATA["equipment_families"]
        rows = editor.read_rows(self.src / spec.filename, spec)
        result = editor.validate_candidate(self.root, spec.table, rows)
        self.assertTrue(any("max_team_members" in e for e in result.errors), result.errors)

    def test_main_validation(self):
        self.invalidate()
        result = workbench.validate_project(self.root)
        self.assertTrue(any("max_team_members" in e for e in result.errors), result.errors)
        self.assertEqual(result.stats["vehicle_types"], 2)

    def test_task_save_staging(self):
        self.assertIn(vehicles.VEHICLE_TYPES_FILE, tasks.FILES)
        self.assertEqual(tasks.FILES.count(vehicles.VEHICLE_TYPES_FILE), 1)

    def gui_method(self):
        source = (W / "doda_content_gui.py").read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        node = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "run_network_rules")
        namespace = {"network_editors_dirty": lambda app: [], "APP_TITLE": "Test", "messagebox": Mock()}
        for n in tree.body:
            if isinstance(n, ast.Import):
                for alias in n.names:
                    if alias.name.startswith("doda_"):
                        module = Mock()
                        module.export.side_effect = lambda root: (net.Result(), None)
                        namespace[alias.asname or alias.name] = module
        namespace["doda_network_rules"].Result = net.Result
        namespace["doda_zscript_catalog"].is_current.return_value = True
        exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])), "gui-method", "exec"), namespace)
        app = SimpleNamespace(project_root=self.root, log=Mock())
        return namespace["run_network_rules"], namespace, app

    def test_gui_export_failure_propagates(self):
        fn, ns, app = self.gui_method()
        failed = net.Result()
        failed.errors.append("vehicle export failure")
        ns["doda_vehicle_rules"].export.return_value = (failed, None)
        ns["doda_vehicle_rules"].export.side_effect = None
        self.assertFalse(fn(app, "export", False))
        ns["doda_vehicle_rules"].export.assert_called_once_with(self.root)
        ns["messagebox"].showerror.assert_called_once()
        ns["messagebox"].showinfo.assert_not_called()
        ns["doda_zscript_catalog"].generate.assert_not_called()

    def test_gui_validation_failure_propagates(self):
        fn, ns, app = self.gui_method()
        def fail(root, result):
            result.errors.append("vehicle validation failure")
        ns["doda_vehicle_rules"].validate_vehicles.side_effect = fail
        self.assertFalse(fn(app, "validate", False))
        ns["doda_vehicle_rules"].validate_vehicles.assert_called_once()
        ns["messagebox"].showerror.assert_called_once()
        ns["messagebox"].showinfo.assert_not_called()
