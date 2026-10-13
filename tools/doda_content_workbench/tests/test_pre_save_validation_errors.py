import csv
import copy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import doda_network_editor as editor


class PreSaveValidationErrorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="pre-save-errors-")
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

    def run_save(self, validation_error=None, hash_effect=None):
        with (
            patch.object(
                editor, "validate_candidate", return_value=self.good,
                side_effect=validation_error,
            ) as validator,
            patch.object(
                editor, "_sha", wraps=editor._sha, side_effect=hash_effect,
            ),
            patch.object(editor.messagebox, "showerror") as dialog,
            patch.object(editor, "write_rows", wraps=editor.write_rows) as writer,
        ):
            editor.NetworkTableEditor.save(self.obj)
        return validator, dialog, writer

    def assert_failed(self, dialog, writer):
        dialog.assert_called_once()
        self.assertIn("Save was not attempted", dialog.call_args.args[1])
        self.assertIn("in-memory draft is retained", dialog.call_args.args[1])
        writer.assert_not_called()
        self.assertFalse(self.obj.backup_dir.exists())
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(self.obj.rows, self.rows_before)
        self.assertTrue(self.obj.dirty)
        self.obj.load.assert_not_called()
        self.assertFalse(any(
            call.args[0].startswith("Saved ")
            for call in self.app.log.call_args_list
        ))
        self.assertTrue(any(
            "Pre-save validation failed:" in call.args[0]
            for call in self.app.log.call_args_list
        ))

    def test_initial_hash_filesystem_error(self):
        validator, dialog, writer = self.run_save(
            hash_effect=PermissionError("source read blocked")
        )
        validator.assert_not_called()
        self.assert_failed(dialog, writer)

    def test_initial_hash_unicode_error(self):
        validator, dialog, writer = self.run_save(
            hash_effect=UnicodeError("source decoding failed")
        )
        validator.assert_not_called()
        self.assert_failed(dialog, writer)

    def test_candidate_filesystem_error(self):
        validator, dialog, writer = self.run_save(
            validation_error=OSError("candidate staging failed")
        )
        validator.assert_called_once()
        self.assert_failed(dialog, writer)

    def test_candidate_unicode_error(self):
        validator, dialog, writer = self.run_save(
            validation_error=UnicodeError("candidate decoding failed")
        )
        validator.assert_called_once()
        self.assert_failed(dialog, writer)

    def test_candidate_csv_error(self):
        validator, dialog, writer = self.run_save(
            validation_error=csv.Error("candidate parsing failed")
        )
        validator.assert_called_once()
        self.assert_failed(dialog, writer)

    def test_post_validation_hash_error(self):
        validator, dialog, writer = self.run_save(hash_effect=[
            self.obj.loaded_sha,
            PermissionError("post-validation read blocked"),
        ])
        validator.assert_called_once()
        self.assert_failed(dialog, writer)

    def test_programming_error_is_not_hidden(self):
        with (
            patch.object(
                editor, "validate_candidate",
                side_effect=ValueError("programming error"),
            ),
            patch.object(editor.messagebox, "showerror") as dialog,
            patch.object(editor, "write_rows") as writer,
        ):
            with self.assertRaises(ValueError):
                editor.NetworkTableEditor.save(self.obj)
        dialog.assert_not_called()
        writer.assert_not_called()
        self.assertEqual(self.path.read_bytes(), self.original)

    def test_retry_after_validation_error_can_save(self):
        validator, dialog, writer = self.run_save(
            validation_error=OSError("temporary staging error")
        )
        self.assert_failed(dialog, writer)
        validator, dialog, writer = self.run_save()
        dialog.assert_not_called()
        writer.assert_called_once()
        self.assertIn(b"Saved edit", self.path.read_bytes())
        self.obj.load.assert_called_once()
