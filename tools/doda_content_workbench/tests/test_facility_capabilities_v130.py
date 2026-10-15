import copy
import csv
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

import doda_content_workbench as validator
import doda_content_gui as gui
import doda_facility_capabilities_editor as module
import doda_facility_capabilities_draft_policy as policy


class Variable:
    def __init__(self, value="", callback=None):
        self.value, self.callback = value, callback
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
        if self.callback:
            self.callback()


class Tree:
    def __init__(self, rows):
        self.columns = module.FIELDS
        self.selected = tuple(module.row_iid(row) for row in rows[:2])
        self.focused = self.selected[0]
        self.items = {module.row_iid(r): tuple(r[f] for f in self.columns) for r in rows}
        self.item = Mock(side_effect=self.update_item)
    def selection(self):
        return self.selected
    def selection_set(self, *items):
        self.selected = tuple(items)
    def selection_remove(self, *items):
        self.selected = tuple(i for i in self.selected if i not in items)
    def focus(self, iid=None):
        if iid is not None:
            self.focused = iid
        return self.focused
    def get_children(self):
        return tuple(self.items)
    def exists(self, iid):
        return iid in self.items
    def delete(self, iid):
        self.items.pop(iid)
        self.selected = tuple(i for i in self.selected if i != iid)
        if self.focused == iid:
            self.focused = ""
    def insert(self, _parent, _where, *, iid, values):
        self.items[iid] = tuple(values)
    def update_item(self, iid, *, values):
        self.items[iid] = tuple(values)
    def __getitem__(self, name):
        if name != "columns":
            raise KeyError(name)
        return self.columns


def tables():
    return {
        "facilities": [
            dict(facility_id=f, display_name=f, personnel_capacity=capacity, active="TRUE")
            for f, capacity in (("F1", "5"), ("F2", "2"))
        ],
        "capabilities": [
            dict(capability_id=c, display_name=c, sort_order=str(i), active="TRUE")
            for i, c in enumerate(("C1", "C2", "C3"), 1)
        ],
        "enum_catalog": [
            dict(enum_group="FACILITY_TIER", enum_value=t, sort_order=str(i), active="TRUE")
            for i, t in enumerate(("UNBUILT", "READY"), 1)
        ],
    }


def example_rows():
    return [
        dict(zip(module.FIELDS, ("F1", "C1", "One", "2", "UNBUILT", "P1", "1", "TRUE"))),
        dict(zip(module.FIELDS, ("F2", "C2", "", "1", "READY", "P2", "1", "TRUE"))),
        dict(zip(module.FIELDS, ("F1", "C2", "Third", "1", "UNBUILT", "P3", "2", "FALSE"))),
    ]


class EditorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="v130-editor-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "facility_capabilities.csv"
        self.rows = example_rows()
        self.e = module.FacilityCapabilitiesEditor.__new__(module.FacilityCapabilitiesEditor)
        e = self.e
        e.app = NS(tables=tables(), log=Mock(), refresh_all=Mock(), open_folder=Mock())
        e._loading = False
        e.vars = {
            f: Variable(self.rows[0][f], lambda f=f: e.changed(f)) for f in module.FIELDS
        }
        e.widgets = {f: Mock() for f in module.FIELDS}
        for widget in e.widgets.values():
            widget.after_idle.side_effect = lambda callback: callback()
        e.facility_hint = Mock()
        e.status = Variable()
        e.tree = Tree(self.rows)
        e.loaded_rows = copy.deepcopy(self.rows)
        e.editing_key = None
        e._session = e.tree.selection()
        e._original = copy.deepcopy(self.rows)
        e._changes = {}
        e._validated_dependencies = {}
        e.dirty = False
        e.loaded_path = self.path.resolve()
        e.source_path = lambda: self.path
        e.backup_directory = lambda: self.root / "backups"
        e.write(self.path, self.rows)
        e.snapshot_hash = e.digest(self.path)
        e.candidate_valid = Mock(return_value=(True, "PASS"))
        self.dialog_patch = patch.object(module, "messagebox")
        self.dialogs = self.dialog_patch.start()
        self.dialogs.askyesno.return_value = True
        self.addCleanup(self.dialog_patch.stop)

    def single(self, index=0):
        self.e.tree.selected = (module.row_iid(self.rows[index]),)
        self.e.on_select(force=True)

    def batch(self, field, value):
        self.e.vars[field].set(value)
        return self.e.apply_record()

    def test_schema_is_exactly_eight_fields(self):
        self.assertEqual(module.FIELDS, (
            "facility_id", "capability_id", "display_name_override",
            "max_concurrent_personnel", "initial_tier_id", "foims_panel_id",
            "sort_order", "active",
        ))

    def test_compound_iid_is_collision_free(self):
        a = dict(facility_id="A::B", capability_id="C")
        b = dict(facility_id="A", capability_id="B::C")
        self.assertNotEqual(module.row_iid(a), module.row_iid(b))

    def test_common_and_mixed_display(self):
        self.e.on_select(force=True)
        self.assertEqual(self.e.vars["active"].get(), "TRUE")
        self.assertEqual(self.e.vars["sort_order"].get(), "1")
        self.assertEqual(self.e.vars["facility_id"].get(), module.MULTIPLE_VALUES)
        self.assertEqual(self.e.vars["display_name_override"].get(), module.MULTIPLE_VALUES)
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)

    def test_load_does_not_mark_fields_edited(self):
        self.e.on_select(force=True)
        self.assertEqual(self.e._changes, {})

    def test_duplicate_selection_event_preserves_pending_edit(self):
        self.e.on_select(force=True)
        self.e.vars["foims_panel_id"].set("Pending")
        self.e.on_select()
        self.assertEqual(self.e._changes, {"foims_panel_id": "Pending"})

    def test_placeholder_focus_is_not_edit(self):
        self.e.on_select(force=True)
        self.e.select_placeholder("display_name_override")
        self.e.widgets["display_name_override"].selection_range.assert_called_once_with(0, "end")
        self.assertEqual(self.e._changes, {})

    def test_noop_batch_skips_validation(self):
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()
        self.assertFalse(self.e.dirty)

    def test_equal_batch_values_do_not_dirty_draft(self):
        self.assertFalse(self.batch("active", "TRUE"))
        self.assertFalse(self.e.dirty)

    def test_batch_edits_selected_fields_and_rows_only(self):
        before = self.path.read_bytes()
        self.assertTrue(self.batch("display_name_override", "Updated"))
        expected = copy.deepcopy(self.rows)
        expected[0]["display_name_override"] = expected[1]["display_name_override"] = "Updated"
        self.assertEqual(self.e.loaded_rows, expected)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.e.tree.selection(), tuple(module.row_iid(r) for r in self.rows[:2]))
        self.assertEqual(self.e.tree.item.call_count, 2)

    def test_optional_override_can_be_cleared_in_batch(self):
        self.assertTrue(self.batch("display_name_override", ""))
        self.assertEqual([r["display_name_override"] for r in self.e.loaded_rows], ["", "", "Third"])

    def test_mixed_tier_untouched_is_preserved(self):
        self.assertTrue(self.batch("foims_panel_id", "Common"))
        self.assertEqual([r["initial_tier_id"] for r in self.e.loaded_rows], ["UNBUILT", "READY", "UNBUILT"])

    def test_bulk_tier_edit(self):
        self.assertTrue(self.batch("initial_tier_id", "READY"))
        self.assertEqual([r["initial_tier_id"] for r in self.e.loaded_rows], ["READY", "READY", "UNBUILT"])

    def test_bulk_active_edit(self):
        self.assertTrue(self.batch("active", "FALSE"))
        self.assertEqual([r["active"] for r in self.e.loaded_rows], ["FALSE", "FALSE", "FALSE"])

    def test_batch_capacity_checks_each_facility_atomically(self):
        self.assertFalse(self.batch("max_concurrent_personnel", "3"))
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)
        self.e.candidate_valid.assert_not_called()

    def test_batch_capacity_at_smaller_facility_limit(self):
        self.assertTrue(self.batch("max_concurrent_personnel", "2"))

    def test_aggregate_capacity_is_not_local_rejection(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["max_concurrent_personnel"] = "5"
        rows[2]["max_concurrent_personnel"] = "5"
        rows[2]["active"] = "TRUE"
        self.e.validate_rows(rows)

    def test_required_panel_clear_is_atomic(self):
        self.assertFalse(self.batch("foims_panel_id", ""))
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_placeholder_rejected(self):
        self.assertFalse(self.batch("foims_panel_id", module.MULTIPLE_VALUES))

    def test_invalid_capacity_integer_rejected(self):
        self.assertFalse(self.batch("max_concurrent_personnel", "1.5"))

    def test_zero_capacity_rejected(self):
        self.assertFalse(self.batch("max_concurrent_personnel", "0"))

    def test_invalid_sort_integer_rejected(self):
        self.assertFalse(self.batch("sort_order", "a"))

    def test_zero_sort_rejected(self):
        self.assertFalse(self.batch("sort_order", "0"))

    def test_invalid_tier_rejected(self):
        self.assertFalse(self.batch("initial_tier_id", "INVENTED"))

    def test_invalid_boolean_rejected(self):
        self.assertFalse(self.batch("active", "maybe"))

    def test_identity_batch_injection_rejected(self):
        self.e._changes = {"facility_id": "F2"}
        self.assertFalse(self.e.apply_record())

    def test_duplicate_pair_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.e.validate_rows([self.rows[0], self.rows[0]])

    def test_malformed_row_rejected(self):
        with self.assertRaises(ValueError):
            self.e.validate_rows([{**self.rows[0], "extra": ""}])

    def test_unknown_facility_rejected(self):
        with self.assertRaises(ValueError):
            self.e.validate_rows([{**self.rows[0], "facility_id": "UNKNOWN"}])

    def test_unknown_capability_rejected(self):
        with self.assertRaises(ValueError):
            self.e.validate_rows([{**self.rows[0], "capability_id": "UNKNOWN"}])

    def test_inactive_parent_rejected(self):
        self.e.app.tables["facilities"][0]["active"] = "FALSE"
        with self.assertRaises(ValueError):
            self.e.validate_rows(self.rows)

    def test_candidate_failure_preserves_draft(self):
        self.e.candidate_valid.return_value = False, "references broken"
        self.assertFalse(self.batch("foims_panel_id", "Changed"))
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_stale_selection_rejected(self):
        self.e.tree.selected = (module.row_iid(self.rows[0]), module.row_iid(self.rows[2]))
        self.assertFalse(self.batch("foims_panel_id", "Changed"))
        self.e.candidate_valid.assert_not_called()

    def test_draft_mutation_during_validation_blocks_apply(self):
        def validate(_path):
            self.e.loaded_rows[2]["foims_panel_id"] = "Concurrent"
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.batch("foims_panel_id", "Changed"))
        self.assertEqual(self.e.loaded_rows[0]["foims_panel_id"], "P1")

    def test_selection_mutation_during_validation_blocks_apply(self):
        def validate(_path):
            self.e.tree.selected = (module.row_iid(self.rows[2]),)
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.batch("foims_panel_id", "Changed"))
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_single_facility_identity_change_blocked(self):
        self.single()
        self.e.vars["facility_id"].set("F2")
        self.assertFalse(self.e.apply_record())

    def test_single_capability_identity_change_blocked(self):
        self.single()
        self.e.vars["capability_id"].set("C3")
        self.assertFalse(self.e.apply_record())

    def test_single_edit_is_draft_only(self):
        self.single()
        before = self.path.read_bytes()
        self.e.vars["foims_panel_id"].set("Updated")
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.path.read_bytes(), before)

    def test_single_noop_skips_validation(self):
        self.single()
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_new_duplicate_pair_blocked(self):
        self.e.new()
        self.e.vars["foims_panel_id"].set("New")
        self.assertFalse(self.e.apply_record())

    def test_new_unique_pair_is_draft_only(self):
        before = self.path.read_bytes()
        self.e.new()
        self.e.vars["capability_id"].set("C3")
        self.e.vars["foims_panel_id"].set("New")
        self.assertTrue(self.e.apply_record())
        self.assertEqual(len(self.e.loaded_rows), 4)
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_defaults_and_sort_are_facility_scoped(self):
        self.e.new()
        self.assertEqual(self.e.vars["sort_order"].get(), "3")
        self.assertEqual(self.e.vars["initial_tier_id"].get(), "UNBUILT")
        self.assertEqual(self.e.vars["foims_panel_id"].get(), "")
        self.e.vars["facility_id"].set("F2")
        self.e.on_facility_changed()
        self.assertEqual(self.e.vars["sort_order"].get(), "2")

    def test_render_columns_and_identity_do_not_shift(self):
        self.e._render_draft()
        self.assertEqual(self.e.tree.items[module.row_iid(self.rows[0])], tuple(self.rows[0][f] for f in module.FIELDS))

    def test_render_preserves_selection_and_focus(self):
        before = self.e.tree.selection(), self.e.tree.focus()
        self.e._render_draft()
        self.assertEqual((self.e.tree.selection(), self.e.tree.focus()), before)

    def test_dirty_refresh_retains_rows_and_hash(self):
        self.e.dirty = True
        before = self.e.snapshot_hash
        self.path.write_text("external", encoding="utf-8")
        self.e.update()
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertEqual(self.e.snapshot_hash, before)

    def test_clean_refresh_reloads_source(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["foims_panel_id"] = "Reloaded"
        self.e.write(self.path, rows)
        self.e.update()
        self.assertEqual(self.e.loaded_rows, sorted(rows, key=module.sort_key))

    def test_bad_header_refresh_preserves_draft(self):
        self.e.dirty = True
        self.path.write_text("bad,header\n", encoding="utf-8")
        self.assertFalse(self.e.revert_source())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertTrue(self.e.dirty)

    def test_project_change_blocks_refresh_and_apply(self):
        self.e.dirty = True
        self.e.source_path = lambda: self.root / "other.csv"
        with self.assertRaises(ValueError):
            self.e.update()
        self.assertFalse(self.batch("foims_panel_id", "Changed"))

    def test_save_without_apply_does_not_commit(self):
        with patch.object(self.e, "commit") as commit:
            self.assertFalse(self.e.save())
        commit.assert_not_called()

    def test_save_ignores_unapplied_form(self):
        self.assertTrue(self.batch("foims_panel_id", "Applied"))
        self.e.vars["foims_panel_id"].set("Not applied")
        self.assertTrue(self.e.save())
        with self.path.open(newline="") as handle:
            saved = list(csv.DictReader(handle))
        self.assertEqual([r["foims_panel_id"] for r in saved], ["Applied", "P3", "Applied"])

    def test_save_creates_exact_original_backup(self):
        before = self.path.read_bytes()
        self.assertTrue(self.batch("foims_panel_id", "Changed"))
        self.assertTrue(self.e.save())
        backups = list(self.e.backup_directory().glob("*.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), before)
        self.assertFalse(self.e.dirty)
        self.e.app.refresh_all.assert_called_once_with(False)

    def test_external_csv_change_blocks_save(self):
        self.e.dirty = True
        self.path.write_text("external", encoding="utf-8")
        self.assertFalse(self.e.save())
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_text(), "external")

    def test_candidate_failure_blocks_save(self):
        self.e.dirty = True
        self.e.candidate_valid.return_value = False, "FAIL"
        before = self.path.read_bytes()
        self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue(self.e.dirty)
        self.assertFalse(self.e.backup_directory().exists())

    def test_csv_change_during_validation_blocks_save(self):
        self.e.dirty = True
        def validate(_path):
            self.path.write_text("external", encoding="utf-8")
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_text(), "external")

    def test_candidate_tamper_during_validation_blocks_save(self):
        self.e.dirty = True
        before = self.path.read_bytes()
        def validate(path):
            path.write_text("tampered", encoding="utf-8")
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue(self.e.dirty)

    def test_backup_failure_blocks_save(self):
        self.e.dirty = True
        before = self.path.read_bytes()
        with patch.object(module.shutil, "copy2", side_effect=OSError("backup denied")):
            self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue(self.e.dirty)

    def test_replace_failure_blocks_save(self):
        self.e.dirty = True
        before = self.path.read_bytes()
        with patch.object(module.os, "replace", side_effect=OSError("replace denied")):
            self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue(self.e.dirty)
        self.assertEqual(list(self.root.glob(".*.tmp.csv")), [])

    def test_dependency_change_before_replace_blocks_save(self):
        self.e.dirty = True
        dependency = self.root / "parent.csv"
        dependency.write_text("old")
        self.e._validated_dependencies = {dependency: self.e.digest(dependency)}
        dependency.write_text("new")
        before = self.path.read_bytes()
        self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), before)

    def test_multiple_delete_blocked(self):
        self.assertFalse(self.e.remove())
        self.e.candidate_valid.assert_not_called()

    def test_single_delete_is_draft_only(self):
        self.single()
        before = self.path.read_bytes()
        self.assertTrue(self.e.remove())
        self.assertEqual(len(self.e.loaded_rows), 2)
        self.assertEqual(self.path.read_bytes(), before)
        self.assertTrue(self.e.dirty)

    def test_delete_cancel_preserves_draft(self):
        self.single()
        self.dialogs.askyesno.return_value = False
        self.assertFalse(self.e.remove())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.e.candidate_valid.assert_not_called()

    def test_referenced_delete_rejected_before_acceptance(self):
        self.single()
        self.e.candidate_valid.return_value = False, "Referenced"
        self.assertFalse(self.e.remove())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_referenced_deactivation_rejected_before_acceptance(self):
        self.single()
        self.e.vars["active"].set("FALSE")
        self.e.candidate_valid.return_value = False, "Referenced"
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_revert_cancel_retains_draft(self):
        self.e.dirty = True
        self.dialogs.askyesno.return_value = False
        self.assertFalse(self.e.revert_source())
        self.assertTrue(self.e.dirty)

    def test_revert_read_failure_retains_draft(self):
        self.e.dirty = True
        self.path.unlink()
        self.assertFalse(self.e.revert_source())
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_revert_restores_deleted_source_row(self):
        self.single()
        self.assertTrue(self.e.remove())
        self.assertTrue(self.e.revert_source())
        self.assertEqual(self.e.loaded_rows, sorted(self.rows, key=module.sort_key))
        self.assertFalse(self.e.dirty)

    def test_revert_form_restores_draft_values(self):
        self.e.on_select(force=True)
        self.e.vars["foims_panel_id"].set("Pending")
        self.e.revert()
        self.assertEqual(self.e.vars["foims_panel_id"].get(), module.MULTIPLE_VALUES)
        self.assertEqual(self.e._changes, {})


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Mock()
        self.app = NS(facility_capabilities_editor=NS(dirty=True),
                      _network_close_handler=self.previous, protocol=Mock(), destroy=Mock())
        self.dialogs = Mock()

    def test_close_cancel_stops_chain(self):
        self.dialogs.askyesno.return_value = False
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()
        self.assertTrue(self.app.facility_capabilities_editor.dirty)

    def test_close_accept_delegates_without_clearing_draft(self):
        self.dialogs.askyesno.return_value = True
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.assertTrue(self.app.facility_capabilities_editor.dirty)

    def test_later_guard_cancel_does_not_discard_draft(self):
        self.dialogs.askyesno.return_value = True
        self.previous.return_value = None
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.assertTrue(self.app.facility_capabilities_editor.dirty)
        self.app.destroy.assert_not_called()

    def test_clean_close_has_no_extra_prompt(self):
        self.app.facility_capabilities_editor.dirty = False
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_dirty_project_change_blocked(self):
        self.assertFalse(policy.allow_facility_capabilities_project_change(self.app, self.dialogs))

    def test_clean_project_change_allowed(self):
        self.app.facility_capabilities_editor.dirty = False
        self.assertTrue(policy.allow_facility_capabilities_project_change(self.app, self.dialogs))

    def test_missing_editor_is_clean(self):
        self.assertFalse(policy.facility_capabilities_draft_dirty(NS()))

    def test_guard_installation_idempotent(self):
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        handler = self.app._network_close_handler
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        self.assertIs(handler, self.app._network_close_handler)
        self.app.protocol.assert_called_once()

    def test_project_guard_precedes_folder_picker(self):
        with patch.object(gui, "allow_facility_capabilities_project_change", return_value=False), \
                patch.object(gui.filedialog, "askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()

    def test_file_exit_uses_same_guard(self):
        self.dialogs.askyesno.return_value = False
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()

    def test_window_close_uses_same_handler(self):
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        self.assertEqual(self.app.protocol.call_args.args, ("WM_DELETE_WINDOW", self.app._network_close_handler))

    def test_no_existing_handler_destroy_on_accept(self):
        self.app._network_close_handler = None
        self.dialogs.askyesno.return_value = True
        policy.install_facility_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.app.destroy.assert_called_once()


class RealValidatorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="v130-validator-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.candidate = self.root / "facility_capabilities.csv"
        self.workbench = Path(validator.__file__).resolve().parent
        self.source = self.workbench.parents[1] / "data_authoring" / "source"
        self.editor = module.FacilityCapabilitiesEditor.__new__(module.FacilityCapabilitiesEditor)
        self.editor.app = NS(source_directory=self.source, validator_path=self.workbench / "doda_content_workbench.py")
        with (self.source / "facility_capabilities.csv").open(encoding="utf-8-sig", newline="") as handle:
            self.rows = list(csv.DictReader(handle))
        self.source_before = {name: (self.source / name).read_bytes() for name in module.FILES}

    def tearDown(self):
        for name, original in self.source_before.items():
            self.assertEqual((self.source / name).read_bytes(), original, name)

    def validate(self, rows):
        self.editor.write(self.candidate, rows)
        return self.editor.candidate_valid(self.candidate)

    def test_current_source_passes_real_validator(self):
        valid, output = self.validate(self.rows)
        self.assertTrue(valid, output)

    def test_last_installation_deletion_rejected_for_active_task(self):
        self.active_task_fixture()
        self.assertTrue(self.rows)
        valid, output = self.validate([])
        self.assertFalse(valid, output)
        self.assertIn("no active Facility Capability installation", output)

    def test_last_installation_deactivation_rejected_for_active_task(self):
        self.active_task_fixture()
        valid, output = self.validate([{**r, "active": "FALSE"} for r in self.rows])
        self.assertFalse(valid, output)
        self.assertIn("no active Facility Capability installation", output)

    def test_capacity_excess_rejected(self):
        with (self.source / "facilities.csv").open(encoding="utf-8-sig", newline="") as handle:
            capacities = {r["facility_id"]: int(r["personnel_capacity"]) for r in csv.DictReader(handle)}
        rows = copy.deepcopy(self.rows)
        rows[0]["max_concurrent_personnel"] = str(capacities[rows[0]["facility_id"]] + 1)
        valid, output = self.validate(rows)
        self.assertFalse(valid, output)
        self.assertIn("exceeds facility", output)

    def test_empty_display_override_is_valid(self):
        valid, output = self.validate([{**r, "display_name_override": ""} for r in self.rows])
        self.assertTrue(valid, output)

    def fixture_project(self):
        source = self.root / "fixture" / "data_authoring" / "source"
        source.mkdir(parents=True)
        for name, contents in self.source_before.items():
            (source / name).write_bytes(contents)
        self.editor.app.source_directory = source
        return source

    def active_task_fixture(self):
        # Current authored tasks are inactive drafts. Create one valid active
        # task in an isolated copy rather than claim the live data covers this.
        source = self.fixture_project()
        path = source / "task_templates.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields, tasks = reader.fieldnames, list(reader)
        tasks[0].update(active="TRUE", capability_id=self.rows[0]["capability_id"],
                        time_to_complete_minutes="1")
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(tasks)
        # Isolate task-availability validation from staffing-reference errors.
        path = source / "facility_capability_staffing_overrides.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            fields = csv.DictReader(handle).fieldnames
        with path.open("w", newline="") as handle:
            csv.DictWriter(handle, fieldnames=fields).writeheader()
        valid, output = self.validate(self.rows)
        self.assertTrue(valid, output)

    def test_staffing_override_blocks_pair_removal(self):
        source = self.fixture_project()
        key = module.row_key(self.rows[0])
        with (source / "capability_staffing_rules.csv").open(encoding="utf-8-sig", newline="") as handle:
            rules = list(csv.DictReader(handle))
        rule = next(r for r in rules if r["capability_id"] == key[1] and r["active"] == "TRUE")
        path = source / "facility_capability_staffing_overrides.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields, overrides = reader.fieldnames, list(reader)
        override = {f: rule.get(f, "") for f in fields}
        override["facility_id"], override["capability_id"] = key
        with path.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(overrides + [override])
        valid, output = self.validate(self.rows)
        self.assertTrue(valid, output)
        valid, output = self.validate([r for r in self.rows if module.row_key(r) != key])
        self.assertFalse(valid, output)
        self.assertIn("facility_id/capability_id pair", output)

    def test_aggregate_overcommit_remains_warning(self):
        source = self.fixture_project()
        with (source / "facilities.csv").open(encoding="utf-8-sig", newline="") as handle:
            capacities = {r["facility_id"]: int(r["personnel_capacity"]) for r in csv.DictReader(handle)}
        with (source / "capabilities.csv").open(encoding="utf-8-sig", newline="") as handle:
            capabilities = [r["capability_id"] for r in csv.DictReader(handle) if r["active"] == "TRUE"]
        rows = copy.deepcopy(self.rows)
        first = rows[0]
        first["max_concurrent_personnel"] = str(capacities[first["facility_id"]])
        second = dict(first, capability_id=next(c for c in capabilities if c != first["capability_id"]),
                      sort_order=str(int(first["sort_order"]) + 1), foims_panel_id="V130_FIXTURE")
        valid, output = self.validate(rows + [second])
        self.assertTrue(valid, output)
        self.assertIn("strategic allocation tradeoff", output)

    def test_validation_uses_complete_current_dependency_list(self):
        from doda_task_templates_editor import FILES
        self.assertEqual(module.FILES, tuple(FILES))


class TkControlTests(unittest.TestCase):
    """Automated widget smoke checks, not user manual GUI verification."""
    def setUp(self):
        try:
            self.app = tk.Tk()
        except tk.TclError as error:
            self.skipTest(str(error))
        self.addCleanup(self.app.destroy)
        self.app.withdraw()
        self.app.tables = tables()
        self.app.facility_capabilities_tab = tk.Frame(self.app)
        self.e = module.FacilityCapabilitiesEditor(self.app)
        self.e.loaded_rows = example_rows()
        self.e._render_draft()

    def test_extended_selection_and_exact_columns(self):
        self.assertEqual(str(self.e.tree.cget("selectmode")), "extended")
        self.assertEqual(tuple(self.e.tree["columns"]), module.FIELDS)

    def test_real_variable_traces_ignore_programmatic_load(self):
        self.e.tree.selection_set(*(module.row_iid(r) for r in self.e.loaded_rows[:2]))
        self.e.on_select(force=True)
        self.app.update_idletasks()
        self.assertEqual(self.e._changes, {})
        self.e.vars["foims_panel_id"].set("Changed")
        self.assertEqual(self.e._changes, {"foims_panel_id": "Changed"})

    def test_both_identity_controls_disabled_when_selected(self):
        self.e.tree.selection_set(module.row_iid(self.e.loaded_rows[0]))
        self.e.on_select(force=True)
        for field in module.IDENTITY:
            self.assertEqual(str(self.e.widgets[field].cget("state")), "disabled")

    def test_new_enables_readonly_identity_choices(self):
        self.e.new()
        for field in module.IDENTITY:
            self.assertEqual(str(self.e.widgets[field].cget("state")), "readonly")

    def test_mixed_tier_does_not_become_edit_on_selection_event(self):
        self.e.tree.selection_set(*(module.row_iid(r) for r in self.e.loaded_rows[:2]))
        self.e.on_select(force=True)
        self.app.update()
        self.assertEqual(self.e.vars["initial_tier_id"].get(), module.MULTIPLE_VALUES)
        self.assertEqual(self.e._changes, {})

    def load_current_source(self):
        workbench = Path(validator.__file__).resolve().parent
        self.app.project_root = workbench.parents[1]
        self.app.source_directory = self.app.project_root / "data_authoring" / "source"
        self.app.tables = {}
        for table in ("facilities", "capabilities", "enum_catalog"):
            with (self.app.source_directory / (table + ".csv")).open(
                encoding="utf-8-sig", newline=""
            ) as handle:
                self.app.tables[table] = list(csv.DictReader(handle))
        self.e.update()
        self.app.update()

    def test_current_source_load_refresh_and_alignment_with_real_widgets(self):
        self.load_current_source()
        original = self.e.source_path().read_bytes()
        self.assertTrue(self.e.loaded_rows)
        for row in self.e.loaded_rows:
            self.assertEqual(tuple(self.e.tree.item(module.row_iid(row), "values")),
                             tuple(row[f] for f in module.FIELDS))
        self.e.update()
        self.assertEqual(self.e.source_path().read_bytes(), original)
        self.assertFalse(self.e.dirty)

    def test_current_source_dirty_refresh_retains_real_selection(self):
        self.load_current_source()
        source_before = self.e.source_path().read_bytes()
        self.e.tree.selection_set(*(module.row_iid(r) for r in self.e.loaded_rows))
        self.e.on_select(force=True)
        selected = self.e.tree.selection()
        self.e.dirty = True
        self.e.update()
        self.app.update()
        self.assertEqual(self.e.tree.selection(), selected)
        self.assertEqual(self.e.source_path().read_bytes(), source_before)
        self.assertTrue(self.e.dirty)
