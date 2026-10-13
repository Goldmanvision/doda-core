import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch
import doda_network_editor as editor


class SharedEditorSaveGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="shared-save-guard-")
        self.root = Path(self.tmp.name)
        self.path = self.root / "vehicle_types.csv"
        self.original = b"vehicle_type_id,display_name\r\nVAN,Van\r\n"
        self.external = b"vehicle_type_id,display_name\r\nVAN,External edit\r\n"
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
            spec=SimpleNamespace(
                table="vehicle_types",
                filename="vehicle_types.csv",
                columns=["vehicle_type_id", "display_name"],
            ),
            rows=[{"vehicle_type_id": "VAN", "display_name": "Saved edit"}],
            _report=Mock(),
            load=Mock(),
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_save(self, effect=None):
        effect = effect or (lambda *args: self.good)
        with (
            patch.object(editor, "validate_candidate", side_effect=effect) as validator,
            patch.object(editor.messagebox, "showerror") as dialog,
            patch.object(editor, "write_rows", wraps=editor.write_rows) as writer,
        ):
            editor.NetworkTableEditor.save(self.obj)
        return validator, dialog, writer

    def test_preexisting_external_change_blocks_save(self):
        self.path.write_bytes(self.external)
        validator, dialog, writer = self.run_save()
        validator.assert_not_called()
        dialog.assert_called_once()
        writer.assert_not_called()
        self.assertEqual(self.path.read_bytes(), self.external)

    def test_invalid_candidate_leaves_source_and_backup_untouched(self):
        bad = SimpleNamespace(valid=False, errors=["invalid"], warnings=[])
        validator, dialog, writer = self.run_save(lambda *args: bad)
        self.obj._report.assert_called_once()
        writer.assert_not_called()
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertFalse(self.obj.backup_dir.exists())

    def test_external_edit_during_validation_blocks_save(self):
        def change(*args):
            self.path.write_bytes(self.external)
            return self.good
        validator, dialog, writer = self.run_save(change)
        dialog.assert_called_once()
        writer.assert_not_called()
        self.obj.load.assert_not_called()
        self.assertEqual(self.path.read_bytes(), self.external)
        self.assertFalse(self.obj.backup_dir.exists())

    def test_deletion_during_validation_blocks_save(self):
        def change(*args):
            self.path.unlink()
            return self.good
        validator, dialog, writer = self.run_save(change)
        dialog.assert_called_once()
        writer.assert_not_called()
        self.assertFalse(self.path.exists())

    def test_creation_during_validation_blocks_save(self):
        self.path.unlink()
        self.obj.loaded_sha = None
        def change(*args):
            self.path.write_bytes(self.external)
            return self.good
        validator, dialog, writer = self.run_save(change)
        dialog.assert_called_once()
        writer.assert_not_called()
        self.assertEqual(self.path.read_bytes(), self.external)

    def test_external_edit_during_backup_blocks_save(self):
        original_copy = editor.shutil.copy2
        def change(source, destination):
            result = original_copy(source, destination)
            self.path.write_bytes(self.external)
            return result
        with patch.object(editor.shutil, "copy2", side_effect=change):
            validator, dialog, writer = self.run_save()
        dialog.assert_called_once()
        writer.assert_not_called()
        self.obj.load.assert_not_called()
        self.assertEqual(self.path.read_bytes(), self.external)

    def test_unchanged_source_saves_and_preserves_backup(self):
        validator, dialog, writer = self.run_save()
        validator.assert_called_once()
        dialog.assert_not_called()
        writer.assert_called_once()
        backups = list(self.obj.backup_dir.glob("*.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), self.original)
        self.assertIn(b"Saved edit", self.path.read_bytes())
        self.obj.load.assert_called_once()

    def test_success_does_not_reload_other_dirty_editors(self):
        clean = SimpleNamespace(dirty=False, load=Mock())
        dirty = SimpleNamespace(dirty=True, load=Mock())
        self.app.network_editors = [self.obj, clean, dirty]
        self.run_save()
        clean.load.assert_called_once()
        dirty.load.assert_not_called()
