import copy
import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

import doda_capability_staffing_rules_editor as module
import doda_capability_staffing_draft_policy as policy
import doda_content_gui as gui


class Variable:
    def __init__(self, value=""):
        self.value = value
    def get(self):
        return self.value
    def set(self, value):
        self.value = value


class StaffingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "capability_staffing_rules.csv"
        self.rows = [
            dict(capability_id="CAP", qualification_id=q, min_contributors="0",
                 preferred_contributors=p, max_contributors="4", sort_order=str(i), active="TRUE")
            for i, (q, p) in enumerate((("Q1", "1"), ("Q2", "2"), ("Q3", "3")), 1)
        ]
        self.e = module.CapabilityStaffingRulesEditor.__new__(module.CapabilityStaffingRulesEditor)
        e = self.e
        e.app = NS(log=Mock(), refresh_all=Mock(), tables={
            "capabilities": [dict(capability_id="CAP", active="TRUE")],
            "qualification_catalog": [
                dict(qualification_id=q, active="TRUE") for q in ("Q1", "Q2", "Q3", "Q4")
            ]
        })
        e.vars = {f: Variable(self.rows[0][f]) for f in module.FIELDS}
        e.widgets = {f: Mock() for f in module.FIELDS}
        e.status = Variable()
        e.tree = Mock()
        e.tree.selection.return_value = ("CAP::Q1", "CAP::Q2")
        e.loaded_rows = copy.deepcopy(self.rows)
        e.editing_key = None
        e._loading = False
        e._session = ("CAP::Q1", "CAP::Q2")
        e._original = copy.deepcopy(self.rows)
        e._changes = {}
        e.dirty = False
        e.loaded_path = self.path.resolve()
        e.source_path = lambda: self.path
        e.backup_directory = lambda: self.root / "backups"
        e.write(self.path, self.rows)
        e.snapshot_hash = e.digest(self.path)
        e.candidate_valid = Mock(return_value=(True, "PASS"))
        e._render_draft = Mock()
        e.new = Mock()
        self.dialog_patch = patch.object(module, "messagebox")
        self.dialogs = self.dialog_patch.start()
        self.addCleanup(self.dialog_patch.stop)

    def test_common_and_mixed_display(self):
        self.e.on_select(force=True)
        self.assertEqual(self.e.vars["min_contributors"].get(), "0")
        self.assertEqual(self.e.vars["preferred_contributors"].get(), "Multiple values")
        self.assertEqual(self.e.vars["qualification_id"].get(), "Multiple values")
        self.assertEqual(self.e._changes, {})
        self.e.widgets["qualification_id"].configure.assert_called_with(state="disabled")

    def test_loading_does_not_track_edits(self):
        self.e._loading = True
        self.e.changed("min_contributors")
        self.assertEqual(self.e._changes, {})

    def test_identity_changes_not_tracked(self):
        self.e.changed("qualification_id")
        self.assertEqual(self.e._changes, {})

    def test_noop_apply_skips_validation(self):
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()
        self.assertFalse(self.e.dirty)

    def test_batch_changes_selected_rows_and_field_only(self):
        original_bytes = self.path.read_bytes()
        self.e._changes = {"preferred_contributors": "4"}
        self.assertTrue(self.e.apply_record())
        expected = copy.deepcopy(self.rows)
        expected[0]["preferred_contributors"] = "4"
        expected[1]["preferred_contributors"] = "4"
        self.assertEqual(self.e.loaded_rows, expected)
        self.assertEqual(self.path.read_bytes(), original_bytes)
        self.assertTrue(self.e.dirty)
        self.e._render_draft.assert_not_called()
        self.assertEqual(self.e.tree.item.call_count, 2)
        self.assertEqual(self.e.tree.selection(), ("CAP::Q1", "CAP::Q2"))

    def test_invalid_range_is_atomic(self):
        self.e._changes = {"min_contributors": "3"}
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_placeholder_rejected(self):
        self.e._changes = {"preferred_contributors": "Multiple values"}
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_blank_integer_rejected(self):
        self.e._changes = {"sort_order": ""}
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_identity_injection_rejected(self):
        self.e._changes = {"qualification_id": "Q3"}
        self.assertFalse(self.e.apply_record())

    def test_stale_selection_rejected(self):
        self.e.tree.selection.return_value = ("CAP::Q1", "CAP::Q3")
        self.e._changes = {"sort_order": "5"}
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_candidate_failure_preserves_draft(self):
        self.e._changes = {"sort_order": "5"}
        self.e.candidate_valid.return_value = (False, "invalid")
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_validation_draft_change_blocks_apply(self):
        self.e._changes = {"sort_order": "5"}
        def validate(_path):
            self.e.loaded_rows[2]["sort_order"] = "9"
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows[0]["sort_order"], "1")

    def test_single_identity_change_rejected(self):
        self.e.tree.selection.return_value = ("CAP::Q1",)
        self.e.editing_key = ("CAP", "Q1")
        self.e.vars["qualification_id"].set("Q2")
        self.assertFalse(self.e.apply_record())

    def test_new_duplicate_rejected(self):
        self.e.tree.selection.return_value = ()
        self.assertFalse(self.e.apply_record())

    def test_new_unique_row_is_draft_only(self):
        original_bytes = self.path.read_bytes()
        self.e.tree.selection.return_value = ()
        self.e.vars["qualification_id"].set("Q4")
        self.e.on_select = Mock()
        self.assertTrue(self.e.apply_record())
        self.assertEqual(len(self.e.loaded_rows), 4)
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_single_apply_is_draft_only(self):
        self.e.tree.selection.return_value = ("CAP::Q1",)
        self.e.editing_key = ("CAP", "Q1")
        self.e.vars["preferred_contributors"].set("4")
        original_bytes = self.path.read_bytes()
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows[-1]["preferred_contributors"], "4")
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_save_without_apply_does_not_commit(self):
        self.e.commit = Mock()
        self.e.save()
        self.e.commit.assert_not_called()

    def test_save_uses_draft_not_form(self):
        self.e.dirty = True
        self.e.commit = Mock()
        self.e.save()
        self.e.commit.assert_called_once_with(self.e.loaded_rows)

    def test_save_creates_original_backup(self):
        original = self.path.read_bytes()
        self.e.loaded_rows[0]["preferred_contributors"] = "4"
        self.e.dirty = True
        self.e.save()
        self.assertFalse(self.e.dirty)
        backups = list((self.root / "backups").glob("*.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        with self.path.open(newline="") as handle:
            self.assertEqual(next(csv.DictReader(handle))["preferred_contributors"], "4")
        self.assertEqual(list(self.root.glob(".capability-staffing-*.tmp.csv")), [])

    def test_external_csv_change_blocks_save(self):
        self.e.dirty = True
        self.path.write_text("external", encoding="utf-8")
        self.e.save()
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_text(), "external")
        self.e.candidate_valid.assert_not_called()

    def test_validation_csv_change_blocks_save(self):
        self.e.dirty = True
        def validate(_path):
            self.path.write_text("external", encoding="utf-8")
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.e.save()
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_text(), "external")

    def test_candidate_failure_blocks_save(self):
        original_bytes = self.path.read_bytes()
        self.e.dirty = True
        self.e.candidate_valid.return_value = (False, "FAIL")
        self.e.save()
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_dirty_refresh_retains_rows_and_snapshot(self):
        self.e.dirty = True
        original_hash = self.e.snapshot_hash
        self.path.write_text("external", encoding="utf-8")
        self.e.update()
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertEqual(self.e.snapshot_hash, original_hash)
        self.e._render_draft.assert_not_called()

    def test_clean_refresh_loads_source(self):
        changed = copy.deepcopy(self.rows)
        changed[0]["preferred_contributors"] = "4"
        self.e.write(self.path, changed)
        self.e.update()
        self.assertEqual(self.e.loaded_rows, changed)
        self.assertFalse(self.e.dirty)

    def test_cross_project_refresh_and_apply_blocked(self):
        self.e.dirty = True
        self.e.loaded_path = (self.root / "other.csv").resolve()
        with self.assertRaises(ValueError):
            self.e.update()
        self.e._changes = {"sort_order": "5"}
        self.assertFalse(self.e.apply_record())

    def test_revert_cancel_preserves_draft(self):
        self.e.dirty = True
        self.dialogs.askyesno.return_value = False
        self.e.update = Mock()
        self.e.revert_source()
        self.e.update.assert_not_called()

    def test_revert_read_failure_preserves_draft(self):
        self.e.dirty = True
        self.dialogs.askyesno.return_value = True
        self.path.unlink()
        self.e.revert_source()
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_multiple_delete_blocked(self):
        self.e.remove()
        self.e.candidate_valid.assert_not_called()

    def test_single_delete_is_draft_only(self):
        self.e.tree.selection.return_value = ("CAP::Q1",)
        self.e.editing_key = ("CAP", "Q1")
        self.dialogs.askyesno.return_value = True
        original_bytes = self.path.read_bytes()
        self.e.remove()
        self.assertEqual(len(self.e.loaded_rows), 2)
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.path.read_bytes(), original_bytes)

    def test_delete_validation_failure_preserves_draft(self):
        self.e.tree.selection.return_value = ("CAP::Q1",)
        self.e.editing_key = ("CAP", "Q1")
        self.dialogs.askyesno.return_value = True
        self.e.candidate_valid.return_value = (False, "FAIL")
        self.e.remove()
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_duplicate_and_invalid_boolean_rejected(self):
        with self.assertRaises(ValueError):
            self.e.validate_rows([self.rows[0], self.rows[0]])
        with self.assertRaises(ValueError):
            self.e.validate_rows([{**self.rows[0], "active": "maybe"}])


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Mock()
        self.app = NS(
            capability_staffing_rules_editor=NS(dirty=True),
            _network_close_handler=self.previous, protocol=Mock(), destroy=Mock()
        )
        self.dialogs = Mock()

    def test_close_cancel_does_not_delegate(self):
        self.dialogs.askyesno.return_value = False
        policy.install_capability_staffing_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()

    def test_close_confirm_delegates_existing_chain(self):
        self.dialogs.askyesno.return_value = True
        policy.install_capability_staffing_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.app.destroy.assert_not_called()

    def test_clean_close_has_no_extra_prompt(self):
        self.app.capability_staffing_rules_editor.dirty = False
        policy.install_capability_staffing_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_dirty_project_switch_blocked(self):
        self.assertFalse(policy.allow_capability_staffing_project_change(self.app, self.dialogs))

    def test_clean_project_switch_allowed(self):
        self.app.capability_staffing_rules_editor.dirty = False
        self.assertTrue(policy.allow_capability_staffing_project_change(self.app, self.dialogs))

    def test_install_idempotent(self):
        policy.install_capability_staffing_draft_close_guard(self.app, self.dialogs)
        first = self.app._network_close_handler
        policy.install_capability_staffing_draft_close_guard(self.app, self.dialogs)
        self.assertIs(first, self.app._network_close_handler)
        self.app.protocol.assert_called_once()

    def test_project_guard_precedes_picker(self):
        with patch.object(gui, "allow_capability_staffing_project_change", return_value=False), \
             patch.object(gui.filedialog, "askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()

    def test_file_exit_uses_existing_guard(self):
        self.dialogs.askyesno.return_value = False
        policy.install_capability_staffing_draft_close_guard(self.app, self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()