import copy
import csv
import inspect
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

import doda_task_templates_editor as tasks
import doda_task_draft_policy as policy
import doda_content_gui as gui


class Variable:
    def __init__(self, value=""):
        self.value=value
    def set(self, value):
        self.value=value
    def get(self):
        return self.value


class TaskTemplateDraftTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="doda-task-draft-test-")
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.path=self.root / "task_templates.csv"
        self.row={field:"" for field in tasks.FIELDS}
        self.row.update(task_template_id="A",display_name="One",description="Description",priority="NORMAL",target_type="TERRITORY",loop_task="FALSE",reward_mode="CONTINUOUS",payout_count="0",sort_order="1",active="FALSE")
        self.write_source([self.row])
        self.editor=tasks.TaskTemplatesEditor.__new__(tasks.TaskTemplatesEditor)
        e=self.editor
        e.app=NS(log=Mock(),refresh_all=Mock())
        e.status=Variable()
        e.tree=Mock()
        e.tree.selection.return_value=("A",)
        e.loaded_rows=[dict(self.row)]
        e.editing_id="A"
        e.dirty=False
        e.loaded_path=self.path.resolve()
        e.snapshot_hash=e.digest(self.path)
        e.source_path=lambda:self.path
        e.backup_directory=lambda:self.root / "backups"
        e.record=Mock(return_value={**self.row,"display_name":"Changed"})
        e._render_draft=Mock()
        e.on_select=Mock()
        e.new=Mock()
        e._validate_rows=Mock()
        e.candidate_valid=Mock(return_value=(True,"PASS"))
        e.choices=Mock(return_value=[])
        e.widgets={field:Mock() for field in tasks.FIELDS}

    def write_source(self, rows):
        with self.path.open("w",encoding="utf-8",newline="") as handle:
            writer=csv.DictWriter(handle,fieldnames=tasks.FIELDS)
            writer.writeheader()
            writer.writerows(rows)

    def test_apply_updates_only_draft(self):
        before=self.path.read_bytes()
        self.editor.commit=Mock()
        self.editor.apply_record()
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"Changed")
        self.assertTrue(self.editor.dirty)
        self.editor.commit.assert_not_called()

    def test_apply_validation_failure_is_atomic(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor._validate_rows.side_effect=ValueError("invalid candidate")
        with patch.object(tasks.messagebox,"showerror"):
            self.editor.apply_record()
        self.assertEqual(self.editor.loaded_rows,before)
        self.assertFalse(self.editor.dirty)

    def test_apply_identity_change_blocked(self):
        self.editor.record.return_value={**self.row,"task_template_id":"B"}
        with patch.object(tasks.messagebox,"showerror"):
            self.editor.apply_record()
        self.assertEqual(self.editor.loaded_rows,[self.row])
        self.editor._validate_rows.assert_not_called()

    def test_new_duplicate_id_blocked(self):
        self.editor.editing_id=None
        with patch.object(tasks.messagebox,"showerror"):
            self.editor.apply_record()
        self.assertFalse(self.editor.dirty)
        self.editor._validate_rows.assert_not_called()

    def test_new_unique_row_is_draft_only(self):
        self.editor.editing_id=None
        self.editor.record.return_value={**self.row,"task_template_id":"B","sort_order":"2"}
        before=self.path.read_bytes()
        self.editor.apply_record()
        self.assertEqual(len(self.editor.loaded_rows),2)
        self.assertEqual(self.path.read_bytes(),before)

    def test_multi_apply_stays_blocked_in_v125a(self):
        self.editor.tree.selection.return_value=("A","B")
        with patch.object(tasks.messagebox,"showwarning"):
            self.editor.apply_record()
        self.editor.record.assert_not_called()

    def test_delete_is_draft_only(self):
        before=self.path.read_bytes()
        self.editor.commit=Mock()
        with patch.object(tasks.messagebox,"askyesno",return_value=True):
            self.editor.remove()
        self.assertEqual(self.editor.loaded_rows,[])
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.path.read_bytes(),before)
        self.editor.commit.assert_not_called()

    def test_delete_validation_failure_preserves_draft(self):
        self.editor._validate_rows.side_effect=ValueError("referenced task")
        with patch.object(tasks.messagebox,"askyesno",return_value=True), patch.object(tasks.messagebox,"showerror"):
            self.editor.remove()
        self.assertEqual(self.editor.loaded_rows,[self.row])
        self.assertFalse(self.editor.dirty)

    def test_delete_cancel_changes_nothing(self):
        with patch.object(tasks.messagebox,"askyesno",return_value=False):
            self.editor.remove()
        self.assertEqual(self.editor.loaded_rows,[self.row])
        self.editor._validate_rows.assert_not_called()

    def test_refresh_keeps_dirty_draft_and_hash(self):
        self.editor.dirty=True
        self.editor.loaded_rows[0]["display_name"]="Draft"
        saved_hash=self.editor.snapshot_hash
        self.write_source([{**self.row,"display_name":"External"}])
        self.editor.update()
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"Draft")
        self.assertEqual(self.editor.snapshot_hash,saved_hash)
        self.assertTrue(self.editor.dirty)
        self.editor._render_draft.assert_not_called()

    def test_clean_refresh_loads_source(self):
        self.write_source([{**self.row,"display_name":"External"}])
        self.editor.update()
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"External")
        self.assertFalse(self.editor.dirty)
        self.assertEqual(self.editor.snapshot_hash,self.editor.digest(self.path))

    def test_dirty_cross_project_refresh_blocked(self):
        self.editor.dirty=True
        self.editor.loaded_path=(self.root / "another_project.csv").resolve()
        with self.assertRaises(ValueError):
            self.editor.update()
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.editor.loaded_rows,[self.row])

    def test_revert_cancel_keeps_dirty_draft(self):
        self.editor.dirty=True
        self.editor.update=Mock()
        with patch.object(tasks.messagebox,"askyesno",return_value=False):
            self.editor.revert_source()
        self.editor.update.assert_not_called()
        self.assertTrue(self.editor.dirty)

    def test_revert_reloads_source_without_writing(self):
        self.editor.dirty=True
        self.editor.loaded_rows[0]["display_name"]="Draft"
        before=self.path.read_bytes()
        with patch.object(tasks.messagebox,"askyesno",return_value=True):
            self.editor.revert_source()
        self.assertFalse(self.editor.dirty)
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"One")
        self.assertEqual(self.path.read_bytes(),before)

    def test_revert_read_error_keeps_dirty_draft(self):
        self.editor.dirty=True
        self.path.unlink()
        with patch.object(tasks.messagebox,"askyesno",return_value=True),patch.object(tasks.messagebox,"showerror"):
            self.editor.revert_source()
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.editor.loaded_rows,[self.row])

    def test_save_without_apply_does_not_commit_form(self):
        self.editor.commit=Mock()
        self.editor.save()
        self.editor.commit.assert_not_called()
        self.editor.record.assert_not_called()

    def test_save_uses_draft_even_with_multiple_selection(self):
        self.editor.dirty=True
        self.editor.tree.selection.return_value=("A","B")
        self.editor.commit=Mock()
        self.editor.save()
        self.editor.commit.assert_called_once_with(self.editor.loaded_rows)
        self.editor.record.assert_not_called()

    def test_successful_source_save_creates_backup(self):
        original=self.path.read_bytes()
        self.editor.loaded_rows[0]["display_name"]="Draft"
        self.editor.dirty=True
        with patch.object(tasks.messagebox,"showinfo"):
            self.editor.save()
        self.assertFalse(self.editor.dirty)
        self.assertEqual(self.editor.snapshot_hash,self.editor.digest(self.path))
        backups=list((self.root / "backups").glob("*.csv"))
        self.assertEqual(len(backups),1)
        self.assertEqual(backups[0].read_bytes(),original)
        with self.path.open(newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["display_name"],"Draft")
        self.assertEqual(list(self.root.glob(".tasks-*.tmp.csv")),[])

    def test_pre_validation_hash_conflict_preserves_source(self):
        self.editor.dirty=True
        self.write_source([{**self.row,"display_name":"External"}])
        external=self.path.read_bytes()
        with patch.object(tasks.messagebox,"showerror"):
            self.editor.save()
        self.assertEqual(self.path.read_bytes(),external)
        self.assertTrue(self.editor.dirty)
        self.editor.candidate_valid.assert_not_called()

    def test_validation_failure_keeps_dirty_draft(self):
        self.editor.dirty=True
        self.editor.candidate_valid.return_value=(False,"FAIL")
        before=self.path.read_bytes()
        with patch.object(tasks.messagebox,"showerror"):
            self.editor.save()
        self.assertEqual(self.path.read_bytes(),before)
        self.assertTrue(self.editor.dirty)
        self.assertEqual(list(self.root.glob(".tasks-*.tmp.csv")),[])

    def test_source_changed_during_validation_is_not_overwritten(self):
        self.editor.dirty=True
        def validation(_candidate):
            self.write_source([{**self.row,"display_name":"External"}])
            return True,"PASS"
        self.editor.candidate_valid.side_effect=validation
        with patch.object(tasks.messagebox,"showerror"):
            self.editor.save()
        self.assertTrue(self.editor.dirty)
        with self.path.open(newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["display_name"],"External")
        self.assertFalse((self.root / "backups").exists())

    def test_source_changed_during_backup_is_not_overwritten(self):
        self.editor.dirty=True
        real_copy=tasks.shutil.copy2
        def backup(source,destination):
            result=real_copy(source,destination)
            self.write_source([{**self.row,"display_name":"External"}])
            return result
        with patch.object(tasks.shutil,"copy2",side_effect=backup), patch.object(tasks.messagebox,"showerror"):
            self.editor.save()
        self.assertTrue(self.editor.dirty)
        with self.path.open(newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["display_name"],"External")

    def test_backup_error_retains_draft(self):
        self.editor.dirty=True
        before=self.path.read_bytes()
        with patch.object(tasks.shutil,"copy2",side_effect=OSError("backup failed")),patch.object(tasks.messagebox,"showerror"):
            self.editor.save()
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(list(self.root.glob(".tasks-*.tmp.csv")),[])

    def test_write_error_retains_draft(self):
        self.editor.dirty=True
        before=self.path.read_bytes()
        with patch.object(tasks.os,"replace",side_effect=OSError("write failed")),patch.object(tasks.messagebox,"showerror"):
            self.editor.save()
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.path.read_bytes(),before)
        self.assertEqual(list(self.root.glob(".tasks-*.tmp.csv")),[])

    def test_save_read_error_retains_draft(self):
        self.editor.dirty=True
        with patch.object(self.editor,"digest",side_effect=OSError("read failed")),patch.object(tasks.messagebox,"showerror"):
            self.editor.save()
        self.assertTrue(self.editor.dirty)
        self.editor.candidate_valid.assert_not_called()

    def test_candidate_validation_uses_temp_file_only(self):
        before=self.path.read_bytes()
        paths=[]
        def validation(path):
            paths.append(path)
            self.assertTrue(path.is_file())
            self.assertNotEqual(path,self.path)
            return True,"PASS"
        self.editor.candidate_valid.side_effect=validation
        tasks.TaskTemplatesEditor._validate_rows(self.editor,[self.row])
        self.assertEqual(self.path.read_bytes(),before)
        self.assertFalse(paths[0].exists())


class TaskDraftPolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous=Mock()
        self.app=NS(task_templates_editor=NS(dirty=True),_network_close_handler=self.previous,protocol=Mock(),destroy=Mock())
        self.dialogs=Mock()

    def test_close_cancel_preserves_task_draft(self):
        self.dialogs.askyesno.return_value=False
        policy.install_task_draft_close_guard(self.app,self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()
        self.assertTrue(self.app.task_templates_editor.dirty)

    def test_close_confirm_delegates_to_shared_guard(self):
        self.dialogs.askyesno.return_value=True
        policy.install_task_draft_close_guard(self.app,self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.app.destroy.assert_not_called()

    def test_clean_task_close_does_not_add_prompt(self):
        self.app.task_templates_editor.dirty=False
        policy.install_task_draft_close_guard(self.app,self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_dirty_task_blocks_project_change(self):
        self.assertFalse(policy.allow_task_project_change(self.app,self.dialogs))
        self.dialogs.showwarning.assert_called_once()
        self.assertTrue(self.app.task_templates_editor.dirty)

    def test_clean_task_allows_project_change(self):
        self.app.task_templates_editor.dirty=False
        self.assertTrue(policy.allow_task_project_change(self.app,self.dialogs))
        self.dialogs.showwarning.assert_not_called()

    def test_close_guard_installation_is_idempotent(self):
        policy.install_task_draft_close_guard(self.app,self.dialogs)
        first=self.app._network_close_handler
        policy.install_task_draft_close_guard(self.app,self.dialogs)
        self.assertIs(self.app._network_close_handler,first)
        self.app.protocol.assert_called_once()

    def test_project_change_guard_runs_before_folder_picker(self):
        with patch.object(gui,"allow_task_project_change",return_value=False),patch.object(gui.filedialog,"askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()

    def test_file_exit_uses_wrapped_close_handler(self):
        self.dialogs.askyesno.return_value=False
        policy.install_task_draft_close_guard(self.app,self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()
