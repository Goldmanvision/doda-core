"""Saved-file freshness and actual GUI method integration; isolated fixtures only."""
import ast
import csv
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace as NS
import unittest
from unittest.mock import Mock, patch

import doda_export_freshness as fresh

LIVE = Path(os.environ.get("DODA_V136_LIVE_MODULE", str(Path(fresh.__file__).resolve().parent)))
GUI_SOURCE = Path(os.environ.get("DODA_V136_GUI_SOURCE", str(LIVE / "doda_content_gui.py")))
ROOT = LIVE.parents[1]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def method(name, namespace):
    tree = ast.parse(GUI_SOURCE.read_text(encoding="utf-8-sig"))
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ContentWorkbenchApp")
    node = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[node], type_ignores=[])),
                 str(GUI_SOURCE), "exec"), namespace)
    return namespace[name], node


class Fixture(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="v136-freshness-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        source = self.root / "data_authoring/source"
        source.mkdir(parents=True)
        for filename in fresh.exporter.TABLE_FILES.values():
            (source / filename).write_bytes(b"id,value\nA,B\n")
        self.department = self.root / fresh.DEPARTMENT_JSON
        self.department.parent.mkdir(parents=True)
        self.payload = {
            "schemaVersion": fresh.exporter.SCHEMA_VERSION,
            "tables": {name: [] for name in fresh.exporter.TABLE_FILES},
        }
        self.department.write_text(json.dumps(self.payload), encoding="utf-8")
        self.manifest_path = self.root / fresh.MANIFEST
        self.manifest_path.parent.mkdir(parents=True)
        self.manifest = {
            "schemaVersion": fresh.exporter.SCHEMA_VERSION,
            "sourceFiles": {
                filename: digest(source / filename)
                for filename in fresh.exporter.TABLE_FILES.values()
            },
            "outputFiles": {fresh.DEPARTMENT_JSON.as_posix(): digest(self.department)},
        }
        self.write_manifest()
        for relative in (
            fresh.zscript_catalog.NETWORK_JSON,
            fresh.zscript_catalog.EQUIPMENT_JSON,
            fresh.zscript_catalog.OUTPUT_ZS,
        ):
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}", encoding="utf-8")
        self.checker = patch.object(fresh.zscript_catalog, "is_current", return_value=True).start()
        self.addCleanup(patch.stopall)

    def write_manifest(self):
        self.manifest_path.write_text(json.dumps(self.manifest), encoding="utf-8")

    def inspect(self):
        return fresh.inspect_freshness(self.root)

    def change_csv(self):
        path = self.root / "data_authoring/source/capability_staffing_rules.csv"
        path.write_bytes(path.read_bytes() + b"\n")

    def assert_department(self, state):
        report = self.inspect()
        self.assertEqual(report.department.state, state)
        self.assertFalse(report.current)
        self.assertTrue(report.warnings)
        return report


class FreshnessTests(Fixture):
    def test_current_chain(self):
        report = self.inspect()
        self.assertTrue(report.current)
        self.assertEqual(report.warnings, ())
        self.assertIn("Catalog vs JSON: CURRENT", report.summary)

    def test_changed_csv_with_current_catalog(self):
        self.change_csv()
        report = self.assert_department(fresh.STALE)
        self.assertEqual(report.catalog.state, fresh.CURRENT)
        self.assertIn("Export All", report.warnings[0])
        self.assertIn("capability_staffing_rules.csv", report.warnings[0])

    def test_changed_json_output(self):
        self.payload["tables"]["capabilities"].append({"changed": True})
        self.department.write_text(json.dumps(self.payload), encoding="utf-8")
        self.assert_department(fresh.STALE)

    def test_stale_catalog_with_current_export(self):
        self.checker.return_value = False
        report = self.inspect()
        self.assertEqual(report.department.state, fresh.CURRENT)
        self.assertEqual(report.catalog.state, fresh.STALE)
        self.assertFalse(report.current)

    def test_both_stages_stale(self):
        self.change_csv()
        self.checker.return_value = False
        report = self.inspect()
        self.assertEqual(len(report.warnings), 2)
        self.assertEqual(report.department.state, fresh.STALE)
        self.assertEqual(report.catalog.state, fresh.STALE)

    def test_missing_manifest(self):
        self.manifest_path.unlink()
        self.assert_department(fresh.MISSING)

    def test_missing_department_json(self):
        self.department.unlink()
        report = self.assert_department(fresh.MISSING)
        self.assertEqual(report.catalog.state, fresh.MISSING)

    def test_missing_saved_csv(self):
        (self.root / "data_authoring/source/capability_staffing_rules.csv").unlink()
        self.assert_department(fresh.MISSING)

    def test_missing_catalog(self):
        (self.root / fresh.zscript_catalog.OUTPUT_ZS).unlink()
        self.assertEqual(self.inspect().catalog.state, fresh.MISSING)
        self.checker.assert_not_called()

    def test_missing_network_json(self):
        (self.root / fresh.zscript_catalog.NETWORK_JSON).unlink()
        self.assertEqual(self.inspect().catalog.state, fresh.MISSING)

    def test_missing_equipment_json(self):
        (self.root / fresh.zscript_catalog.EQUIPMENT_JSON).unlink()
        self.assertEqual(self.inspect().catalog.state, fresh.MISSING)

    def test_malformed_manifest(self):
        self.manifest_path.write_text("{", encoding="utf-8")
        self.assert_department(fresh.UNVERIFIED)

    def test_nonobject_manifest(self):
        self.manifest_path.write_text("[]", encoding="utf-8")
        self.assert_department(fresh.UNVERIFIED)

    def test_missing_source_hash_mapping(self):
        del self.manifest["sourceFiles"]
        self.write_manifest()
        self.assert_department(fresh.UNVERIFIED)

    def test_missing_source_hash_entry(self):
        del self.manifest["sourceFiles"]["capability_staffing_rules.csv"]
        self.write_manifest()
        self.assert_department(fresh.UNVERIFIED)

    def test_bad_source_hash(self):
        self.manifest["sourceFiles"]["capability_staffing_rules.csv"] = "not-a-hash"
        self.write_manifest()
        self.assert_department(fresh.UNVERIFIED)

    def test_nonstring_source_hash(self):
        self.manifest["sourceFiles"]["capability_staffing_rules.csv"] = None
        self.write_manifest()
        self.assert_department(fresh.UNVERIFIED)

    def test_bad_output_hash(self):
        self.manifest["outputFiles"][fresh.DEPARTMENT_JSON.as_posix()] = "bad"
        self.write_manifest()
        self.assert_department(fresh.UNVERIFIED)

    def test_missing_output_hash(self):
        self.manifest["outputFiles"] = {}
        self.write_manifest()
        self.assert_department(fresh.UNVERIFIED)

    def test_wrong_manifest_schema(self):
        self.manifest["schemaVersion"] = -1
        self.write_manifest()
        self.assert_department(fresh.UNVERIFIED)

    def test_bad_department_json(self):
        self.department.write_text("{", encoding="utf-8")
        self.assert_department(fresh.UNVERIFIED)

    def test_missing_department_tables(self):
        self.department.write_text(json.dumps({"schemaVersion": fresh.exporter.SCHEMA_VERSION}), encoding="utf-8")
        self.assert_department(fresh.UNVERIFIED)

    def test_checker_error_is_unverified(self):
        self.checker.side_effect = ValueError("Invalid catalog inputs")
        report = self.inspect()
        self.assertEqual(report.catalog.state, fresh.UNVERIFIED)
        self.assertFalse(report.current)

    def test_unreadable_manifest_is_unverified(self):
        real_read = Path.read_bytes
        target = self.manifest_path.resolve()
        def read(path):
            if path.resolve() == target:
                raise PermissionError("fixture access denied")
            return real_read(path)
        with patch.object(Path, "read_bytes", read):
            self.assert_department(fresh.UNVERIFIED)

    def test_extra_manifest_entries_do_not_expand_inventory(self):
        self.manifest["sourceFiles"]["unrelated.csv"] = "ignored"
        self.write_manifest()
        self.assertTrue(self.inspect().current)

    def test_unrelated_csv_does_not_stale_department_export(self):
        (self.root / "data_authoring/source/unrelated.csv").write_text("x\nchanged\n", encoding="utf-8")
        self.assertTrue(self.inspect().current)

    def test_uppercase_recorded_hashes(self):
        for mapping in (self.manifest["sourceFiles"], self.manifest["outputFiles"]):
            for key in mapping:
                mapping[key] = mapping[key].upper()
        self.write_manifest()
        self.assertTrue(self.inspect().current)

    def test_check_does_not_modify_inputs(self):
        before = {p.relative_to(self.root): digest(p) for p in self.root.rglob("*") if p.is_file()}
        self.assertTrue(self.inspect().current)
        after = {p.relative_to(self.root): digest(p) for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(after, before)

    def test_changed_during_inspection_is_unverified(self):
        def changed(_root):
            self.change_csv()
            return True
        self.checker.side_effect = changed
        report = self.inspect()
        self.assertEqual(report.department.state, fresh.UNVERIFIED)
        self.assertEqual(report.catalog.state, fresh.UNVERIFIED)

    def test_saved_files_not_unapplied_draft_objects(self):
        draft = {"min_contributors": "99"}
        self.assertTrue(self.inspect().current)
        draft["min_contributors"] = "100"
        self.assertTrue(self.inspect().current)

    def test_no_automatic_export_or_generation(self):
        with patch.object(fresh.exporter, "export_content", side_effect=AssertionError("export called")), \
             patch.object(fresh.zscript_catalog, "generate", side_effect=AssertionError("generate called")):
            self.assertTrue(self.inspect().current)


class GuiTests(Fixture):
    def app(self):
        return NS(
            validation_report=None, validation_text=Mock(), export_text=Mock(),
            project_root=self.root, build_directory=self.root / "build", log=Mock(),
        )

    def status(self, app):
        fn, _ = method("update_status_labels", {
            "datetime": datetime, "doda_export_freshness": fresh,
        })
        fn(app)
        return app.export_text.set.call_args.args[0]

    def rules(self):
        app = self.app()
        result = NS(valid=True, errors=[], warnings=[])
        namespace = {
            "APP_TITLE": "Workbench", "messagebox": NS(showinfo=Mock(), showerror=Mock()),
            "network_editors_dirty": lambda _app: [],
            "doda_export_freshness": fresh,
        }
        _, node = method("run_network_rules", dict(namespace))
        for item in ast.walk(node):
            if isinstance(item, ast.Name) and item.id.startswith("doda_") and item.id not in namespace:
                namespace[item.id] = Mock()
        namespace["doda_network_rules"].Result.return_value = result
        fn, _ = method("run_network_rules", namespace)
        self.assertTrue(fn(app, "validate", False))
        for name, obj in namespace.items():
            if name.startswith("doda_") and name != "doda_export_freshness":
                obj.export.assert_not_called()
        return app, result

    def test_built_status_separates_presence_and_freshness(self):
        app = self.app()
        app.build_directory.mkdir()
        (app.build_directory / "doda-generated-content.pk3").write_bytes(b"presence only")
        status = self.status(app)
        self.assertTrue(status.startswith("BUILT"))
        self.assertNotIn("READY", status)
        self.assertIn("Department export: CURRENT", status)
        self.assertIn("Catalog vs JSON: CURRENT", status)

    def test_existing_pk3_does_not_hide_stale_csv(self):
        app = self.app()
        app.build_directory.mkdir()
        (app.build_directory / "doda-generated-content.pk3").write_bytes(b"presence only")
        self.change_csv()
        self.assertIn("Department export: STALE", self.status(app))

    def test_missing_pk3_status(self):
        status = self.status(self.app())
        self.assertTrue(status.startswith("NOT BUILT"))
        self.assertIn("Catalog vs JSON: CURRENT", status)

    def test_missing_evidence_does_not_crash_status(self):
        self.manifest_path.unlink()
        self.assertIn("Department export: MISSING", self.status(self.app()))

    def test_rules_validation_warns_for_stale_export(self):
        self.change_csv()
        app, result = self.rules()
        self.assertTrue(any("Department export STALE" in w and "Export All" in w for w in result.warnings))
        self.assertTrue(any("NETWORK WARNING" in str(c.args[0]) for c in app.log.call_args_list))

    def test_rules_validation_warns_for_stale_catalog(self):
        self.checker.return_value = False
        _, result = self.rules()
        self.assertTrue(any("ZScript catalog vs JSON STALE" in w for w in result.warnings))

    def test_current_rules_check_adds_no_freshness_warning(self):
        _, result = self.rules()
        self.assertEqual(result.warnings, [])


class RealInputTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix="v136-real-inputs-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        paths = [
            Path("data_authoring/source") / filename
            for filename in fresh.exporter.TABLE_FILES.values()
        ] + [
            fresh.MANIFEST, fresh.DEPARTMENT_JSON,
            fresh.zscript_catalog.NETWORK_JSON, fresh.zscript_catalog.EQUIPMENT_JSON,
            fresh.zscript_catalog.OUTPUT_ZS,
        ]
        for relative in paths:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)

    def test_real_refreshed_inputs_are_current(self):
        report = fresh.inspect_freshness(self.root)
        self.assertTrue(report.current, report.warnings)

    def test_real_stale_csv_current_catalog_reproduces_original_gap(self):
        path = self.root / "data_authoring/source/capability_staffing_rules.csv"
        with path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            fields = reader.fieldnames
            rows = list(reader)
        row = next(r for r in rows if r["capability_id"] == "OCCULT_RESPONSE" and r["qualification_id"] == "OCCULT_RESPONSE")
        row["min_contributors"] = "0"
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        self.assertTrue(fresh.zscript_catalog.is_current(self.root))
        report = fresh.inspect_freshness(self.root)
        self.assertEqual(report.department.state, fresh.STALE)
        self.assertEqual(report.catalog.state, fresh.CURRENT)

    def test_real_catalog_modification_is_separate_stale_stage(self):
        path = self.root / fresh.zscript_catalog.OUTPUT_ZS
        path.write_bytes(path.read_bytes() + b"\n// isolated fixture change\n")
        report = fresh.inspect_freshness(self.root)
        self.assertEqual(report.department.state, fresh.CURRENT)
        self.assertEqual(report.catalog.state, fresh.STALE)