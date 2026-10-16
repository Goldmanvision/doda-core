import copy
import csv
import os
import shutil
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from tkinter import ttk
from types import SimpleNamespace as NS
from unittest.mock import Mock, patch

import doda_flavor_text_editor as module
import doda_flavor_text_draft_policy as policy
import doda_content_gui as gui

LIVE = Path(os.environ.get(
    "DODA_V133_LIVE_MODULE", str(Path(module.__file__).resolve().parent)
)).resolve()
SOURCE = LIVE.parents[1] / "data_authoring" / "source"


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write(path, fields, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


class Fixture(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="v133-staged-")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)
        self.src = self.folder / "data_authoring" / "source"
        self.src.mkdir(parents=True)
        for name in module.FILES:
            shutil.copy2(SOURCE / name, self.src / name)
        root = self.app = tk.Tk()
        self.addCleanup(root.destroy)
        root.withdraw()
        root.project_root = self.folder
        root.source_directory = self.src
        root.validator_path = LIVE / "doda_content_workbench.py"
        root.tables = {"flavor_text": read(self.src / "flavor_text.csv")}
        root.log = Mock()
        root.refresh_all = Mock()
        root.flavor_tab = ttk.Frame(root)
        self.e = module.FlavorTextEditor(root)
        self.e.update()
        root.update_idletasks()
        self.rows = copy.deepcopy(self.e.loaded_rows)
        self.ids = tuple(row["flavor_text_id"] for row in self.rows)
        self.path = self.src / "flavor_text.csv"
        self.e.candidate_valid = Mock(return_value=(True, "PASS"))
        self.dialog_patch = patch.object(module, "messagebox")
        self.dialogs = self.dialog_patch.start()
        self.addCleanup(self.dialog_patch.stop)

    def select(self, count=2):
        ids = self.ids[:count]
        self.e.tree.selection_set(*ids)
        self.e.on_select(force=True)
        return ids

    def set_body(self, text):
        self.e.body.delete("1.0", "end")
        self.e.body.insert("1.0", text)

    def by_id(self):
        return {row["flavor_text_id"]: row for row in self.e.loaded_rows}


class DraftTests(Fixture):
    def test_schema_and_real_source_loading(self):
        self.assertEqual(tuple(self.rows[0]), module.FIELDS)
        self.assertEqual(len(module.FIELDS), 5)
        self.assertNotIn("sort_order", module.FIELDS)
        self.assertEqual(module.IDENTITY, ("flavor_text_id",))
        self.assertEqual(str(self.e.tree["selectmode"]), "extended")

    def test_exact_list_column_alignment(self):
        columns = tuple(self.e.tree["columns"])
        self.assertEqual(columns, (
            "flavor_text_id", "category", "title", "active",
        ))
        for row in self.rows:
            values = tuple(map(str, self.e.tree.item(row["flavor_text_id"], "values")))
            self.assertEqual(values, tuple(row[f] for f in columns))

    def test_selection_load_does_not_create_edits(self):
        self.select()
        self.app.update_idletasks()
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)
        self.assertEqual(str(self.e.widgets["flavor_text_id"].cget("state")), "disabled")

    def test_untouched_apply_skips_validation(self):
        self.select()
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_batch_changes_selected_rows_and_field_only(self):
        selected = self.select()
        before = self.path.read_bytes()
        self.e.vars["title"].set("Temporary name")
        self.assertTrue(self.e.apply_record())
        for old, current in zip(self.rows, self.e.loaded_rows):
            expected = {**old, "title": "Temporary name"} if old["flavor_text_id"] in selected else old
            self.assertEqual(current, expected)
        self.assertEqual(self.e.tree.selection(), selected)
        self.assertEqual(self.path.read_bytes(), before)

    def test_body_immediate_apply(self):
        selected = self.select()
        self.set_body("Temporary body")
        self.assertTrue(self.e.apply_record())
        for row in self.e.loaded_rows:
            original = next(r for r in self.rows if r["flavor_text_id"] == row["flavor_text_id"])
            expected = "Temporary body" if row["flavor_text_id"] in selected else original["body"]
            self.assertEqual(row["body"], expected)

    def test_same_selection_preserves_pending_text(self):
        self.select()
        self.set_body("Pending body")
        self.e.on_select()
        self.assertEqual(self.e.body.get("1.0", "end-1c"), "Pending body")

    def test_double_refresh_preserves_pending_single_entry(self):
        selected = self.select(1)
        self.e.vars["title"].set("Pending name")
        self.e.update()
        self.e.update()
        self.assertEqual(self.e.vars["title"].get(), "Pending name")
        self.assertEqual(self.e.tree.selection(), selected)

    def test_double_refresh_preserves_pending_body(self):
        self.select()
        self.set_body("Pending body")
        self.e.update()
        self.e.update()
        self.assertEqual(self.e.body.get("1.0", "end-1c"), "Pending body")

    def test_dirty_refresh_retains_draft_and_snapshot(self):
        self.select(1)
        self.e.vars["title"].set("Applied draft")
        self.assertTrue(self.e.apply_record())
        expected = copy.deepcopy(self.e.loaded_rows)
        snapshot = self.e.snapshot_hash
        self.path.write_text("external", encoding="utf-8")
        self.e.update()
        self.assertEqual(self.e.loaded_rows, expected)
        self.assertEqual(self.e.snapshot_hash, snapshot)

    def test_clean_refresh_loads_external_change(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["title"] = "External"
        self.e.write(self.path, rows)
        self.e.update()
        self.assertEqual(self.e.loaded_rows, rows)

    def test_required_fields_reject_atomically(self):
        self.select()
        for field in ("category", "title", "body"):
            with self.subTest(field=field):
                self.e._changes = {field: ""}
                self.assertFalse(self.e.apply_record())
                self.assertEqual(self.e.loaded_rows, self.rows)

    def test_invalid_values_reject_atomically(self):
        self.select()
        for field, value in (
            ("active", "maybe"), ("category", "Multiple values"),
            ("title", "Multiple values"), ("body", "Multiple values"),
        ):
            with self.subTest(field=field, value=value):
                self.e._changes = {field: value}
                self.assertFalse(self.e.apply_record())
                self.assertEqual(self.e.loaded_rows, self.rows)

    def test_single_identity_change_rejected(self):
        self.select(1)
        self.e.vars["flavor_text_id"].set("OTHER")
        self.assertFalse(self.e.apply_record())

    def test_batch_identity_injection_rejected(self):
        self.select()
        self.e._changes = {"flavor_text_id": "OTHER"}
        self.assertFalse(self.e.apply_record())

    def test_single_apply_preserves_row_order(self):
        self.select(1)
        self.e.vars["title"].set("Temporary edited title")
        self.assertTrue(self.e.apply_record())
        self.assertEqual(tuple(r["flavor_text_id"] for r in self.e.loaded_rows), self.ids)

    def test_new_unique_record_is_draft_only(self):
        before = self.path.read_bytes()
        self.e.new()
        row = {**self.rows[0], "flavor_text_id": "V133_TEMP_FLAVOR", "active": "FALSE"}
        for field, value in row.items():
            self.e.vars[field].set(value)
        self.set_body(row["body"])
        self.assertTrue(self.e.apply_record())
        self.assertIn(row["flavor_text_id"], self.by_id())
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_duplicate_rejected(self):
        self.e.new()
        for field, value in self.rows[0].items():
            self.e.vars[field].set(value)
        self.set_body(self.rows[0]["body"])
        self.assertFalse(self.e.apply_record())

    def test_stale_selection_rejected(self):
        self.select()
        self.e.tree.selection_set(self.ids[0], self.ids[2])
        self.e._changes = {"title": "Changed"}
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_draft_mutation_during_validation_blocks_apply(self):
        self.select()
        self.e._changes = {"title": "Changed"}
        def validate(_path):
            self.e.loaded_rows[-1]["title"] = "External draft mutation"
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.by_id()[self.ids[0]], self.rows[0])

    def test_candidate_failure_preserves_draft(self):
        self.select()
        self.e._changes = {"title": "Changed"}
        self.e.candidate_valid.return_value = (False, "FAIL")
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_multi_delete_blocked(self):
        self.select()
        self.assertFalse(self.e.remove())
        self.e.candidate_valid.assert_not_called()

    def test_single_delete_is_draft_only(self):
        self.select(1)
        before = self.path.read_bytes()
        self.dialogs.askyesno.return_value = True
        self.assertTrue(self.e.remove())
        self.assertNotIn(self.ids[0], self.by_id())
        self.assertEqual(self.path.read_bytes(), before)

    def test_delete_validation_failure_is_atomic(self):
        self.select(1)
        self.dialogs.askyesno.return_value = True
        self.e.candidate_valid.return_value = (False, "referenced")
        self.assertFalse(self.e.remove())
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_save_without_apply_does_not_commit(self):
        self.e.commit = Mock()
        self.assertFalse(self.e.save())
        self.e.commit.assert_not_called()

    def test_save_uses_draft_not_pending_form(self):
        self.e.dirty = True
        self.set_body("Unapplied")
        self.e.commit = Mock()
        self.assertTrue(self.e.save())
        self.e.commit.assert_called_once_with(self.e.loaded_rows)
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_save_creates_original_backup(self):
        original = self.path.read_bytes()
        self.e.loaded_rows[0]["title"] = "Saved name"
        self.e.dirty = True
        self.assertTrue(self.e.save())
        backups = list(self.e.backup_directory().glob("*.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual({r["flavor_text_id"]: r for r in read(self.path)}[self.ids[0]]["title"], "Saved name")
        self.assertFalse(self.e.dirty)

    def test_external_change_blocks_save(self):
        self.e.dirty = True
        self.path.write_text("external", encoding="utf-8")
        self.assertFalse(self.e.save())
        self.e.candidate_valid.assert_not_called()
        self.assertTrue(self.e.dirty)

    def test_source_change_during_validation_blocks_save(self):
        self.e.dirty = True
        def validate(_path):
            self.path.write_text("external", encoding="utf-8")
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_text(), "external")

    def test_backup_and_replace_failures_retain_source(self):
        original = self.path.read_bytes()
        self.e.dirty = True
        with patch.object(module.shutil, "copy2", side_effect=OSError("backup failed")):
            self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), original)
        with patch.object(module.os, "replace", side_effect=OSError("replace failed")):
            self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), original)
        self.assertTrue(self.e.dirty)

    def test_dependency_change_during_backup_blocks_save(self):
        dependency = self.src / "facilities.csv"
        self.e._validated_dependencies = {dependency.resolve(): self.e.digest(dependency)}
        self.e.dirty = True
        original = self.path.read_bytes()
        real_copy = module.shutil.copy2
        def backup(source, destination):
            result = real_copy(source, destination)
            with dependency.open("a", encoding="utf-8") as handle:
                handle.write("\n")
            return result
        with patch.object(module.shutil, "copy2", side_effect=backup):
            self.assertFalse(self.e.save())
        self.assertEqual(self.path.read_bytes(), original)

    def test_revert_form_and_cancel_draft_revert(self):
        self.select()
        original = self.e.body.get("1.0", "end-1c")
        self.set_body("Pending")
        self.e.revert()
        self.assertEqual(self.e.body.get("1.0", "end-1c"), original)
        self.e.dirty = True
        self.dialogs.askyesno.return_value = False
        self.assertFalse(self.e.revert_source())
        self.assertTrue(self.e.dirty)

    def test_revert_draft_reloads_source(self):
        self.e.loaded_rows[0]["title"] = "Draft"
        self.e.dirty = True
        self.dialogs.askyesno.return_value = True
        self.assertTrue(self.e.revert_source())
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_dirty_cross_project_refresh_blocked(self):
        self.e.dirty = True
        self.e.loaded_path = self.folder / "other.csv"
        with self.assertRaises(ValueError):
            self.e.update()

    def test_installer_preserves_refresh_alias(self):
        module.install_flavor_text_editor(self.app)
        self.assertIs(self.app.update_flavor_text.__self__, self.app.flavor_text_editor)
        self.assertIs(self.app.update_flavor_text.__func__, module.FlavorTextEditor.update)


    def test_category_remains_editable_and_accepts_new_value(self):
        selected = self.select()
        self.assertEqual(str(self.e.widgets["category"].cget("state")), "normal")
        self.e.vars["category"].set("V133_CUSTOM_CATEGORY")
        self.assertTrue(self.e.apply_record())
        for row in self.e.loaded_rows:
            original = next(r for r in self.rows if r["flavor_text_id"] == row["flavor_text_id"])
            expected = "V133_CUSTOM_CATEGORY" if row["flavor_text_id"] in selected else original["category"]
            self.assertEqual(row["category"], expected)
        self.assertIn("V133_CUSTOM_CATEGORY", self.e.categories())

    def test_multiline_unicode_body_preserved_through_apply_and_save(self):
        selected = self.select(1)
        body = '  First line,\n"Quoted" text\nCaf\u00e9 \u03a9\n  '
        self.set_body(body)
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.by_id()[selected[0]]["body"], body)
        self.assertTrue(self.e.save())
        saved = {r["flavor_text_id"]: r for r in read(self.path)}
        self.assertEqual(saved[selected[0]]["body"], body)

    def test_long_title_shortened_only_in_list(self):
        selected = self.select(1)
        title = "Long title " * 11 + "end"
        self.e.vars["title"].set(title)
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.by_id()[selected[0]]["title"], title)
        self.assertEqual(self.e.vars["title"].get(), title)
        shown = self.e.tree.item(selected[0], "values")[2]
        self.assertEqual(len(shown), 70)
        self.assertTrue(shown.endswith("..."))

    def test_body_placeholder_focus_does_not_create_edit(self):
        self.select()
        self.e.select_placeholder("body")
        self.app.update_idletasks()
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)

    def test_csv_writer_preserves_row_order_and_field_values(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["body"] = '  A,\n"B"\nCaf\u00e9  '
        path = self.folder / "roundtrip.csv"
        self.e.write(path, rows)
        self.assertEqual(read(path), rows)

class ValidatorTests(Fixture):
    def validate(self, rows=None):
        candidate = self.folder / "candidate.csv"
        write(candidate, module.FIELDS, self.rows if rows is None else rows)
        return module.FlavorTextEditor.candidate_valid(self.e, candidate)

    def referenced_id(self):
        return read(self.src / "metric_tiers.csv")[0]["flavor_text_id"]

    def test_current_source_passes_actual_validator(self):
        valid, output = self.validate()
        self.assertTrue(valid, output)

    def test_referenced_flavor_deletion_rejected(self):
        fid = self.referenced_id()
        valid, output = self.validate([r for r in self.rows if r["flavor_text_id"] != fid])
        self.assertFalse(valid, output)
        self.assertIn(fid, output)

    def test_referenced_flavor_deactivation_rejected(self):
        fid = self.referenced_id()
        rows = [{**r, "active": "FALSE"} if r["flavor_text_id"] == fid else dict(r) for r in self.rows]
        self.assertFalse(self.validate(rows)[0])

    def test_duplicate_flavor_id_rejected(self):
        self.assertFalse(self.validate(self.rows + [dict(self.rows[0])])[0])

    def test_new_unreferenced_inactive_flavor_is_valid(self):
        row = {**self.rows[0], "flavor_text_id": "V133_UNUSED_TEST_FLAVOR", "active": "FALSE"}
        valid, output = self.validate(self.rows + [row])
        self.assertTrue(valid, output)

    def test_body_edit_preserves_metric_tier_references(self):
        fid = self.referenced_id()
        rows = [{**r, "body": "New body.\nSecond line."} if r["flavor_text_id"] == fid else dict(r) for r in self.rows]
        valid, output = self.validate(rows)
        self.assertTrue(valid, output)

    def test_dependency_change_during_validation_rejected(self):
        candidate = self.folder / "candidate.csv"
        write(candidate, module.FIELDS, self.rows)
        dependency = self.src / "metric_tiers.csv"
        def validate(*_args, **_kwargs):
            with dependency.open("a", encoding="utf-8") as handle:
                handle.write("\n")
            return NS(returncode=0, stdout="PASS", stderr="")
        with patch.object(module.subprocess, "run", side_effect=validate):
            with self.assertRaisesRegex(ValueError, "changed during validation"):
                module.FlavorTextEditor.candidate_valid(self.e, candidate)

    def test_complete_validation_dependency_list_preserved(self):
        from doda_task_templates_editor import FILES
        self.assertEqual(module.FILES, tuple(FILES))

class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Mock()
        self.app = NS(
            flavor_text_editor=NS(dirty=True), _network_close_handler=self.previous,
            protocol=Mock(), destroy=Mock(),
        )
        self.dialogs = Mock()

    def test_close_cancel_stops_chain(self):
        self.dialogs.askyesno.return_value = False
        policy.install_flavor_text_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()

    def test_close_accept_delegates_and_preserves_draft_flag(self):
        self.dialogs.askyesno.return_value = True
        policy.install_flavor_text_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.assertTrue(self.app.flavor_text_editor.dirty)

    def test_clean_close_adds_no_prompt(self):
        self.app.flavor_text_editor.dirty = False
        policy.install_flavor_text_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_project_change_guard(self):
        self.assertFalse(policy.allow_flavor_text_project_change(self.app, self.dialogs))
        self.app.flavor_text_editor.dirty = False
        self.assertTrue(policy.allow_flavor_text_project_change(self.app, self.dialogs))

    def test_guard_installation_is_idempotent(self):
        policy.install_flavor_text_draft_close_guard(self.app, self.dialogs)
        first = self.app._network_close_handler
        policy.install_flavor_text_draft_close_guard(self.app, self.dialogs)
        self.assertIs(self.app._network_close_handler, first)
        self.app.protocol.assert_called_once()

    def test_file_exit_uses_guard(self):
        self.dialogs.askyesno.return_value = False
        policy.install_flavor_text_draft_close_guard(self.app, self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()

    def test_project_guard_precedes_picker(self):
        with patch.object(gui, "allow_flavor_text_project_change", return_value=False), \
             patch.object(gui.filedialog, "askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()