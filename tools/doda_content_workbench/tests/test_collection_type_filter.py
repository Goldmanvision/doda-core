import csv
import inspect
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import doda_network_editor as editor
import doda_page_registry as registry


class Scalar:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class CollectionTypeFilterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.src = Path(self.tmp.name)
        for table, keys in (
            ("collection_receptacles", ("EVIDENCE_BAGS", "CHEMICAL_COLLECTION_KIT")),
            ("collection_device_types", ("FILM_CAMERA",)),
        ):
            spec = registry.TABLE_METADATA[table]
            with (self.src / spec.filename).open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=spec.columns)
                writer.writeheader()
                for key in keys:
                    writer.writerow({
                        spec.key: key, "display_name": key,
                        "description": "Test.", "sort_order": "10", "active": "true",
                    })
        self.field = next(
            f for f in registry.TABLE_METADATA["collection_models"].fields
            if f.name == "collection_type_id"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def keys(self, kind):
        return editor.reference_keys(self.src, self.field, kind)

    def fake_editor(self, kind, current):
        return SimpleNamespace(
            app=SimpleNamespace(source_directory=self.src),
            spec=registry.TABLE_METADATA["collection_models"],
            vars={
                "collection_kind": Scalar(kind),
                "collection_type_id": Scalar(current),
                "evidence_types": Scalar("EVIDENCE_PHOTOGRAPHIC"),
                "evidence_value_multiplier": Scalar("2"),
            },
            _ref_choices=lambda: None,
        )

    def test_receptacle_choices(self):
        self.assertEqual(self.keys("RECEPTACLE"),
                         ["EVIDENCE_BAGS", "CHEMICAL_COLLECTION_KIT"])

    def test_device_choices(self):
        self.assertEqual(self.keys("DEVICE"), ["FILM_CAMERA"])

    def test_blank_kind(self):
        self.assertEqual(self.keys(""), [])

    def test_unknown_kind(self):
        self.assertEqual(self.keys("UNKNOWN"), [])

    def test_legacy_unfiltered_call(self):
        self.assertEqual(editor.reference_keys(self.src, self.field), [
            "EVIDENCE_BAGS", "CHEMICAL_COLLECTION_KIT", "FILM_CAMERA",
        ])

    def test_explicit_change_clears_incompatible(self):
        fake = self.fake_editor("RECEPTACLE", "FILM_CAMERA")
        editor.NetworkTableEditor._collection_kind_changed(fake)
        self.assertEqual(fake.vars["collection_type_id"].get(), "")

    def test_explicit_change_keeps_compatible(self):
        fake = self.fake_editor("DEVICE", "FILM_CAMERA")
        editor.NetworkTableEditor._collection_kind_changed(fake)
        self.assertEqual(fake.vars["collection_type_id"].get(), "FILM_CAMERA")

    def test_other_model_properties_unchanged(self):
        fake = self.fake_editor("RECEPTACLE", "FILM_CAMERA")
        editor.NetworkTableEditor._collection_kind_changed(fake)
        self.assertEqual(fake.vars["evidence_types"].get(), "EVIDENCE_PHOTOGRAPHIC")
        self.assertEqual(fake.vars["evidence_value_multiplier"].get(), "2")

    def test_form_refresh_hooks(self):
        for name in ("_on_select", "_clear_form", "paste_csv"):
            self.assertIn("self._ref_choices()",
                          inspect.getsource(getattr(editor.NetworkTableEditor, name)))
        refresh = inspect.getsource(editor.NetworkTableEditor._ref_choices)
        self.assertIn('self.vars["collection_kind"].get().strip()', refresh)
        self.assertNotIn('.set("")', refresh)

    def test_kind_selection_binding(self):
        source = inspect.getsource(editor.NetworkTableEditor._build)
        self.assertIn('"<<ComboboxSelected>>", self._collection_kind_changed', source)
