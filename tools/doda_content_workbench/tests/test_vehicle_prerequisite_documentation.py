import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path
import doda_task_prerequisite_rules as prerequisites
import doda_vehicle_rules as vehicles

W = Path(__file__).resolve().parents[1]
ROOT = W.parents[1]
FILES = ("task_templates.csv", "task_prerequisites.csv", "vehicle_types.csv")


class VehiclePrerequisiteDocumentationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="vehicle-documentation-")
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.live_source = ROOT / "data_authoring/source"
        self.live_before = {}
        for name in FILES:
            source = self.live_source / name
            self.live_before[name] = source.read_bytes()
            shutil.copy2(source, self.src / name)

    def tearDown(self):
        self.tmp.cleanup()

    def vehicle_prerequisite(self):
        with (self.src / "task_prerequisites.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            return next(
                row for row in csv.DictReader(handle)
                if row["prerequisite_id"] == "PRE_INVESTIGATE_VEHICLE"
            )

    def prerequisite_export(self):
        result, path = prerequisites.export(self.root)
        self.assertTrue(result.valid, result.errors)
        self.assertIsNotNone(path)
        return json.loads(path.read_text(encoding="utf-8"))

    def test_description_recognizes_catalog_and_runtime_boundary(self):
        text = self.vehicle_prerequisite()["description"]
        self.assertIn("Generic vehicle types are cataloged", text)
        self.assertIn(
            "runtime capacity enforcement and allocation are not implemented",
            text,
        )
        self.assertNotIn(
            "Vehicle catalog and runtime capacity/allocation checks are not implemented",
            text,
        )

    def test_prerequisite_export_preserves_source_description_and_semantics(self):
        source = self.vehicle_prerequisite()
        payload = self.prerequisite_export()
        row = next(
            item for item in payload["prerequisites"]
            if item["prerequisiteId"] == source["prerequisite_id"]
        )
        self.assertEqual(row["description"], source["description"])
        self.assertEqual(row["taskTemplateId"], source["task_template_id"])
        self.assertEqual(row["requirementKind"], source["requirement_kind"])
        self.assertEqual(row["scope"], source["scope"])
        self.assertEqual(row["minQuantity"], int(source["min_quantity"]))
        self.assertEqual(row["active"], source["active"].upper() == "TRUE")
        self.assertFalse(payload["runtimeImplemented"])

    def test_exported_open_item_distinguishes_catalog_from_runtime(self):
        payload = self.prerequisite_export()
        self.assertEqual(
            payload["openItems"]["PRE-01"],
            "Owned vehicle quantities, runtime capacity enforcement and allocation; "
            "generic vehicle types and capacities are authored separately.",
        )

    def test_vehicle_export_matches_authored_capacities_and_boundaries(self):
        with (self.src / "vehicle_types.csv").open(
            encoding="utf-8-sig", newline=""
        ) as handle:
            expected = {
                row["vehicle_type_id"]: int(row["max_team_members"])
                for row in csv.DictReader(handle)
            }
        result, path = vehicles.export(self.root)
        self.assertTrue(result.valid, result.errors)
        self.assertIsNotNone(path)
        payload = json.loads(path.read_text(encoding="utf-8"))
        actual = {
            row["vehicleTypeId"]: row["maxTeamMembers"]
            for row in payload["vehicleTypes"]
        }
        self.assertEqual(actual, expected)
        self.assertFalse(payload["runtimeImplemented"])
        self.assertTrue(payload["rules"]["definitionsCreateNoInventory"])
        self.assertTrue(payload["rules"]["capacityDoesNotChangeTaskStaffingLimits"])
        self.assertFalse(payload["rules"]["runtimeCapacityChecksImplemented"])
        self.assertFalse(payload["rules"]["allocationImplemented"])

    def test_temporary_exports_do_not_modify_source_files(self):
        before = {name: (self.src / name).read_bytes() for name in FILES}
        self.prerequisite_export()
        result, path = vehicles.export(self.root)
        self.assertTrue(result.valid, result.errors)
        self.assertIsNotNone(path)
        for name in FILES:
            self.assertEqual((self.src / name).read_bytes(), before[name])
            self.assertEqual(
                (self.live_source / name).read_bytes(), self.live_before[name]
            )
