import csv
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import doda_network_editor as editor


class SharedSaveErrorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="shared-save-errors-")
        self.root = Path(self.tmp.name)
        self.path = self.root / "vehicle_types.csv"
        self.original = b"vehicle_type_id,display_name\r\nVAN,Van\r\n"
        self.path.write_bytes(self.original)
        self.good = SimpleNamespace(valid=True, errors=[], warnings=[])
        self.app = SimpleNamespace(
            project_root=self.root, log=Mock(), network_editors=[]
        )
        self.obj = SimpleNamespace(
            path=self.path,
            loaded_sha=editor._sha(self.path),
            title="Vehicle Types",
            backup_dir=self.root / "backups",
            app=self.app,
            dirty=True,
            spec=SimpleNamespace(
                table="vehicle_types", filename="vehicle_types.csv",
                columns=["vehicle_type_id", "display_name"],
            ),
            rows=[{"vehicle_type_id": "VAN", "display_name": "Saved edit"}],
            _report=Mock(),
            load=Mock(),
        )
        self.rows_before = copy.deepcopy(self.obj.rows)

    def tearDown(self):
        self.tmp.cleanup()

    def run_save(self, write_error=None):
        with (
            patch.object(editor, "validate_candidate", return_value=self.good),
            patch.object(editor.messagebox, "showerror") as dialog,
            patch.object(
                editor, "write_rows", wraps=editor.write_rows,
                side_effect=write_error,
            ) as writer,
        ):
            editor.NetworkTableEditor.save(self.obj)
        return dialog, writer

    def assert_failed(self, dialog):
        dialog.assert_called_once()
        self.assertIn("in-memory draft is retained", dialog.call_args.args[1])
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(self.obj.rows, self.rows_before)
        self.assertTrue(self.obj.dirty)
        self.obj.load.assert_not_called()
        self.assertFalse(any(
            call.args[0].startswith("Saved ")
            for call in self.app.log.call_args_list
        ))
        self.assertTrue(any(
            "Save failed:" in call.args[0]
            for call in self.app.log.call_args_list
        ))

    def test_backup_directory_error_retains_draft(self):
        with patch.object(
            Path, "mkdir",
            side_effect=PermissionError("backup directory blocked"),
        ):
            dialog, writer = self.run_save()
        self.assert_failed(dialog)
        writer.assert_not_called()

    def test_backup_copy_error_retains_draft(self):
        with patch.object(
            editor.shutil, "copy2",
            side_effect=PermissionError("backup copy blocked"),
        ):
            dialog, writer = self.run_save()
        self.assert_failed(dialog)
        writer.assert_not_called()

    def test_file_write_error_retains_draft(self):
        dialog, writer = self.run_save(PermissionError("destination blocked"))
        self.assert_failed(dialog)
        writer.assert_called_once()

    def test_csv_serialization_error_retains_draft(self):
        dialog, writer = self.run_save(csv.Error("CSV serialization failed"))
        self.assert_failed(dialog)
        writer.assert_called_once()

    def test_encoding_error_retains_draft(self):
        dialog, writer = self.run_save(UnicodeError("encoding failed"))
        self.assert_failed(dialog)
        writer.assert_called_once()

    def test_retry_after_write_error_can_save(self):
        dialog, writer = self.run_save(
            PermissionError("temporary access failure")
        )
        self.assert_failed(dialog)
        dialog, writer = self.run_save()
        dialog.assert_not_called()
        writer.assert_called_once()
        self.assertIn(b"Saved edit", self.path.read_bytes())
        self.obj.load.assert_called_once()
