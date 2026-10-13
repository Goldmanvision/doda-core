import csv
import inspect
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import doda_multiselect as multi
import doda_collection_model_rules as models
import doda_page_registry as registry
import doda_network_editor as editor


class CollectionModelUITests(unittest.TestCase):
    def test_empty_selection(self):
        self.assertEqual(multi.parse_selection(""), [])

    def test_selection_normalization(self):
        self.assertEqual(multi.parse_selection(" A ; B ; A "), ["A", "B"])

    def test_unknown_selection_preserved(self):
        self.assertEqual(
            multi.merged_selection("OLD;A", [("A", "a"), ("B", "b")], {"B"}),
            "B;OLD",
        )

    def test_evidence_choice_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "resources.csv"
            path.write_text(
                "resource_id,display_name,resource_kind,active\n"
                "EVIDENCE_PHYSICAL,Physical,STOCKPILE,true\n"
                "EVIDENCE_CHEMICAL,Chemical,STOCKPILE,false\n"
                "ADMISSIBLE_EVIDENCE,Admissible,STOCKPILE,true\n"
                "EVIDENCE_NOT_STOCK,Invalid,HEADCOUNT,true\n",
                encoding="utf-8",
            )
            self.assertEqual(multi.evidence_choices(directory), [
                ("EVIDENCE_PHYSICAL", "Physical"),
                ("EVIDENCE_CHEMICAL", "Chemical (inactive)"),
            ])

    def test_model_columns(self):
        self.assertEqual(registry.TABLE_METADATA["collection_models"].columns,
                         models.MODEL_COLUMNS)

    def test_device_columns(self):
        self.assertEqual(registry.TABLE_METADATA["collection_device_types"].columns,
                         models.DEVICE_COLUMNS)

    def test_pages_and_registry(self):
        for title in ("Collection Device Types", "Collection Models"):
            page = registry.page_for_tab_text(title + " — Editor")
            self.assertEqual(page.group, "Equipment")
        self.assertEqual(registry.check_registry(), [])

    def test_field_kinds(self):
        fields = {f.name: f for f in registry.TABLE_METADATA["collection_models"].fields}
        self.assertEqual(fields["evidence_types"].kind, "evidence_multi")
        self.assertEqual(fields["evidence_value_multiplier"].kind, "decimal")
        self.assertFalse(fields["evidence_types"].required)
        self.assertFalse(fields["brand"].required)

    def test_collection_type_choices(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            for table, key in (
                ("collection_receptacles", "EVIDENCE_BAGS"),
                ("collection_device_types", "FILM_CAMERA"),
            ):
                spec = registry.TABLE_METADATA[table]
                with (source / spec.filename).open("w", encoding="utf-8", newline="") as handle:
                    writer = csv.DictWriter(handle, fieldnames=spec.columns)
                    writer.writeheader()
                    writer.writerow({spec.key: key})
            field = SimpleNamespace(kind="collection_type_ref")
            self.assertEqual(editor.reference_keys(source, field),
                             ["EVIDENCE_BAGS", "FILM_CAMERA"])

    def test_widget_and_refresh_hooks(self):
        self.assertIn("MultiSelectDropdown", inspect.getsource(editor.NetworkTableEditor._build))
        self.assertIn("evidence_choices", inspect.getsource(editor.NetworkTableEditor._ref_choices))
        self.assertIn("not (tmp_src / filename).is_file()",
                      inspect.getsource(editor.validate_candidate))
