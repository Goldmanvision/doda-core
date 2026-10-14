import copy
import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

import doda_qualification_catalog_editor as module
import doda_qualification_draft_policy as policy
import doda_content_gui as gui


class Variable:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


class Text:
    def __init__(self, value=""):
        self.value = value
        self.modified = False
        self.tag_add = Mock()
        self.mark_set = Mock()
    def get(self, *_args):
        return self.value
    def delete(self, *_args):
        self.value = ""
        self.modified = True
    def insert(self, _index, value):
        self.value = value
        self.modified = True
    def edit_modified(self, value=None):
        if value is not None:
            self.modified = bool(value)
        return self.modified
    def after_idle(self, callback):
        callback()


class Tree:
    columns = ("qualification_id", "display_name", "sort_order", "active")
    def __init__(self, rows):
        self.selected = ("Q1", "Q2")
        self.items = {r["qualification_id"]: tuple(r[f] for f in self.columns) for r in rows}
        self.item = Mock(side_effect=self.update_item)
    def selection(self):
        return self.selected
    def selection_set(self, *items):
        self.selected = tuple(items)
    def selection_remove(self, *items):
        self.selected = tuple(i for i in self.selected if i not in items)
    def get_children(self):
        return tuple(self.items)
    def exists(self, iid):
        return iid in self.items
    def delete(self, iid):
        self.items.pop(iid)
        self.selected = tuple(i for i in self.selected if i != iid)
    def insert(self, _parent, _where, *, iid, values):
        self.items[iid] = tuple(values)
    def update_item(self, iid, *, values):
        self.items[iid] = tuple(values)
    def __getitem__(self, name):
        if name != "columns":
            raise KeyError(name)
        return self.columns


class QualificationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "qualification_catalog.csv"
        self.rows = [
            dict(qualification_id="Q" + str(i), display_name=name, description=desc,
                 sort_order=str(i), active="TRUE")
            for i, (name, desc) in enumerate(
                (("One", "First"), ("Two", "Second"), ("Three", "Third")), 1
            )
        ]
        self.e = module.QualificationCatalogEditor.__new__(module.QualificationCatalogEditor)
        e = self.e
        e.app = NS(log=Mock(), refresh_all=Mock())
        e.vars = {f: Variable(self.rows[0][f]) for f in module.FIELDS}
        e.widgets = {f: Mock() for f in module.FIELDS}
        e.description = Text("Multiple values")
        e.widgets["description"] = e.description
        e._description_seen = "Multiple values"
        e.status = Variable()
        e.tree = Tree(self.rows)
        e.loaded_rows = copy.deepcopy(self.rows)
        e.editing_key = None
        e._loading = False
        e._session = ("Q1", "Q2")
        e._original = copy.deepcopy(self.rows)
        e._changes = {}
        e.dirty = False
        e.loaded_path = self.path.resolve()
        e.source_path = lambda: self.path
        e.backup_directory = lambda: self.root / "backups"
        e.write(self.path, self.rows)
        e.snapshot_hash = e.digest(self.path)
        e.candidate_valid = Mock(return_value=(True, "PASS"))
        self.dialog_patch = patch.object(module, "messagebox")
        self.dialogs = self.dialog_patch.start()
        self.addCleanup(self.dialog_patch.stop)

    def test_common_and_mixed_display(self):
        self.e.on_select(force=True)
        self.assertEqual(self.e.vars["active"].get(), "TRUE")
        self.assertEqual(self.e.vars["display_name"].get(), "Multiple values")
        self.assertEqual(self.e.description.get(), "Multiple values")
        self.assertEqual(self.e._changes, {})

    def test_programmatic_text_load_is_not_edit(self):
        self.e.on_select(force=True)
        self.e.description_modified()
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)

    def test_description_focus_is_not_edit(self):
        self.e.select_placeholder("description")
        self.e.description.tag_add.assert_called_once_with("sel", "1.0", "end-1c")
        self.assertEqual(self.e._changes, {})

    def test_description_event_tracks_only_description(self):
        self.e.description.value = "New"
        self.e.description.modified = True
        self.e.description_modified()
        self.assertEqual(self.e._changes, {"description": "New"})
        self.assertFalse(self.e.dirty)

    def test_apply_flushes_last_description_edit(self):
        self.e.description.value = "New"
        self.assertTrue(self.e.apply_record())
        self.assertEqual([r["description"] for r in self.e.loaded_rows], ["New", "New", "Third"])

    def test_duplicate_selection_event_preserves_pending_text(self):
        self.e.description.value = "Pending"
        self.e.on_select()
        self.assertEqual(self.e.description.get(), "Pending")

    def test_noop_apply_skips_validation(self):
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()
        self.assertFalse(self.e.dirty)

    def test_batch_changes_selected_field_and_rows_only(self):
        before = self.path.read_bytes()
        self.e._changes = {"display_name": "Updated"}
        self.assertTrue(self.e.apply_record())
        expected = copy.deepcopy(self.rows)
        expected[0]["display_name"] = "Updated"
        expected[1]["display_name"] = "Updated"
        self.assertEqual(self.e.loaded_rows, expected)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.e.tree.selection(), ("Q1", "Q2"))
        self.assertEqual(self.e.tree.item.call_count, 2)

    def test_render_columns_do_not_include_description(self):
        self.e._render_draft()
        self.assertEqual(self.e.tree.items["Q1"], ("Q1", "One", "1", "TRUE"))

    def test_inline_apply_columns_do_not_shift(self):
        self.e._changes = {"display_name": "Updated"}
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.e.tree.items["Q1"], ("Q1", "Updated", "1", "TRUE"))

    def test_description_clear_is_atomic(self):
        self.e.description.value = ""
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_required_name_clear_rejected(self):
        self.e._changes = {"display_name": ""}
        self.assertFalse(self.e.apply_record())

    def test_placeholder_rejected(self):
        self.e._changes = {"display_name": "Multiple values"}
        self.assertFalse(self.e.apply_record())

    def test_invalid_integer_rejected(self):
        self.e._changes = {"sort_order": "1.5"}
        self.assertFalse(self.e.apply_record())

    def test_invalid_boolean_rejected(self):
        self.e._changes = {"active": "maybe"}
        self.assertFalse(self.e.apply_record())

    def test_identity_injection_rejected(self):
        self.e._changes = {"qualification_id": "OTHER"}
        self.assertFalse(self.e.apply_record())

    def test_invalid_id_and_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            self.e.validate_rows([{**self.rows[0], "qualification_id": "bad"}])
        with self.assertRaises(ValueError):
            self.e.validate_rows([self.rows[0], self.rows[0]])

    def test_candidate_failure_preserves_draft(self):
        self.e._changes = {"display_name": "Updated"}
        self.e.candidate_valid.return_value = (False, "references broken")
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_stale_selection_rejected(self):
        self.e.tree.selected = ("Q1", "Q3")
        self.e._changes = {"display_name": "Updated"}
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_draft_mutation_during_validation_blocks_apply(self):
        self.e._changes = {"display_name": "Updated"}
        def validate(_path):
            self.e.loaded_rows[2]["display_name"] = "External draft change"
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows[0]["display_name"], "One")

    def test_single_identity_change_blocked(self):
        self.e.tree.selected = ("Q1",)
        self.e.on_select(force=True)
        self.e.vars["qualification_id"].set("OTHER")
        self.assertFalse(self.e.apply_record())

    def test_new_duplicate_blocked(self):
        self.e.tree.selected = ()
        self.e.description.value = "First"
        self.assertFalse(self.e.apply_record())

    def test_new_unique_row_is_draft_only(self):
        self.e.new()
        self.e.vars["qualification_id"].set("Q4")
        self.e.vars["display_name"].set("Fourth")
        self.e.description.value = "Fourth description"
        before = self.path.read_bytes()
        self.assertTrue(self.e.apply_record())
        self.assertEqual(len(self.e.loaded_rows), 4)
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_defaults_clear_description(self):
        self.e.new()
        self.assertEqual(self.e.description.get(), "")
        self.assertEqual(self.e.vars["qualification_id"].get(), "")
        self.assertEqual(self.e.vars["sort_order"].get(), "4")
        self.assertEqual(self.e._changes, {})

    def test_dirty_refresh_preserves_draft_and_hash(self):
        self.e.dirty = True
        before = self.e.snapshot_hash
        self.path.write_text("external", encoding="utf-8")
        self.e.update()
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertEqual(self.e.snapshot_hash, before)

    def test_clean_refresh_reloads_source(self):
        changed = copy.deepcopy(self.rows)
        changed[0]["display_name"] = "External"
        self.e.write(self.path, changed)
        self.e.update()
        self.assertEqual(self.e.loaded_rows, changed)
        self.assertFalse(self.e.dirty)

    def test_project_change_blocks_refresh_and_apply(self):
        self.e.dirty = True
        self.e.loaded_path = self.root / "other.csv"
        with self.assertRaises(ValueError):
            self.e.update()
        self.e._changes = {"display_name": "Updated"}
        self.assertFalse(self.e.apply_record())

    def test_save_without_apply_does_not_commit(self):
        self.e.commit = Mock()
        self.e.save()
        self.e.commit.assert_not_called()

    def test_save_uses_draft_not_pending_description(self):
        self.e.dirty = True
        self.e.description.value = "Unapplied"
        self.e.commit = Mock()
        self.e.save()
        self.e.commit.assert_called_once_with(self.e.loaded_rows)

    def test_save_creates_original_backup(self):
        original = self.path.read_bytes()
        self.e.loaded_rows[0]["display_name"] = "Saved"
        self.e.dirty = True
        self.e.save()
        self.assertFalse(self.e.dirty)
        backups = list((self.root / "backups").glob("*.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        with self.path.open(newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["display_name"], "Saved")

    def test_external_change_blocks_save(self):
        self.e.dirty = True
        self.path.write_text("external", encoding="utf-8")
        self.e.save()
        self.assertTrue(self.e.dirty)
        self.e.candidate_valid.assert_not_called()

    def test_candidate_failure_blocks_save(self):
        before = self.path.read_bytes()
        self.e.dirty = True
        self.e.candidate_valid.return_value = (False, "FAIL")
        self.e.save()
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_bytes(), before)

    def test_csv_change_during_validation_blocks_save(self):
        self.e.dirty = True
        def validate(_path):
            self.path.write_text("external", encoding="utf-8")
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.e.save()
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_text(), "external")

    def test_multiple_delete_blocked(self):
        self.e.remove()
        self.e.candidate_valid.assert_not_called()

    def test_single_delete_is_draft_only(self):
        self.e.tree.selected = ("Q1",)
        self.e.on_select(force=True)
        self.dialogs.askyesno.return_value = True
        before = self.path.read_bytes()
        self.e.remove()
        self.assertEqual(len(self.e.loaded_rows), 2)
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_bytes(), before)

    def test_referenced_delete_failure_preserves_draft(self):
        self.e.tree.selected = ("Q1",)
        self.e.on_select(force=True)
        self.dialogs.askyesno.return_value = True
        self.e.candidate_valid.return_value = (False, "referenced")
        self.e.remove()
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_revert_cancel_retains_draft(self):
        self.e.dirty = True
        self.e.update = Mock()
        self.dialogs.askyesno.return_value = False
        self.e.revert_source()
        self.e.update.assert_not_called()

    def test_revert_read_failure_retains_draft(self):
        self.e.dirty = True
        self.dialogs.askyesno.return_value = True
        self.path.unlink()
        self.e.revert_source()
        self.assertTrue(self.e.dirty)

    def test_revert_form_restores_draft_text(self):
        self.e.on_select(force=True)
        self.e.description.value = "Pending"
        self.e.revert()
        self.assertEqual(self.e.description.get(), "Multiple values")
        self.assertEqual(self.e._changes, {})


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Mock()
        self.app = NS(
            qualification_catalog_editor=NS(dirty=True),
            _network_close_handler=self.previous, protocol=Mock(), destroy=Mock()
        )
        self.dialogs = Mock()

    def test_close_cancel_stops_existing_chain(self):
        self.dialogs.askyesno.return_value = False
        policy.install_qualification_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()

    def test_close_accept_delegates_without_clearing_draft(self):
        self.dialogs.askyesno.return_value = True
        policy.install_qualification_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.assertTrue(self.app.qualification_catalog_editor.dirty)

    def test_clean_close_has_no_extra_prompt(self):
        self.app.qualification_catalog_editor.dirty = False
        policy.install_qualification_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_dirty_project_change_blocked(self):
        self.assertFalse(policy.allow_qualification_project_change(self.app, self.dialogs))

    def test_clean_project_change_allowed(self):
        self.app.qualification_catalog_editor.dirty = False
        self.assertTrue(policy.allow_qualification_project_change(self.app, self.dialogs))

    def test_guard_installation_idempotent(self):
        policy.install_qualification_draft_close_guard(self.app, self.dialogs)
        first = self.app._network_close_handler
        policy.install_qualification_draft_close_guard(self.app, self.dialogs)
        self.assertIs(first, self.app._network_close_handler)
        self.app.protocol.assert_called_once()

    def test_project_guard_precedes_folder_picker(self):
        with patch.object(gui, "allow_qualification_project_change", return_value=False), \
             patch.object(gui.filedialog, "askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()

    def test_file_exit_uses_same_guard(self):
        self.dialogs.askyesno.return_value = False
        policy.install_qualification_draft_close_guard(self.app, self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()