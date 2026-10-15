import copy
import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

import doda_capabilities_editor as module
import doda_capabilities_draft_policy as policy
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
    columns = ("capability_id", "display_name", "standing_operation_label", "sort_order", "active")
    def __init__(self, rows):
        self.selected = ("Q1", "Q2")
        self.items = {r["capability_id"]: tuple(r[f] for f in self.columns) for r in rows}
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


class CapabilityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "capabilities.csv"
        self.rows = [
            dict(capability_id="Q" + str(i), display_name=name, description=desc, standing_operation_label="Routine",
                 sort_order=str(i), active="TRUE")
            for i, (name, desc) in enumerate(
                (("One", "First"), ("Two", "Second"), ("Three", "Third")), 1
            )
        ]
        self.e = module.CapabilitiesEditor.__new__(module.CapabilitiesEditor)
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
        self.assertEqual(self.e.tree.items["Q1"], ("Q1", "One", "Routine", "1", "TRUE"))

    def test_inline_apply_columns_do_not_shift(self):
        self.e._changes = {"display_name": "Updated"}
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.e.tree.items["Q1"], ("Q1", "Updated", "Routine", "1", "TRUE"))

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
        self.e._changes = {"capability_id": "OTHER"}
        self.assertFalse(self.e.apply_record())

    def test_invalid_id_and_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            self.e.validate_rows([{**self.rows[0], "capability_id": "bad"}])
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
        self.e.vars["capability_id"].set("OTHER")
        self.assertFalse(self.e.apply_record())

    def test_new_duplicate_blocked(self):
        self.e.tree.selected = ()
        self.e.description.value = "First"
        self.assertFalse(self.e.apply_record())

    def test_new_unique_row_is_draft_only(self):
        self.e.new()
        self.e.vars["capability_id"].set("Q4")
        self.e.vars["display_name"].set("Fourth")
        self.e.vars["standing_operation_label"].set("Fourth operation")
        self.e.description.value = "Fourth description"
        before = self.path.read_bytes()
        self.assertTrue(self.e.apply_record())
        self.assertEqual(len(self.e.loaded_rows), 4)
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_defaults_clear_description(self):
        self.e.new()
        self.assertEqual(self.e.description.get(), "")
        self.assertEqual(self.e.vars["capability_id"].get(), "")
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


    def test_standing_operation_common_display_is_not_edit(self):
        self.e.on_select(force=True)
        self.assertEqual(self.e.vars["standing_operation_label"].get(), "Routine")
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)

    def test_standing_operation_batch_changes_selected_rows_only(self):
        before = self.path.read_bytes()
        self.e._changes = {"standing_operation_label": "Updated operation"}
        self.assertTrue(self.e.apply_record())
        self.assertEqual(
            [r["standing_operation_label"] for r in self.e.loaded_rows],
            ["Updated operation", "Updated operation", "Routine"],
        )
        self.assertEqual(self.path.read_bytes(), before)
        self.assertEqual(self.e.tree.selection(), ("Q1", "Q2"))

    def test_standing_operation_clear_is_atomic(self):
        self.e._changes = {"standing_operation_label": ""}
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_standing_operation_placeholder_is_rejected(self):
        self.e._changes = {"standing_operation_label": "Multiple values"}
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_standing_operation_placeholder_focus_is_not_edit(self):
        self.e.loaded_rows[1]["standing_operation_label"] = "Different"
        self.e.on_select(force=True)
        widget = self.e.widgets["standing_operation_label"]
        widget.after_idle.side_effect = lambda callback: callback()
        self.e.select_placeholder("standing_operation_label")
        widget.selection_range.assert_called_once_with(0, "end")
        self.assertEqual(self.e._changes, {})

    def test_single_standing_operation_update_is_draft_only(self):
        self.e.tree.selected = ("Q1",)
        self.e.on_select(force=True)
        self.e.vars["standing_operation_label"].set("Single operation")
        before = self.path.read_bytes()
        self.assertTrue(self.e.apply_record())
        by_id = {row["capability_id"]: row for row in self.e.loaded_rows}
        self.assertEqual(by_id["Q1"]["standing_operation_label"], "Single operation")
        self.assertEqual(by_id["Q2"], self.rows[1])
        self.assertEqual(by_id["Q3"], self.rows[2])
        self.assertEqual(self.path.read_bytes(), before)

    def test_local_schema_remains_six_fields(self):
        self.assertEqual(
            module.FIELDS,
            ("capability_id", "display_name", "description",
             "standing_operation_label", "sort_order", "active"),
        )


class CapabilityProjectValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="v129-candidate-validation-")
        self.addCleanup(self.temp.cleanup)
        self.candidate = Path(self.temp.name) / "capabilities.csv"
        self.workbench = Path(module.__file__).resolve().parent
        self.source = self.workbench.parents[1] / "data_authoring" / "source"
        self.editor = module.CapabilitiesEditor.__new__(module.CapabilitiesEditor)
        self.editor.app = NS(
            source_directory=self.source,
            validator_path=self.workbench / "doda_content_workbench.py",
        )
        with (self.source / "capabilities.csv").open(encoding="utf-8-sig", newline="") as handle:
            self.rows = [dict(row) for row in csv.DictReader(handle)]
        self.source_before = {
            name: (self.source / name).read_bytes() for name in module.FILES
        }
        with (self.source / "capability_staffing_rules.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            self.referenced_id = next(csv.DictReader(handle))["capability_id"]

    def tearDown(self):
        for name, original in self.source_before.items():
            self.assertEqual((self.source / name).read_bytes(), original, name)

    def validate(self, rows):
        self.editor.write(self.candidate, rows)
        return self.editor.candidate_valid(self.candidate)

    def new_row(self, active):
        from uuid import uuid4
        return dict(
            capability_id="CAP_V129_TEST_" + uuid4().hex.upper(),
            display_name="Temporary test capability",
            description="Temporary validator fixture.",
            standing_operation_label="Temporary operation",
            sort_order=str(max(int(r["sort_order"]) for r in self.rows) + 1),
            active=active,
        )

    def test_saved_source_candidate_passes_real_validator(self):
        valid, output = self.validate(self.rows)
        self.assertTrue(valid, output)

    def test_referenced_capability_delete_fails_real_validator(self):
        candidate = [r for r in self.rows if r["capability_id"] != self.referenced_id]
        self.assertLess(len(candidate), len(self.rows))
        valid, output = self.validate(candidate)
        self.assertFalse(valid, output)
        self.assertIn(self.referenced_id, output)

    def test_referenced_capability_deactivation_fails_real_validator(self):
        candidate = [
            {**r, "active": "FALSE"} if r["capability_id"] == self.referenced_id else dict(r)
            for r in self.rows
        ]
        valid, output = self.validate(candidate)
        self.assertFalse(valid, output)
        self.assertIn(self.referenced_id, output)

    def test_new_active_capability_without_staffing_is_rejected(self):
        row = self.new_row("TRUE")
        valid, output = self.validate(self.rows + [row])
        self.assertFalse(valid, output)
        self.assertIn("No active staffing rule exists", output)
        self.assertIn(row["capability_id"], output)

    def test_new_inactive_unreferenced_capability_is_valid(self):
        valid, output = self.validate(self.rows + [self.new_row("FALSE")])
        self.assertTrue(valid, output)

class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Mock()
        self.app = NS(
            capabilities_editor=NS(dirty=True),
            _network_close_handler=self.previous, protocol=Mock(), destroy=Mock()
        )
        self.dialogs = Mock()

    def test_close_cancel_stops_existing_chain(self):
        self.dialogs.askyesno.return_value = False
        policy.install_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()

    def test_close_accept_delegates_without_clearing_draft(self):
        self.dialogs.askyesno.return_value = True
        policy.install_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.assertTrue(self.app.capabilities_editor.dirty)

    def test_clean_close_has_no_extra_prompt(self):
        self.app.capabilities_editor.dirty = False
        policy.install_capabilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_dirty_project_change_blocked(self):
        self.assertFalse(policy.allow_capabilities_project_change(self.app, self.dialogs))

    def test_clean_project_change_allowed(self):
        self.app.capabilities_editor.dirty = False
        self.assertTrue(policy.allow_capabilities_project_change(self.app, self.dialogs))

    def test_guard_installation_idempotent(self):
        policy.install_capabilities_draft_close_guard(self.app, self.dialogs)
        first = self.app._network_close_handler
        policy.install_capabilities_draft_close_guard(self.app, self.dialogs)
        self.assertIs(first, self.app._network_close_handler)
        self.app.protocol.assert_called_once()

    def test_project_guard_precedes_folder_picker(self):
        with patch.object(gui, "allow_capabilities_project_change", return_value=False), \
             patch.object(gui.filedialog, "askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()

    def test_file_exit_uses_same_guard(self):
        self.dialogs.askyesno.return_value = False
        policy.install_capabilities_draft_close_guard(self.app, self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()


class LegacyDraftCompatibilityTests(unittest.TestCase):
    def setUp(self):
        CapabilityTests.setUp(self)
        self.legacy_rows = copy.deepcopy(self.rows)
        self.legacy_rows[2].update(active="FALSE", standing_operation_label="")
        self.e.write(self.path, self.legacy_rows)

    def load_legacy(self):
        self.e.update(force=True)

    def by_id(self):
        return {row["capability_id"]: row for row in self.e.loaded_rows}

    def test_refresh_loads_inactive_source_draft_with_blank_label(self):
        self.load_legacy()
        self.assertEqual(self.by_id()["Q3"]["standing_operation_label"], "")
        self.assertFalse(self.e.dirty)
        self.assertEqual(self.e._source_rows["Q3"], self.legacy_rows[2])

    def test_refresh_rejects_active_source_record_with_blank_label(self):
        rows = copy.deepcopy(self.legacy_rows)
        rows[2]["active"] = "TRUE"
        self.e.write(self.path, rows)
        before = copy.deepcopy(self.e.loaded_rows)
        with self.assertRaisesRegex(ValueError, "Standing Operation Label"):
            self.e.update(force=True)
        self.assertEqual(self.e.loaded_rows, before)

    def test_other_batch_edit_preserves_unchanged_source_draft(self):
        self.load_legacy()
        before = self.path.read_bytes()
        self.e._changes = {"display_name": "Updated"}
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.by_id()["Q3"], self.legacy_rows[2])
        self.assertEqual(self.path.read_bytes(), before)

    def test_changed_legacy_record_still_requires_label(self):
        self.load_legacy()
        self.e.tree.selected = ("Q3",)
        self.e.on_select(force=True)
        self.e.description.value = "Changed description"
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.by_id()["Q3"], self.legacy_rows[2])
        self.assertFalse(self.e.dirty)

    def test_legacy_record_can_be_completed_with_explicit_label(self):
        self.load_legacy()
        self.e.tree.selected = ("Q3",)
        self.e.on_select(force=True)
        self.e.vars["standing_operation_label"].set("Explicit operation")
        before = self.path.read_bytes()
        self.assertTrue(self.e.apply_record())
        self.assertEqual(
            self.by_id()["Q3"]["standing_operation_label"], "Explicit operation"
        )
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_inactive_record_with_blank_label_is_rejected(self):
        self.load_legacy()
        self.e.new()
        self.e.vars["capability_id"].set("Q4")
        self.e.vars["display_name"].set("Fourth")
        self.e.description.value = "Fourth description"
        self.e.vars["active"].set("FALSE")
        self.assertFalse(self.e.apply_record())
        self.assertNotIn("Q4", self.by_id())

    def test_save_other_edit_preserves_blank_legacy_label(self):
        self.load_legacy()
        self.e.loaded_rows[0]["display_name"] = "Saved name"
        self.e.dirty = True
        self.e.save()
        self.assertFalse(self.e.dirty)
        with self.path.open(encoding="utf-8-sig", newline="") as handle:
            saved = {r["capability_id"]: r for r in csv.DictReader(handle)}
        self.assertEqual(saved["Q3"], self.legacy_rows[2])
        self.assertEqual(saved["Q1"]["display_name"], "Saved name")

    def test_revert_restores_source_draft_and_baseline(self):
        self.load_legacy()
        self.e.tree.selected = ("Q3",)
        self.e.on_select(force=True)
        self.e.vars["standing_operation_label"].set("Temporary operation")
        self.assertTrue(self.e.apply_record())
        self.dialogs.askyesno.return_value = True
        self.e.revert_source()
        self.assertFalse(self.e.dirty)
        self.assertEqual(self.by_id()["Q3"], self.legacy_rows[2])
        self.assertEqual(self.e._source_rows["Q3"], self.legacy_rows[2])
