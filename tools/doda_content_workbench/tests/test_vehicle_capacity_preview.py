import ast
import inspect
import unittest
import doda_vehicle_capacity_preview as preview
import doda_network_editor as editor


class VehicleCapacityPreviewTests(unittest.TestCase):
    def test_standard_fit(self):
        data = preview.calculate_preview("4", "2")
        self.assertTrue(data["fitsSingleVehicle"])
        self.assertEqual(data["unusedCapacity"], 2)
        self.assertEqual(data["membersOverCapacity"], 0)

    def test_standard_exact(self):
        data = preview.calculate_preview(4, 4)
        self.assertTrue(data["fitsSingleVehicle"])
        self.assertEqual(data["unusedCapacity"], 0)

    def test_standard_exceeds(self):
        data = preview.calculate_preview(4, 5)
        self.assertFalse(data["fitsSingleVehicle"])
        self.assertEqual(data["membersOverCapacity"], 1)
        self.assertEqual(data["unusedCapacity"], 0)

    def test_van_exact(self):
        self.assertTrue(preview.calculate_preview("6", "6")["fitsSingleVehicle"])

    def test_van_exceeds(self):
        self.assertEqual(preview.calculate_preview("6", "7")["membersOverCapacity"], 1)

    def test_one_and_whitespace(self):
        data = preview.calculate_preview(" 1 ", " 1 ")
        self.assertTrue(data["fitsSingleVehicle"])
        self.assertEqual(data["teamMembers"], 1)

    def test_invalid_capacity(self):
        for raw in ("", "0", "-1", "4.5", "4.0", "NaN", "1e2",
                    True, False, 4.0, None, "\u0664"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                preview.calculate_preview(raw, 1)

    def test_invalid_team_members(self):
        for raw in ("", "0", "-1", "2.5", "2.0", "NaN", "1e2",
                    True, False, 2.0, None, "\u0662"):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                preview.calculate_preview(4, raw)

    def test_exact_large_integer(self):
        data = preview.calculate_preview("9007199254740993", "9007199254740994")
        self.assertEqual(data["maxTeamMembers"], 9007199254740993)
        self.assertEqual(data["membersOverCapacity"], 1)

    def test_scope_boundaries(self):
        data = preview.calculate_preview(6, 5)
        self.assertEqual(data["scope"], "SINGLE_VEHICLE_CAPACITY_ARITHMETIC_ONLY")
        for key in ("taskEligibilityChecked", "inventoryChecked",
                    "allocationImplemented", "runtimeImplemented"):
            self.assertFalse(data[key])
        self.assertNotIn("vehiclesRequired", data)

    def test_vehicle_page_button(self):
        source = inspect.getsource(editor.NetworkTableEditor._build)
        self.assertIn('self.spec.table == "vehicle_types"', source)
        self.assertIn('text="Preview Single-Vehicle Capacity"', source)
        self.assertIn('open_vehicle_capacity_preview(self.tab, self.vars)', source)

    def test_preview_has_no_persistence_calls(self):
        source = inspect.getsource(preview)
        names = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    names.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    names.add(node.func.attr)
        self.assertFalse(names & {
            "open", "write", "write_text", "write_bytes",
            "export", "save", "commit", "apply_record", "validate_candidate",
        })
