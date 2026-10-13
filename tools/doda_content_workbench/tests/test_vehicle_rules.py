import csv
import json
import tempfile
import unittest
from pathlib import Path
import doda_network_rules as net
import doda_vehicle_rules as vehicles


class VehicleTypeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.src = self.root / "data_authoring/source"
        self.src.mkdir(parents=True)
        self.columns = vehicles.COLUMNS
        self.rows = [dict(zip(vehicles.COLUMNS, (
            "STANDARD_MOTOR_VEHICLE", "Standard Motor Vehicle", "4",
            "Generic team transport.", "10", "true",
        )))]

    def tearDown(self):
        self.tmp.cleanup()

    def validate(self):
        with (self.src / vehicles.VEHICLE_TYPES_FILE).open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.DictWriter(handle, fieldnames=self.columns)
            writer.writeheader()
            writer.writerows(self.rows)
        result = net.Result()
        data = vehicles.validate_vehicles(self.root, result)
        return result, data

    def test_valid_capacities(self):
        self.rows.append(dict(zip(vehicles.COLUMNS, (
            "VAN", "Van", "6", "Generic van.", "20", "true",
        ))))
        result, data = self.validate()
        self.assertTrue(result.valid, result.errors)
        self.assertEqual([item["maxTeamMembers"] for item in data["vehicleTypes"]], [4, 6])

    def test_invalid_capacity(self):
        for raw in ("", "0", "-1", "4.5", "NaN"):
            with self.subTest(raw=raw):
                self.rows[0]["max_team_members"] = raw
                self.assertFalse(self.validate()[0].valid)

    def test_duplicate_and_invalid_id(self):
        self.rows.append(dict(self.rows[0]))
        self.assertFalse(self.validate()[0].valid)
        self.rows.pop()
        self.rows[0]["vehicle_type_id"] = "bad id"
        self.assertFalse(self.validate()[0].valid)

    def test_required_text(self):
        for field in ("display_name", "description"):
            old = self.rows[0][field]
            self.rows[0][field] = ""
            self.assertFalse(self.validate()[0].valid)
            self.rows[0][field] = old

    def test_boolean_and_order(self):
        for field, raw in (("active", "maybe"), ("sort_order", "-1")):
            old = self.rows[0][field]
            self.rows[0][field] = raw
            self.assertFalse(self.validate()[0].valid)
            self.rows[0][field] = old

    def test_exact_header(self):
        self.columns = vehicles.COLUMNS[:-1]
        self.rows[0].pop("active")
        self.assertFalse(self.validate()[0].valid)

    def test_malformed_row(self):
        path = self.src / vehicles.VEHICLE_TYPES_FILE
        path.write_text(",".join(vehicles.COLUMNS) + "\nVAN,Van,6\n", encoding="utf-8")
        result = net.Result()
        vehicles.validate_vehicles(self.root, result)
        self.assertFalse(result.valid)

    def test_export_failure_preserves(self):
        self.validate()
        result, path = vehicles.export(self.root)
        self.assertTrue(result.valid, result.errors)
        old = path.read_bytes()
        payload = json.loads(old)
        self.assertFalse(payload["runtimeImplemented"])
        self.assertTrue(payload["rules"]["definitionsCreateNoInventory"])
        self.assertFalse(payload["rules"]["personalDeviceSlotAccountingApplies"])
        self.rows[0]["max_team_members"] = "0"
        self.validate()
        result, failed = vehicles.export(self.root)
        self.assertFalse(result.valid)
        self.assertIsNone(failed)
        self.assertEqual(path.read_bytes(), old)
