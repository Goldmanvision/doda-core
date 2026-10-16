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

import doda_enum_catalog_editor as module
import doda_enum_catalog_draft_policy as policy
import doda_content_gui as gui

LIVE = Path(os.environ.get(
    "DODA_V134_LIVE_MODULE", str(Path(module.__file__).resolve().parent)
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
        self.temp = tempfile.TemporaryDirectory(prefix="v134-staged-")
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
        root.tables = {"enum_catalog": read(self.src / "enum_catalog.csv")}
        root.log = Mock()
        root.refresh_all = Mock()
        root.notebook = ttk.Notebook(root)
        self.e = module.EnumCatalogEditor(root)
        self.e.update()
        root.update_idletasks()
        self.rows = copy.deepcopy(self.e.loaded_rows)
        self.ids = tuple(module.row_iid(row) for row in self.rows)
        self.path = self.src / "enum_catalog.csv"
        self.e.candidate_valid = Mock(return_value=(True, "PASS"))
        self.dialog_patch = patch.object(module, "messagebox")
        self.dialogs = self.dialog_patch.start()
        self.addCleanup(self.dialog_patch.stop)

    def select(self, count=2):
        ids = self.ids[:count]
        self.e.tree.selection_set(*ids)
        self.e.on_select(force=True)
        return ids

    def set_description(self, text):
        self.e.description.delete("1.0", "end")
        self.e.description.insert("1.0", text)

    def by_id(self):
        return {module.row_iid(row): row for row in self.e.loaded_rows}


class DraftTests(Fixture):
    def test_schema_and_real_source_loading(self):
        self.assertEqual(tuple(self.rows[0]), module.FIELDS)
        self.assertEqual(len(module.FIELDS), 6)
        self.assertEqual(module.IDENTITY, ("enum_group", "enum_value"))
        self.assertEqual(module.EDITABLE, ("display_label", "description", "sort_order", "active"))
        self.assertEqual(str(self.e.tree["selectmode"]), "extended")

    def test_exact_list_column_alignment(self):
        columns = tuple(self.e.tree["columns"])
        self.assertEqual(columns, ("enum_group", "enum_value", "display_label", "sort_order", "active"))
        for row in self.rows:
            values = tuple(map(str, self.e.tree.item(module.row_iid(row), "values")))
            self.assertEqual(values, tuple(row[f] for f in columns))

    def test_selection_load_does_not_create_edits(self):
        self.select()
        self.app.update_idletasks()
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)
        for field in module.IDENTITY:
            self.assertEqual(str(self.e.widgets[field].cget("state")), "disabled")

    def test_untouched_apply_skips_validation(self):
        self.select()
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_batch_changes_selected_rows_and_field_only(self):
        selected = self.select()
        before = self.path.read_bytes()
        self.e.vars["display_label"].set("Temporary name")
        self.assertTrue(self.e.apply_record())
        for old, current in zip(self.rows, self.e.loaded_rows):
            expected = {**old, "display_label": "Temporary name"} if module.row_iid(old) in selected else old
            self.assertEqual(current, expected)
        self.assertEqual(self.e.tree.selection(), selected)
        self.assertEqual(self.path.read_bytes(), before)

    def test_description_immediate_apply(self):
        selected = self.select()
        self.set_description("Temporary description")
        self.assertTrue(self.e.apply_record())
        for row in self.e.loaded_rows:
            original = next(r for r in self.rows if module.row_key(r) == module.row_key(row))
            expected = "Temporary description" if module.row_iid(row) in selected else original["description"]
            self.assertEqual(row["description"], expected)

    def test_same_selection_preserves_pending_text(self):
        self.select()
        self.set_description("Pending description")
        self.e.on_select()
        self.assertEqual(self.e.description.get("1.0", "end-1c"), "Pending description")

    def test_double_refresh_preserves_pending_single_entry(self):
        selected = self.select(1)
        self.e.vars["display_label"].set("Pending name")
        self.e.update()
        self.e.update()
        self.assertEqual(self.e.vars["display_label"].get(), "Pending name")
        self.assertEqual(self.e.tree.selection(), selected)

    def test_double_refresh_preserves_pending_description(self):
        self.select()
        self.set_description("Pending description")
        self.e.update()
        self.e.update()
        self.assertEqual(self.e.description.get("1.0", "end-1c"), "Pending description")

    def test_dirty_refresh_retains_draft_and_snapshot(self):
        self.select(1)
        self.e.vars["display_label"].set("Applied draft")
        self.assertTrue(self.e.apply_record())
        expected = copy.deepcopy(self.e.loaded_rows)
        snapshot = self.e.snapshot_hash
        self.path.write_text("external", encoding="utf-8")
        self.e.update()
        self.assertEqual(self.e.loaded_rows, expected)
        self.assertEqual(self.e.snapshot_hash, snapshot)

    def test_clean_refresh_loads_external_change(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["display_label"] = "External"
        self.e.write(self.path, rows)
        self.e.update()
        self.assertEqual(self.e.loaded_rows, rows)

    def test_required_fields_reject_atomically(self):
        self.select()
        for field in ("display_label", "description"):
            with self.subTest(field=field):
                self.e._changes = {field: ""}
                self.assertFalse(self.e.apply_record())
                self.assertEqual(self.e.loaded_rows, self.rows)

    def test_invalid_values_reject_atomically(self):
        self.select()
        for field, value in (
            ("active", "maybe"), ("sort_order", "-1"), ("sort_order", "1.5"),
            ("sort_order", "bad"), ("display_label", "Multiple values"),
            ("description", "Multiple values"),
        ):
            with self.subTest(field=field, value=value):
                self.e._changes = {field: value}
                self.assertFalse(self.e.apply_record())
                self.assertEqual(self.e.loaded_rows, self.rows)

    def test_single_identity_change_rejected(self):
        for field in module.IDENTITY:
            with self.subTest(field=field):
                self.select(1)
                self.e.vars[field].set("OTHER")
                self.assertFalse(self.e.apply_record())
                self.assertEqual(self.e.loaded_rows, self.rows)

    def test_batch_identity_injection_rejected(self):
        self.select()
        for field in module.IDENTITY:
            self.e._changes = {field: "OTHER"}
            self.assertFalse(self.e.apply_record())
            self.assertEqual(self.e.loaded_rows, self.rows)

    def test_single_apply_preserves_row_order(self):
        self.select(1)
        self.e.vars["display_label"].set("Temporary edited title")
        self.assertTrue(self.e.apply_record())
        self.assertEqual(tuple(module.row_iid(r) for r in self.e.loaded_rows), self.ids)

    def test_new_unique_record_is_draft_only(self):
        before = self.path.read_bytes()
        self.e.new()
        row = {**self.rows[0], "enum_value": "V134_TEMP_ENUM", "active": "FALSE"}
        for field, value in row.items():
            self.e.vars[field].set(value)
        self.set_description(row["description"])
        self.assertTrue(self.e.apply_record())
        self.assertIn(module.row_iid(row), self.by_id())
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_duplicate_rejected(self):
        self.e.new()
        for field, value in self.rows[0].items():
            self.e.vars[field].set(value)
        self.set_description(self.rows[0]["description"])
        self.assertFalse(self.e.apply_record())

    def test_stale_selection_rejected(self):
        self.select()
        self.e.tree.selection_set(self.ids[0], self.ids[2])
        self.e._changes = {"display_label": "Changed"}
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_draft_mutation_during_validation_blocks_apply(self):
        self.select()
        self.e._changes = {"display_label": "Changed"}
        def validate(_path):
            self.e.loaded_rows[-1]["display_label"] = "External draft mutation"
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.by_id()[self.ids[0]], self.rows[0])

    def test_candidate_failure_preserves_draft(self):
        self.select()
        self.e._changes = {"display_label": "Changed"}
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
        self.set_description("Unapplied")
        self.e.commit = Mock()
        self.assertTrue(self.e.save())
        self.e.commit.assert_called_once_with(self.e.loaded_rows)
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_save_creates_original_backup(self):
        original = self.path.read_bytes()
        self.e.loaded_rows[0]["display_label"] = "Saved name"
        self.e.dirty = True
        self.assertTrue(self.e.save())
        backups = list(self.e.backup_directory().glob("*.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual({module.row_iid(r): r for r in read(self.path)}[self.ids[0]]["display_label"], "Saved name")
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
        original = self.e.description.get("1.0", "end-1c")
        self.set_description("Pending")
        self.e.revert()
        self.assertEqual(self.e.description.get("1.0", "end-1c"), original)
        self.e.dirty = True
        self.dialogs.askyesno.return_value = False
        self.assertFalse(self.e.revert_source())
        self.assertTrue(self.e.dirty)

    def test_revert_draft_reloads_source(self):
        self.e.loaded_rows[0]["display_label"] = "Draft"
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
        module.install_enum_catalog_editor(self.app)
        self.assertIs(self.app.update_enum_catalog.__self__, self.app.enum_catalog_editor)
        self.assertIs(self.app.update_enum_catalog.__func__, module.EnumCatalogEditor.update)


    def test_new_identity_choices_remain_editable(self):
        self.e.new()
        for field in module.IDENTITY:
            self.assertEqual(str(self.e.widgets[field].cget("state")), "normal")
        self.e.vars["enum_group"].set("V134_CUSTOM_GROUP")
        self.e.vars["enum_value"].set("V134_CUSTOM_VALUE")
        self.e.vars["display_label"].set("Temporary label")
        self.set_description("Temporary description")
        self.e.vars["sort_order"].set("0")
        self.assertTrue(self.e.apply_record())
        self.assertIn("V134_CUSTOM_GROUP", self.e.groups())
        self.assertIn("V134_CUSTOM_VALUE", self.e.values_for_group("V134_CUSTOM_GROUP"))
        for field in module.IDENTITY:
            self.assertEqual(str(self.e.widgets[field].cget("state")), "disabled")

    def test_multiline_unicode_description_preserved_through_apply_and_save(self):
        selected = self.select(1)
        description = '  First line,\n"Quoted" text\nCaf\u00e9 \u03a9\n  '
        self.set_description(description)
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.by_id()[selected[0]]["description"], description)
        self.assertTrue(self.e.save())
        saved = {module.row_iid(r): r for r in read(self.path)}
        self.assertEqual(saved[selected[0]]["description"], description)

    def test_long_display_label_is_not_truncated(self):
        selected = self.select(1)
        label = "Long label " * 11 + "end"
        self.e.vars["display_label"].set(label)
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.by_id()[selected[0]]["display_label"], label)
        self.assertEqual(self.e.vars["display_label"].get(), label)
        self.assertEqual(self.e.tree.item(selected[0], "values")[2], label)

    def test_description_placeholder_focus_does_not_create_edit(self):
        self.select()
        self.e.select_placeholder("description")
        self.app.update_idletasks()
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)

    def test_csv_writer_preserves_row_order_and_field_values(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["description"] = '  A,\n"B"\nCaf\u00e9  '
        path = self.folder / "roundtrip.csv"
        self.e.write(path, rows)
        self.assertEqual(read(path), rows)

    def test_duplicate_value_across_groups_allowed(self):
        rows = copy.deepcopy(self.rows)
        rows.append({**rows[0], "enum_group": "V134_OTHER_GROUP"})
        self.e.validate_rows(rows)

    def test_duplicate_pair_local_rejected(self):
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            self.e.validate_rows(self.rows + [dict(self.rows[0])])

    def test_new_pair_uses_both_identity_fields(self):
        self.e.new()
        row = {**self.rows[0], "enum_group": "V134_OTHER_GROUP"}
        for field, value in row.items():
            self.e.vars[field].set(value)
        self.set_description(row["description"])
        self.assertTrue(self.e.apply_record())
        self.assertIn(module.row_iid(row), self.by_id())
        self.assertIn(self.ids[0], self.by_id())

    def test_zero_sort_order_allowed(self):
        selected = self.select(2)
        self.e.vars["sort_order"].set("0")
        self.assertTrue(self.e.apply_record())
        for iid in selected:
            self.assertEqual(self.by_id()[iid]["sort_order"], "0")

    def test_negative_and_noninteger_sort_reject(self):
        for value in ("-1", "1.5", "bad", ""):
            rows = copy.deepcopy(self.rows)
            rows[0]["sort_order"] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.e.validate_rows(rows)

    def test_filter_limits_view_without_changing_draft(self):
        group = self.rows[0]["enum_group"]
        self.e.catalog_group_filter.set(group)
        self.assertTrue(self.e.on_catalog_group_filter_changed())
        expected = {module.row_iid(r) for r in self.rows if r["enum_group"] == group}
        self.assertEqual(set(self.e.tree.get_children()), expected)
        self.assertEqual(self.e.loaded_rows, self.rows)
        self.assertFalse(self.e.dirty)

    def test_filter_retains_applied_changes(self):
        selected = self.select(1)
        self.e.vars["display_label"].set("Applied label")
        self.assertTrue(self.e.apply_record())
        expected = copy.deepcopy(self.e.loaded_rows)
        other = next(g for g in self.e.groups() if g != self.rows[0]["enum_group"])
        self.e.catalog_group_filter.set(other)
        self.assertTrue(self.e.on_catalog_group_filter_changed())
        self.e.catalog_group_filter.set("All Groups")
        self.assertTrue(self.e.on_catalog_group_filter_changed())
        self.assertEqual(self.e.loaded_rows, expected)
        self.assertTrue(self.e.dirty)
        self.assertEqual(self.by_id()[selected[0]]["display_label"], "Applied label")

    def test_filter_blocks_pending_single_entry(self):
        selected = self.select(1)
        self.e.vars["display_label"].set("Pending")
        self.e.catalog_group_filter.set(self.e.groups()[0])
        self.assertFalse(self.e.on_catalog_group_filter_changed())
        self.assertEqual(self.e.catalog_group_filter.get(), "All Groups")
        self.assertEqual(self.e.vars["display_label"].get(), "Pending")
        self.assertEqual(self.e.tree.selection(), selected)

    def test_filter_blocks_pending_description(self):
        selected = self.select(2)
        self.set_description("Pending description")
        self.e.catalog_group_filter.set(self.e.groups()[0])
        self.assertFalse(self.e.on_catalog_group_filter_changed())
        self.assertEqual(self.e.description.get("1.0", "end-1c"), "Pending description")
        self.assertEqual(self.e.tree.selection(), selected)

    def test_filter_blocks_pending_new_record(self):
        self.e.new()
        self.e.vars["enum_value"].set("V134_PENDING_VALUE")
        self.e.catalog_group_filter.set(self.e.groups()[0])
        self.assertFalse(self.e.on_catalog_group_filter_changed())
        self.assertEqual(self.e.vars["enum_value"].get(), "V134_PENDING_VALUE")

    def test_filter_noop_preserves_pending_text(self):
        self.select(1)
        self.set_description("Pending")
        self.assertTrue(self.e.on_catalog_group_filter_changed())
        self.assertEqual(self.e.description.get("1.0", "end-1c"), "Pending")

    def test_new_record_in_other_group_is_revealed(self):
        self.e.catalog_group_filter.set(self.rows[0]["enum_group"])
        self.assertTrue(self.e.on_catalog_group_filter_changed())
        self.e.new()
        row = {**self.rows[0], "enum_group": "V134_OTHER_GROUP"}
        for field, value in row.items():
            self.e.vars[field].set(value)
        self.set_description(row["description"])
        self.assertTrue(self.e.apply_record())
        self.assertEqual(self.e.catalog_group_filter.get(), row["enum_group"])
        self.assertEqual(self.e.tree.selection(), (module.row_iid(row),))

    def test_new_sort_order_scoped_to_group(self):
        group = self.rows[0]["enum_group"]
        self.e.catalog_group_filter.set(group)
        self.assertTrue(self.e.on_catalog_group_filter_changed())
        self.e.new()
        expected = max(int(r["sort_order"]) for r in self.rows if r["enum_group"] == group) + 1
        self.assertEqual(self.e.vars["enum_group"].get(), group)
        self.assertEqual(self.e.vars["sort_order"].get(), str(expected))

    def test_cross_group_batch_preserves_identity(self):
        first = self.rows[0]
        second = next(r for r in self.rows if r["enum_group"] != first["enum_group"])
        selected = {module.row_iid(first), module.row_iid(second)}
        self.e.tree.selection_set(*selected)
        self.e.on_select(force=True)
        self.e.vars["display_label"].set("Cross-group label")
        self.assertTrue(self.e.apply_record())
        for old, row in zip(self.rows, self.e.loaded_rows):
            expected = {**old, "display_label": "Cross-group label"} if module.row_iid(old) in selected else old
            self.assertEqual(row, expected)

    def test_same_value_different_group_iids_distinct(self):
        first = dict(self.rows[0])
        second = {**first, "enum_group": "V134_OTHER_GROUP"}
        self.assertNotEqual(module.row_key(first), module.row_key(second))
        self.assertNotEqual(module.row_iid(first), module.row_iid(second))

class ValidatorTests(Fixture):
    def validate(self, rows=None):
        candidate = self.folder / "candidate.csv"
        write(candidate, module.FIELDS, self.rows if rows is None else rows)
        return module.EnumCatalogEditor.candidate_valid(self.e, candidate)

    def referenced_keys(self):
        facility = read(self.src / "facilities.csv")[0]
        metric = read(self.src / "metrics.csv")[0]
        return {
            ("FACILITY_TIER", facility["initial_tier_id"]),
            ("METRIC_POLARITY", metric["polarity"]),
            ("METRIC_DISPLAY_MODE", metric["ui_display_mode"]),
        }

    def test_current_source_passes_actual_validator(self):
        valid, output = self.validate()
        self.assertTrue(valid, output)

    def test_referenced_enum_deletion_rejected(self):
        for key in self.referenced_keys():
            with self.subTest(key=key):
                valid, output = self.validate([r for r in self.rows if module.row_key(r) != key])
                self.assertFalse(valid, output)
                self.assertIn(key[1], output)

    def test_referenced_enum_deactivation_rejected(self):
        for key in self.referenced_keys():
            with self.subTest(key=key):
                rows = [{**r, "active": "FALSE"} if module.row_key(r) == key else dict(r) for r in self.rows]
                self.assertFalse(self.validate(rows)[0])

    def test_duplicate_pair_rejected(self):
        self.assertFalse(self.validate(self.rows + [dict(self.rows[0])])[0])

    def test_new_unreferenced_inactive_pair_is_valid(self):
        row = {
            **self.rows[0], "enum_group": "V134_UNUSED_GROUP",
            "enum_value": "V134_UNUSED_VALUE", "sort_order": "0", "active": "FALSE",
        }
        valid, output = self.validate(self.rows + [row])
        self.assertTrue(valid, output)

    def test_metadata_and_zero_sort_preserve_references(self):
        rows = copy.deepcopy(self.rows)
        rows[0].update(display_label="New label", description="New description.\nSecond line.", sort_order="0")
        valid, output = self.validate(rows)
        self.assertTrue(valid, output)

    def test_dependency_change_during_validation_rejected(self):
        candidate = self.folder / "candidate.csv"
        write(candidate, module.FIELDS, self.rows)
        dependency = self.src / "metrics.csv"
        def validate(*_args, **_kwargs):
            with dependency.open("a", encoding="utf-8") as handle:
                handle.write("\n")
            return NS(returncode=0, stdout="PASS", stderr="")
        with patch.object(module.subprocess, "run", side_effect=validate):
            with self.assertRaisesRegex(ValueError, "changed during validation"):
                module.EnumCatalogEditor.candidate_valid(self.e, candidate)

    def test_complete_validation_dependency_list_preserved(self):
        from doda_task_templates_editor import FILES
        self.assertEqual(module.FILES, tuple(FILES))

class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Mock()
        self.app = NS(
            enum_catalog_editor=NS(dirty=True), _network_close_handler=self.previous,
            protocol=Mock(), destroy=Mock(),
        )
        self.dialogs = Mock()

    def test_close_cancel_stops_chain(self):
        self.dialogs.askyesno.return_value = False
        policy.install_enum_catalog_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()

    def test_close_accept_delegates_and_preserves_draft_flag(self):
        self.dialogs.askyesno.return_value = True
        policy.install_enum_catalog_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.assertTrue(self.app.enum_catalog_editor.dirty)

    def test_clean_close_adds_no_prompt(self):
        self.app.enum_catalog_editor.dirty = False
        policy.install_enum_catalog_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_project_change_guard(self):
        self.assertFalse(policy.allow_enum_catalog_project_change(self.app, self.dialogs))
        self.app.enum_catalog_editor.dirty = False
        self.assertTrue(policy.allow_enum_catalog_project_change(self.app, self.dialogs))

    def test_guard_installation_is_idempotent(self):
        policy.install_enum_catalog_draft_close_guard(self.app, self.dialogs)
        first = self.app._network_close_handler
        policy.install_enum_catalog_draft_close_guard(self.app, self.dialogs)
        self.assertIs(self.app._network_close_handler, first)
        self.app.protocol.assert_called_once()

    def test_file_exit_uses_guard(self):
        self.dialogs.askyesno.return_value = False
        policy.install_enum_catalog_draft_close_guard(self.app, self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()

    def test_project_guard_precedes_picker(self):
        with patch.object(gui, "allow_enum_catalog_project_change", return_value=False), \
             patch.object(gui.filedialog, "askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()