import ast
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

WORK = Path(__file__).resolve().parents[1]
SOURCE = (WORK / "doda_foims_x_preview.py").read_text(encoding="utf-8-sig")

def cls():
    return next(
        n for n in ast.parse(SOURCE).body
        if isinstance(n, ast.ClassDef) and n.name == "FoimsXPreview"
    )

class RemovedTaskSpawnerTests(unittest.TestCase):
    def test_obsolete_files_absent(self):
        for name in (
            "doda_foims_x_" + "tasks.py",
            "doda_foims_x_" + "task_catalog.py",
            "tests/test_foims_x_" + "tasks.py",
            "tests/test_foims_x_" + "task_catalog.py",
        ):
            self.assertFalse((WORK / name).exists(), name)

    def test_no_spawner_imports_methods_or_controls(self):
        imports = {
            n.module for n in ast.walk(ast.parse(SOURCE))
            if isinstance(n, ast.ImportFrom)
        }
        self.assertNotIn("doda_foims_x_" + "tasks", imports)
        self.assertNotIn("doda_foims_x_" + "task_catalog", imports)
        methods = {n.name for n in cls().body if isinstance(n, ast.FunctionDef)}
        for name in (
            "_task_" + "now", "_task_" + "spawn", "_task_" + "cancel",
            "_task_" + "clear", "_task_" + "changed",
            "_populate_task_" + "templates",
        ):
            self.assertNotIn(name, methods)
        for label in ("Spawn " + "Task", "Cancel Selected " + "Task", "Clear " + "Tasks"):
            self.assertNotIn(label, SOURCE)

    def test_session_reset_preserves_sandbox_and_roster(self):
        node = next(
            n for n in cls().body
            if isinstance(n, ast.FunctionDef) and n.name == "_reset_simulation"
        )
        namespace = {}
        module = ast.Module(body=[node], type_ignores=[])
        exec(compile(ast.fix_missing_locations(module), "preview reset", "exec"), namespace)
        tables = {}
        owner = SimpleNamespace(
            app=SimpleNamespace(tables=tables),
            sandbox=SimpleNamespace(reset=Mock()),
            roster=SimpleNamespace(reset=Mock()),
            _populate_metric_controls=Mock(),
            _facility_catalog=object(),
            _refresh_facility_catalog=Mock(),
            render=Mock(),
        )
        namespace["_reset_simulation"](owner)
        owner.sandbox.reset.assert_called_once_with(tables)
        owner.roster.reset.assert_called_once_with()
        owner._populate_metric_controls.assert_called_once_with()
        owner._refresh_facility_catalog.assert_called_once_with()
        owner.render.assert_called_once_with()

    def test_catalog_and_debug_features_preserved(self):
        for value in ('"Task Templates"', '"Personnel"', '"Facilities"', '"Qualifications"'):
            self.assertIn(value, SOURCE)
        self.assertIn("self.controls = ttk.Frame(self.debug_window", SOURCE)
        self.assertIn("self.toolbar_frame.pack_forget()", SOURCE)
        self.assertIn("command=self._roster_toggle", SOURCE)
        self.assertIn("command=self._roster_reset", SOURCE)
