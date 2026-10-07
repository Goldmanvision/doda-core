"""Test the actual GUI orchestration methods without starting Tk or subprocesses."""
import ast
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


def method(name, namespace):
    source = Path(__file__).resolve().parents[1] / "doda_content_gui.py"
    tree = ast.parse(source.read_text(encoding="utf-8-sig"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef)
               and any(isinstance(m, ast.FunctionDef) and m.name == name for m in n.body))
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 str(source), "exec"), namespace)
    return namespace[name]


class ExportChainTests(unittest.TestCase):
    def setUp(self):
        self.dialog = SimpleNamespace(showinfo=Mock(), showerror=Mock())
        self.fn = method("run_export", {
            "APP_TITLE": "Workbench", "messagebox": self.dialog,
            "sys": SimpleNamespace(executable="python")})
        self.app = SimpleNamespace(
            exporter_path=SimpleNamespace(is_file=lambda: True), project_root=Path("."),
            run_command=Mock(return_value=True), run_network_rules=Mock(return_value=True),
            log=Mock(), status_text=SimpleNamespace(set=Mock()))

    def test_content_failure_stops_chain(self):
        self.app.run_command.return_value = False
        self.fn(self.app)
        self.app.run_network_rules.assert_not_called()
        self.dialog.showinfo.assert_not_called()

    def test_rules_failure_does_not_report_full_success(self):
        self.app.run_network_rules.return_value = False
        self.fn(self.app)
        self.dialog.showinfo.assert_not_called()
        self.app.status_text.set.assert_called_with(
            "Export All incomplete: rules/catalog export failed.")

    def test_success_announced_only_at_end(self):
        self.fn(self.app)
        self.app.run_command.assert_called_once()
        self.assertFalse(self.app.run_command.call_args.kwargs["announce_success"])
        self.app.run_network_rules.assert_called_once_with("export", announce=False)
        self.dialog.showinfo.assert_called_once()

    def test_missing_exporter_stops_chain(self):
        self.app.exporter_path = SimpleNamespace(is_file=lambda: False)
        self.fn(self.app)
        self.app.run_command.assert_not_called()
        self.app.run_network_rules.assert_not_called()
        self.dialog.showerror.assert_called_once()

    def command_method(self, *, code=0, error=None):
        process = Mock()
        process.run.return_value = SimpleNamespace(stdout="", stderr="", returncode=code)
        process.run.side_effect = error
        fn = method("run_command", {
            "APP_TITLE": "Workbench", "messagebox": self.dialog, "subprocess": process})
        self.app.config = Mock()
        self.app.update_idletasks = Mock()
        self.app.refresh_all = Mock()
        return fn

    def test_process_failure_returns_false(self):
        fn = self.command_method(code=1)
        self.assertFalse(fn(self.app, "Export", ["python"], "ok", announce_success=False))
        self.dialog.showinfo.assert_not_called()
        self.dialog.showerror.assert_called_once()

    def test_launch_failure_returns_false(self):
        fn = self.command_method(error=OSError("cannot launch"))
        self.assertFalse(fn(self.app, "Export", ["python"], "ok", announce_success=False))
        self.dialog.showinfo.assert_not_called()
        self.dialog.showerror.assert_called_once()

    def test_process_success_can_suppress_intermediate_dialog(self):
        fn = self.command_method()
        self.assertTrue(fn(self.app, "Export", ["python"], "ok", announce_success=False))
        self.dialog.showinfo.assert_not_called()
