import inspect
import unittest
import doda_evidence_range_preview as preview
import doda_network_editor as editor


class EvidenceRangePreviewTests(unittest.TestCase):
    def model(self, multiplier="2", active=False, categories=None):
        return {
            "modelId": "TEST_CAMERA", "displayName": "Camera", "active": active,
            "evidenceTypes": ["EVIDENCE_PHOTOGRAPHIC"] if categories is None else categories,
            "evidenceValueMultiplier": multiplier,
        }

    def calculate(self, low="20", high="20", count="1", model=None):
        return preview.calculate_range(
            low, high, "EVIDENCE_PHOTOGRAPHIC",
            self.model() if model is None else model, count,
        )

    def test_fixed_photo(self):
        data = self.calculate(count="2")
        self.assertEqual(data["valuePerPieceMin"], 40)
        self.assertEqual(data["valuePerPieceMax"], 40)
        self.assertEqual(data["totalValueMin"], 80)
        self.assertEqual(data["totalValueMax"], 80)

    def test_wider_range(self):
        data = self.calculate("10", "20", "3")
        self.assertEqual(data["totalValueMin"], 60)
        self.assertEqual(data["totalValueMax"], 120)

    def test_half_up_per_piece(self):
        data = self.calculate("1", "3", "2", self.model("1.5"))
        self.assertEqual(data["valuePerPieceMin"], 2)
        self.assertEqual(data["valuePerPieceMax"], 5)
        self.assertEqual(data["totalValueMin"], 4)
        self.assertEqual(data["totalValueMax"], 10)

    def test_zero_and_large_values(self):
        self.assertEqual(self.calculate("0", "0")["totalValueMax"], 0)
        data = self.calculate("9007199254740993", "9007199254740993")
        self.assertEqual(data["valuePerPieceMin"], 18014398509481986)

    def test_invalid_range(self):
        for low, high in (("5", "4"), ("-1", "4"), ("1.5", "4"), ("", "4")):
            with self.subTest(low=low, high=high):
                with self.assertRaises(ValueError):
                    self.calculate(low, high)

    def test_invalid_count_and_multiplier(self):
        for count in ("0", "1.5", True):
            with self.subTest(count=count):
                with self.assertRaises(ValueError):
                    self.calculate(count=count)
        for factor in ("0", "NaN", None):
            with self.subTest(factor=factor):
                with self.assertRaises(ValueError):
                    self.calculate(model=self.model(factor))

    def test_incompatible_category(self):
        with self.assertRaises(ValueError):
            self.calculate(model=self.model(categories=["EVIDENCE_CHEMICAL"]))
        with self.assertRaises(ValueError):
            preview.calculate_range("1", "1", "ADMISSIBLE_EVIDENCE", self.model(), "1")

    def test_model_filter_includes_draft(self):
        draft = self.model()
        missing = self.model(None)
        wrong = self.model(categories=["EVIDENCE_CHEMICAL"])
        self.assertEqual(preview.compatible_models(
            "EVIDENCE_PHOTOGRAPHIC", [draft, missing, wrong]), [draft])
        self.assertIn("DRAFT / INACTIVE", preview.model_label(draft))
        self.assertIn("ACTIVE", preview.model_label(self.model(active=True)))

    def test_inputs_unchanged(self):
        model = self.model()
        before = dict(model, evidenceTypes=list(model["evidenceTypes"]))
        data = self.calculate(count="2", model=model)
        self.assertEqual(model, before)
        self.assertEqual(data["pieceCount"], 2)
        self.assertFalse(data["modelActive"])

    def test_editor_button(self):
        source = inspect.getsource(editor.NetworkTableEditor._build)
        self.assertIn('self.spec.table == "evidence_type_instances"', source)
        self.assertIn("Preview Collection Range", source)
        self.assertIn("self.tab, self.app.project_root, self.vars", source)
