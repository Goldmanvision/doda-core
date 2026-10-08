import json, unittest, uuid, tempfile, shutil
from pathlib import Path
import doda_zscript_catalog as zc

class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.gettempdir()) / ("zc_" + uuid.uuid4().hex)
        (self.root / "generated/data").mkdir(parents=True)
        (self.root / "data_authoring").mkdir()
        (self.root / "zscript.txt").write_text('version "2.4"\n' + zc.INCLUDE_LINE + "\n")
        net = {"tiers": [{"tierId": "T1", "displayName": 'Say "hi"', "networkType": "DIALUP", "generation": 1, "sortOrder": 1, "active": True},
                         {"tierId": "TX", "displayName": "Off", "networkType": "DIALUP", "generation": 1, "sortOrder": 2, "active": False}],
               "hardwareModels": [{"modelId": "M1", "displayName": "Modem", "hardwareKind": "MODEM", "tierId": "T1", "sortOrder": 1, "active": True}]}
        eq = {"totalPersonalDeviceLimit": 8,
              "families": [{"familyId": "FAX", "displayName": "Fax", "ownership": "LOCATION", "perTaskLimit": None, "storageKind": "NONE", "connectionKind": "PHONE_LINE", "sortOrder": 1, "active": True}],
              "models": [{"modelId": "FX", "displayName": "Fax", "familyId": "FAX", "phoneLineKind": None, "networkTierId": None, "connectionOverride": None, "generationOrder": 1, "sortOrder": 1, "active": True}]}
        (self.root / zc.NETWORK_JSON).write_text(json.dumps(net))
        (self.root / zc.EQUIPMENT_JSON).write_text(json.dumps(eq))
        dept = {"tables": {
            "department_tracks": [{"track_id": "T", "display_name": "Technical", "active": True}],
            "facilities": [
                {"facility_id": "F", "display_name": "Facility", "track_id": "T",
                 "hq_zone_id": "HQ", "description": "Description", "personnel_capacity": 2,
                 "initial_tier_id": "OPERATIONAL", "active": True},
                {"facility_id": "EMPTY", "display_name": "Empty Facility", "track_id": "T",
                 "hq_zone_id": "HQ", "description": "", "personnel_capacity": 1,
                 "initial_tier_id": "UNBUILT", "active": True}],
            "capabilities": [{"capability_id": "C", "display_name": "Capability",
                              "description": "Desc", "standing_operation_label": "Stand",
                              "sort_order": 1, "active": True}],
            "facility_capabilities": [
                {"facility_id": "F", "capability_id": "C", "display_name_override": "Local Name",
                 "max_concurrent_personnel": 2, "initial_tier_id": "UNBUILT",
                 "sort_order": 1, "active": True}],
            "qualification_catalog": [
                {"qualification_id": "Q", "display_name": "Qualified", "active": True},
                {"qualification_id": "Q2", "display_name": "Second Qualification", "active": True}],
            "capability_staffing_rules": [
                {"capability_id": "C", "qualification_id": "Q", "min_contributors": 0,
                 "preferred_contributors": 1, "max_contributors": 2, "sort_order": 1, "active": True},
                {"capability_id": "C", "qualification_id": "Q2", "min_contributors": 1,
                 "preferred_contributors": 2, "max_contributors": 2, "sort_order": 2, "active": True}],
            "facility_capability_staffing_overrides": [
                {"facility_id": "F", "capability_id": "C", "qualification_id": "Q",
                 "min_contributors": 1, "preferred_contributors": 2, "max_contributors": 3,
                 "sort_order": 1, "active": True}],
            "enum_catalog": [{"enum_group": "TASK_PRIORITY", "enum_value": "HIGH", "active": True}],
            "task_templates": [
                {"task_template_id": "TASK", "display_name": "Task Template", "description": "Desc",
                 "capability_id": "C", "priority": "HIGH", "default_target_effort_minutes": 240,
                 "default_deadline_minutes": 120, "auto_allocate": True, "sort_order": 1,
                 "active": True}]}}
        (self.root / zc.DEPARTMENT_JSON).write_text(json.dumps(dept))
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)
    def test_generate_and_check(self):
        self.assertEqual(zc.main(["--root", str(self.root)]), 0)
        self.assertEqual(zc.main(["--root", str(self.root), "--check"]), 0)
        zs = (self.root / zc.OUTPUT_ZS).read_text()
        self.assertIn("const TIER_COUNT = 1;", zs)          # inactive excluded
        self.assertIn('"Say \\"hi\\""', zs)                  # escaping
        self.assertIn("case 0: return -1;", zs)              # None limit
        self.assertNotIn("version", zs.split("class")[0].replace("Generator", ""))
    def test_stale_detected(self):
        zc.main(["--root", str(self.root)])
        p = self.root / zc.OUTPUT_ZS
        p.write_text(p.read_text() + "//x")
        self.assertEqual(zc.main(["--root", str(self.root), "--check"]), 1)

    def test_is_current(self):
        self.assertFalse(zc.is_current(self.root))
        zc.generate(self.root)
        self.assertTrue(zc.is_current(self.root))

    def test_timestamp_does_not_change_output(self):
        zc.generate(self.root)
        p = self.root / zc.NETWORK_JSON
        d = json.loads(p.read_text()); d["generatedAtUtc"] = "2099-01-01"; p.write_text(json.dumps(d))
        self.assertTrue(zc.is_current(self.root))

    def test_department_labels_links_and_separate_tiers(self):
        zc.generate(self.root)
        zs = (self.root / zc.OUTPUT_ZS).read_text()
        self.assertIn("const FACILITY_COUNT = 2;", zs)
        self.assertIn("const CAPABILITY_COUNT = 1;", zs)
        self.assertIn('"Local Name"', zs)
        self.assertIn('"OPERATIONAL"', zs)
        self.assertIn('"UNBUILT"', zs)
        dump = (self.root / zc.EXPECTED_DUMP).read_text()
        self.assertIn("DODA_CATALOG LINK F C", dump)
        self.assertIn("DODA_CATALOG FACILITY EMPTY", dump)

    def test_department_timestamp_and_unused_tables_do_not_stale_catalog(self):
        zc.generate(self.root)
        p = self.root / zc.DEPARTMENT_JSON
        d = json.loads(p.read_text())
        d["generatedAtUtc"] = "2099-01-01"
        d["tables"]["flavor_text"] = [{"ignored": "deferred"}]
        p.write_text(json.dumps(d))
        self.assertTrue(zc.is_current(self.root))

    def test_missing_department_export_fails_without_overwriting(self):
        zc.generate(self.root)
        old = (self.root / zc.OUTPUT_ZS).read_bytes()
        (self.root / zc.DEPARTMENT_JSON).unlink()
        with self.assertRaises(ValueError):
            zc.generate(self.root)
        self.assertEqual(old, (self.root / zc.OUTPUT_ZS).read_bytes())

    def test_dangling_link_fails_without_overwriting(self):
        zc.generate(self.root)
        old = (self.root / zc.OUTPUT_ZS).read_bytes()
        p = self.root / zc.DEPARTMENT_JSON
        d = json.loads(p.read_text())
        d["tables"]["facility_capabilities"][0]["facility_id"] = "UNKNOWN"
        p.write_text(json.dumps(d))
        with self.assertRaises(ValueError):
            zc.generate(self.root)
        self.assertEqual(old, (self.root / zc.OUTPUT_ZS).read_bytes())

    def test_department_changes_stale_catalog(self):
        zc.generate(self.root)
        p = self.root / zc.DEPARTMENT_JSON
        d = json.loads(p.read_text())
        d["tables"]["facilities"][0]["display_name"] = "Changed"
        p.write_text(json.dumps(d))
        self.assertFalse(zc.is_current(self.root))

    def staffing_tables(self):
        return json.loads((self.root / zc.DEPARTMENT_JSON).read_text())["tables"]

    def resolve(self, tables):
        return zc.staffing_catalog(tables, tables["capabilities"], tables["facility_capabilities"])

    def test_override_replaces_entire_row_and_other_row_inherits(self):
        _, rows, _ = self.resolve(self.staffing_tables())
        override, inherited = rows
        self.assertEqual([override[k] for k in ("min_contributors", "preferred_contributors", "max_contributors")],
                         [1, 2, 3])
        self.assertEqual(override["global_min_contributors"], 0)
        self.assertEqual(override["provenance"], "OVERRIDE")
        self.assertEqual(inherited["provenance"], "INHERITED")
        self.assertEqual(inherited["min_contributors"], inherited["global_min_contributors"])

    def test_equal_valued_override_keeps_override_provenance(self):
        t = self.staffing_tables()
        t["facility_capability_staffing_overrides"][0].update(
            min_contributors=0, preferred_contributors=1, max_contributors=2)
        _, rows, _ = self.resolve(t)
        self.assertEqual(rows[0]["provenance"], "OVERRIDE")
        self.assertEqual(rows[0]["min_contributors"], 0)

    def test_inactive_override_inherits(self):
        t = self.staffing_tables()
        t["facility_capability_staffing_overrides"][0]["active"] = False
        _, rows, _ = self.resolve(t)
        self.assertEqual(rows[0]["provenance"], "INHERITED")
        self.assertEqual(rows[0]["min_contributors"], 0)

    def test_override_cannot_create_qualification_requirement(self):
        t = self.staffing_tables()
        t["facility_capability_staffing_overrides"][0]["qualification_id"] = "UNKNOWN"
        with self.assertRaises(ValueError):
            self.resolve(t)

    def test_invalid_range_rejected(self):
        t = self.staffing_tables()
        t["facility_capability_staffing_overrides"][0]["preferred_contributors"] = 0
        with self.assertRaises(ValueError):
            self.resolve(t)

    def test_duplicate_override_rejected(self):
        t = self.staffing_tables()
        t["facility_capability_staffing_overrides"].append(
            dict(t["facility_capability_staffing_overrides"][0]))
        with self.assertRaises(ValueError):
            self.resolve(t)

    def test_staffing_change_stales_catalog(self):
        zc.generate(self.root)
        p = self.root / zc.DEPARTMENT_JSON
        d = json.loads(p.read_text())
        d["tables"]["capability_staffing_rules"][0]["max_contributors"] = 4
        p.write_text(json.dumps(d))
        self.assertFalse(zc.is_current(self.root))

    def test_staffing_dump_contains_baseline_effective_and_source(self):
        zc.generate(self.root)
        dump = (self.root / zc.EXPECTED_DUMP).read_text()
        self.assertIn("STAFFING defaults=2 effective=2 overrides=1", dump)
        self.assertIn("F C Q global=0/1/2 effective=1/2/3 source=OVERRIDE", dump)
        self.assertIn("F C Q2 global=1/2/2 effective=1/2/2 source=INHERITED", dump)

    def task_catalog(self, tables):
        return zc.task_template_catalog(tables, {"C"}, {("F", "C")})

    def test_task_effort_deadline_and_allocation_exported_separately(self):
        zc.generate(self.root)
        dump = (self.root / zc.EXPECTED_DUMP).read_text()
        self.assertIn("TASK_TEMPLATES count=1", dump)
        self.assertIn("TASK_TEMPLATE TASK C priority=HIGH effort=240 deadline=120 auto=1", dump)

    def test_inactive_task_excluded(self):
        t = self.staffing_tables()
        t["task_templates"][0]["active"] = False
        self.assertEqual(self.task_catalog(t), [])

    def test_task_reference_requires_installed_capability(self):
        t = self.staffing_tables()
        with self.assertRaises(ValueError):
            zc.task_template_catalog(t, {"C"}, set())

    def test_bad_task_values_rejected(self):
        for field, value in (("priority", "UNKNOWN"), ("default_target_effort_minutes", 0),
                             ("default_deadline_minutes", -1), ("auto_allocate", "TRUE")):
            with self.subTest(field=field):
                t = self.staffing_tables()
                t["task_templates"][0][field] = value
                with self.assertRaises(ValueError):
                    self.task_catalog(t)

    def test_duplicate_task_id_rejected(self):
        t = self.staffing_tables()
        t["task_templates"].append(dict(t["task_templates"][0]))
        with self.assertRaises(ValueError):
            self.task_catalog(t)

    def test_task_change_stales_catalog(self):
        zc.generate(self.root)
        p = self.root / zc.DEPARTMENT_JSON
        d = json.loads(p.read_text())
        d["tables"]["task_templates"][0]["default_deadline_minutes"] = 60
        p.write_text(json.dumps(d))
        self.assertFalse(zc.is_current(self.root))
