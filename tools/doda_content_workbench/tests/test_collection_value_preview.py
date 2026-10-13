import inspect
import unittest
import doda_collection_value_preview as preview
import doda_network_editor as editor


class CollectionValuePreviewTests(unittest.TestCase):
    def test_default_multiplier(self):
        self.assertEqual(preview.calculate_preview("10", "1", "2")["totalValue"], 20)

    def test_chemical_multiplier(self):
        self.assertEqual(preview.calculate_preview("10", "3", "2")["totalValue"], 60)

    def test_camera_multiplier(self):
        self.assertEqual(preview.calculate_preview("10", "2", "2")["totalValue"], 40)

    def test_half_up(self):
        data = preview.calculate_preview("1.25", "2", "1")
        self.assertEqual(data["valuePerPiece"], 3)

    def test_per_piece_before_total(self):
        data = preview.calculate_preview("1.25", "2", "2")
        self.assertEqual(data["pieceCount"], 2)
        self.assertEqual(data["valuePerPiece"], 3)
        self.assertEqual(data["totalValue"], 6)

    def test_zero_base(self):
        self.assertEqual(preview.calculate_preview("0", "3", "5")["totalValue"], 0)

    def test_fractional_multiplier(self):
        self.assertEqual(preview.calculate_preview("2.5", "1.5", "1")["totalValue"], 4)

    def test_exact_large_integer(self):
        self.assertEqual(
            preview.calculate_preview("9007199254740993", "1", "1")["totalValue"],
            9007199254740993,
        )

    def test_invalid_inputs(self):
        for args in (
            ("abc", "1", "1"),
            ("-1", "1", "1"),
            ("1", "0", "1"),
            ("1", "-1", "1"),
            ("1", "NaN", "1"),
            ("1", "1", "0"),
            ("1", "1", "1.5"),
            ("1", "1", True),
            ("1", "1", 1.0),
        ):
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    preview.calculate_preview(*args)

    def test_model_page_button(self):
        source = inspect.getsource(editor.NetworkTableEditor._build)
        self.assertIn('self.spec.table == "collection_models"', source)
        self.assertIn("Preview Collection Value", source)
        self.assertIn("open_collection_value_preview(self.tab, self.vars)", source)
