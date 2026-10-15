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

import doda_facilities_editor as module
import doda_facilities_draft_policy as policy
import doda_content_gui as gui

LIVE = Path(os.environ.get(
    "DODA_V131_LIVE_MODULE", str(Path(module.__file__).resolve().parent)
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
        self.temp = tempfile.TemporaryDirectory(prefix="v131-staged-")
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
        root.tables = {"department_tracks": read(self.src / "department_tracks.csv")}
        root.log = Mock()
        root.refresh_all = Mock()
        root.facilities_tab = ttk.Frame(root)
        self.e = module.FacilitiesEditor(root)
        self.e.update()
        root.update_idletasks()
        self.rows = copy.deepcopy(self.e.loaded_rows)
        self.ids = tuple(row["facility_id"] for row in self.rows)
        self.path = self.src / "facilities.csv"
        self.e.candidate_valid = Mock(return_value=(True, "PASS"))
        self.dialog_patch = patch.object(module, "messagebox")
        self.dialogs = self.dialog_patch.start()
        self.addCleanup(self.dialog_patch.stop)

    def select(self, count=2):
        ids = self.ids[:count]
        self.e.tree.selection_set(*ids)
        self.e.on_select(force=True)
        return ids

    def describe(self, text):
        self.e.description.delete("1.0", "end")
        self.e.description.insert("1.0", text)

    def by_id(self):
        return {row["facility_id"]: row for row in self.e.loaded_rows}


class DraftTests(Fixture):
    def test_schema_and_real_source_loading(self):
        self.assertEqual(tuple(self.rows[0]), module.FIELDS)
        self.assertEqual(len(module.FIELDS), 10)
        self.assertNotIn("sort_order", module.FIELDS)
        self.assertEqual(module.IDENTITY, ("facility_id",))
        self.assertEqual(str(self.e.tree["selectmode"]), "extended")

    def test_exact_list_column_alignment(self):
        columns = tuple(self.e.tree["columns"])
        self.assertEqual(columns, (
            "facility_id", "display_name", "track_id",
            "personnel_capacity", "initial_tier_id", "active",
        ))
        for row in self.rows:
            values = tuple(map(str, self.e.tree.item(row["facility_id"], "values")))
            self.assertEqual(values, tuple(row[f] for f in columns))

    def test_selection_load_does_not_create_edits(self):
        self.select()
        self.app.update_idletasks()
        self.assertEqual(self.e._changes, {})
        self.assertFalse(self.e.dirty)
        self.assertEqual(str(self.e.widgets["facility_id"].cget("state")), "disabled")

    def test_untouched_apply_skips_validation(self):
        self.select()
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_batch_changes_selected_rows_and_field_only(self):
        selected = self.select()
        before = self.path.read_bytes()
        self.e.vars["display_name"].set("Temporary name")
        self.assertTrue(self.e.apply_record())
        for old, current in zip(self.rows, self.e.loaded_rows):
            expected = {**old, "display_name": "Temporary name"} if old["facility_id"] in selected else old
            self.assertEqual(current, expected)
        self.assertEqual(self.e.tree.selection(), selected)
        self.assertEqual(self.path.read_bytes(), before)

    def test_description_immediate_apply(self):
        selected = self.select()
        self.describe("Temporary description")
        self.assertTrue(self.e.apply_record())
        for row in self.e.loaded_rows:
            original = next(r for r in self.rows if r["facility_id"] == row["facility_id"])
            expected = "Temporary description" if row["facility_id"] in selected else original["description"]
            self.assertEqual(row["description"], expected)

    def test_same_selection_preserves_pending_text(self):
        self.select()
        self.describe("Pending description")
        self.e.on_select()
        self.assertEqual(self.e.description.get("1.0", "end-1c"), "Pending description")

    def test_double_refresh_preserves_pending_single_entry(self):
        selected = self.select(1)
        self.e.vars["display_name"].set("Pending name")
        self.e.update()
        self.e.update()
        self.assertEqual(self.e.vars["display_name"].get(), "Pending name")
        self.assertEqual(self.e.tree.selection(), selected)

    def test_double_refresh_preserves_pending_description(self):
        self.select()
        self.describe("Pending description")
        self.e.update()
        self.e.update()
        self.assertEqual(self.e.description.get("1.0", "end-1c"), "Pending description")

    def test_dirty_refresh_retains_draft_and_snapshot(self):
        self.select(1)
        self.e.vars["display_name"].set("Applied draft")
        self.assertTrue(self.e.apply_record())
        expected = copy.deepcopy(self.e.loaded_rows)
        snapshot = self.e.snapshot_hash
        self.path.write_text("external", encoding="utf-8")
        self.e.update()
        self.assertEqual(self.e.loaded_rows, expected)
        self.assertEqual(self.e.snapshot_hash, snapshot)

    def test_clean_refresh_loads_external_change(self):
        rows = copy.deepcopy(self.rows)
        rows[0]["display_name"] = "External"
        self.e.write(self.path, rows)
        self.e.update()
        self.assertEqual(self.e.loaded_rows, rows)

    def test_required_fields_reject_atomically(self):
        self.select()
        for field in (
            "display_name", "hq_zone_id", "description",
            "interaction_asset_id", "foims_panel_id",
        ):
            with self.subTest(field=field):
                self.e._changes = {field: ""}
                self.assertFalse(self.e.apply_record())
                self.assertEqual(self.e.loaded_rows, self.rows)

    def test_invalid_values_reject_atomically(self):
        self.select()
        for field, value in (
            ("personnel_capacity", "0"), ("personnel_capacity", "-1"),
            ("personnel_capacity", "1.5"), ("personnel_capacity", "bad"),
            ("track_id", "V131_MISSING"), ("initial_tier_id", "V131_MISSING"),
            ("active", "maybe"), ("display_name", "Multiple values"),
        ):
            with self.subTest(field=field, value=value):
                self.e._changes = {field: value}
                self.assertFalse(self.e.apply_record())
                self.assertEqual(self.e.loaded_rows, self.rows)

    def test_single_identity_change_rejected(self):
        self.select(1)
        self.e.vars["facility_id"].set("OTHER")
        self.assertFalse(self.e.apply_record())

    def test_batch_identity_injection_rejected(self):
        self.select()
        self.e._changes = {"facility_id": "OTHER"}
        self.assertFalse(self.e.apply_record())

    def test_single_apply_preserves_row_order(self):
        self.select(1)
        self.e.vars["hq_zone_id"].set("TEMPORARY_ZONE")
        self.assertTrue(self.e.apply_record())
        self.assertEqual(tuple(r["facility_id"] for r in self.e.loaded_rows), self.ids)

    def test_new_unique_record_is_draft_only(self):
        before = self.path.read_bytes()
        self.e.new()
        row = {**self.rows[0], "facility_id": "V131_TEMP_FACILITY", "active": "FALSE"}
        for field, value in row.items():
            self.e.vars[field].set(value)
        self.describe(row["description"])
        self.assertTrue(self.e.apply_record())
        self.assertIn(row["facility_id"], self.by_id())
        self.assertEqual(self.path.read_bytes(), before)

    def test_new_duplicate_rejected(self):
        self.e.new()
        for field, value in self.rows[0].items():
            self.e.vars[field].set(value)
        self.describe(self.rows[0]["description"])
        self.assertFalse(self.e.apply_record())

    def test_stale_selection_rejected(self):
        self.select()
        self.e.tree.selection_set(self.ids[0], self.ids[2])
        self.e._changes = {"display_name": "Changed"}
        self.assertFalse(self.e.apply_record())
        self.e.candidate_valid.assert_not_called()

    def test_draft_mutation_during_validation_blocks_apply(self):
        self.select()
        self.e._changes = {"display_name": "Changed"}
        def validate(_path):
            self.e.loaded_rows[-1]["display_name"] = "External draft mutation"
            return True, "PASS"
        self.e.candidate_valid.side_effect = validate
        self.assertFalse(self.e.apply_record())
        self.assertEqual(self.by_id()[self.ids[0]], self.rows[0])

    def test_candidate_failure_preserves_draft(self):
        self.select()
        self.e._changes = {"display_name": "Changed"}
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
        self.describe("Unapplied")
        self.e.commit = Mock()
        self.assertTrue(self.e.save())
        self.e.commit.assert_called_once_with(self.e.loaded_rows)
        self.assertEqual(self.e.loaded_rows, self.rows)

    def test_save_creates_original_backup(self):
        original = self.path.read_bytes()
        self.e.loaded_rows[0]["display_name"] = "Saved name"
        self.e.dirty = True
        self.assertTrue(self.e.save())
        backups = list(self.e.backup_directory().glob("*.csv"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(read(self.path)[0]["display_name"], "Saved name")
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
        dependency = self.src / "department_tracks.csv"
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
        self.describe("Pending")
        self.e.revert()
        self.assertEqual(self.e.description.get("1.0", "end-1c"), original)
        self.e.dirty = True
        self.dialogs.askyesno.return_value = False
        self.assertFalse(self.e.revert_source())
        self.assertTrue(self.e.dirty)

    def test_revert_draft_reloads_source(self):
        self.e.loaded_rows[0]["display_name"] = "Draft"
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
        module.install_facilities_editor(self.app)
        self.assertIs(self.app.update_facilities.__self__, self.app.facilities_editor)
        self.assertIs(self.app.update_facilities.__func__, module.FacilitiesEditor.update)


class ValidatorTests(Fixture):
    def validate(self, rows=None):
        candidate = self.folder / "candidate.csv"
        self.e.write(candidate, self.rows if rows is None else rows)
        return module.FacilitiesEditor.candidate_valid(self.e, candidate)

    def links(self):
        return read(self.src / "facility_capabilities.csv")

    def test_current_source_passes_actual_validator(self):
        valid, output = self.validate()
        self.assertTrue(valid, output)

    def test_referenced_facility_deletion_rejected(self):
        fid = self.links()[0]["facility_id"]
        valid, output = self.validate([r for r in self.rows if r["facility_id"] != fid])
        self.assertFalse(valid, output)
        self.assertIn(fid, output)

    def test_referenced_facility_deactivation_rejected(self):
        fid = self.links()[0]["facility_id"]
        rows = [{**r, "active": "FALSE"} if r["facility_id"] == fid else dict(r) for r in self.rows]
        self.assertFalse(self.validate(rows)[0])

    def test_unknown_track_and_tier_rejected(self):
        for field in ("track_id", "initial_tier_id"):
            with self.subTest(field=field):
                rows = copy.deepcopy(self.rows)
                rows[0][field] = "V131_MISSING"
                self.assertFalse(self.validate(rows)[0])

    def test_individual_installation_limit_blocks_reduced_capacity(self):
        links = self.links()
        links[0]["max_concurrent_personnel"] = "2"
        fid = links[0]["facility_id"]
        write(self.src / "facility_capabilities.csv", tuple(links[0]), links)
        rows = [{**r, "personnel_capacity": "1"} if r["facility_id"] == fid else dict(r) for r in self.rows]
        valid, output = self.validate(rows)
        self.assertFalse(valid, output)
        self.assertIn("exceeds facility", output)

    def test_aggregate_overcommit_is_warning_not_error(self):
        original = self.links()
        template = original[0]
        fid = template["facility_id"]
        capabilities = [
            r["capability_id"] for r in read(self.src / "capabilities.csv")
            if r["active"].upper() == "TRUE"
        ]
        self.assertGreaterEqual(len(capabilities), 2)
        links = [dict(r) for r in original if r["facility_id"] != fid]
        for index, cid in enumerate(capabilities[:2], 1):
            links.append({
                **template, "capability_id": cid, "max_concurrent_personnel": "2",
                "active": "TRUE", "sort_order": str(index * 10),
                "foims_panel_id": "V131_TEST_PANEL",
            })
        write(self.src / "facility_capabilities.csv", tuple(template), links)
        rows = [{**r, "personnel_capacity": "2"} if r["facility_id"] == fid else dict(r) for r in self.rows]
        valid, output = self.validate(rows)
        self.assertTrue(valid, output)
        self.assertIn("strategic allocation tradeoff", output)

    def test_dependency_change_during_validation_rejected(self):
        candidate = self.folder / "candidate.csv"
        self.e.write(candidate, self.rows)
        dependency = self.src / "department_tracks.csv"
        def validate(*_args, **_kwargs):
            with dependency.open("a", encoding="utf-8") as handle:
                handle.write("\n")
            return NS(returncode=0, stdout="PASS", stderr="")
        with patch.object(module.subprocess, "run", side_effect=validate):
            with self.assertRaisesRegex(ValueError, "changed during validation"):
                module.FacilitiesEditor.candidate_valid(self.e, candidate)


class PolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous = Mock()
        self.app = NS(
            facilities_editor=NS(dirty=True), _network_close_handler=self.previous,
            protocol=Mock(), destroy=Mock(),
        )
        self.dialogs = Mock()

    def test_close_cancel_stops_chain(self):
        self.dialogs.askyesno.return_value = False
        policy.install_facilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_not_called()

    def test_close_accept_delegates_and_preserves_draft_flag(self):
        self.dialogs.askyesno.return_value = True
        policy.install_facilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.previous.assert_called_once()
        self.assertTrue(self.app.facilities_editor.dirty)

    def test_clean_close_adds_no_prompt(self):
        self.app.facilities_editor.dirty = False
        policy.install_facilities_draft_close_guard(self.app, self.dialogs)
        self.app._network_close_handler()
        self.dialogs.askyesno.assert_not_called()
        self.previous.assert_called_once()

    def test_project_change_guard(self):
        self.assertFalse(policy.allow_facilities_project_change(self.app, self.dialogs))
        self.app.facilities_editor.dirty = False
        self.assertTrue(policy.allow_facilities_project_change(self.app, self.dialogs))

    def test_guard_installation_is_idempotent(self):
        policy.install_facilities_draft_close_guard(self.app, self.dialogs)
        first = self.app._network_close_handler
        policy.install_facilities_draft_close_guard(self.app, self.dialogs)
        self.assertIs(self.app._network_close_handler, first)
        self.app.protocol.assert_called_once()

    def test_file_exit_uses_guard(self):
        self.dialogs.askyesno.return_value = False
        policy.install_facilities_draft_close_guard(self.app, self.dialogs)
        gui.ContentWorkbenchApp.request_close(self.app)
        self.previous.assert_not_called()

    def test_project_guard_precedes_picker(self):
        with patch.object(gui, "allow_facilities_project_change", return_value=False), \
             patch.object(gui.filedialog, "askdirectory") as picker:
            gui.ContentWorkbenchApp.choose_project_root(self.app)
        picker.assert_not_called()