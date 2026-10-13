import csv
import inspect
import tempfile
import unittest
from pathlib import Path
import doda_evidence_instance_rules as evidence
import doda_network_editor as editor
import doda_page_registry as registry


class EvidenceInstanceUITests(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(
            registry.TABLE_METADATA["evidence_type_instances"].columns,
            evidence.COLUMNS,
        )

    def test_key(self):
        self.assertEqual(
            registry.TABLE_METADATA["evidence_type_instances"].key_columns,
            ("evidence_instance_id",),
        )

    def test_page_and_registry(self):
        page = registry.page_for_tab_text("Evidence Type Instances — Editor")
        self.assertEqual(page.group, "Content")
        self.assertEqual(page.tables, ("evidence_type_instances",))
        self.assertEqual(registry.check_registry(), [])

    def test_field_metadata(self):
        fields = {
            f.name: f for f in registry.TABLE_METADATA["evidence_type_instances"].fields
        }
        self.assertEqual(fields["evidence_resource_id"].kind, "evidence_ref")
        self.assertEqual(fields["base_value_min"].kind, "int")
        self.assertEqual(fields["base_value_max"].kind, "int")
        self.assertTrue(fields["description"].multiline)
        self.assertTrue(all(f.required for f in fields.values()))

    def test_category_filter(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)
            spec = registry.TABLE_METADATA["resources"]
            with (source / spec.filename).open("w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=spec.columns)
                writer.writeheader()
                for rid, kind, active in (
                    ("EVIDENCE_PAPER", "STOCKPILE", "true"),
                    ("EVIDENCE_AUDIO", "STOCKPILE", "false"),
                    ("ADMISSIBLE_EVIDENCE", "STOCKPILE", "true"),
                    ("RESEARCH_POINTS", "STOCKPILE", "true"),
                    ("LEADS", "HOLDING", "true"),
                    ("EVIDENCE_UNKNOWN", "STOCKPILE", "true"),
                    ("EVIDENCE_VIDEO", "HEADCOUNT", "true"),
                ):
                    writer.writerow({
                        "resource_id": rid, "display_name": rid, "description": "Test.",
                        "resource_kind": kind, "tracks_lifetime": "false",
                        "sort_order": "10", "active": active,
                    })
            field = next(
                f for f in registry.TABLE_METADATA["evidence_type_instances"].fields
                if f.name == "evidence_resource_id"
            )
            self.assertEqual(editor.reference_keys(source, field),
                             ["EVIDENCE_PAPER", "EVIDENCE_AUDIO"])

    def test_editor_hooks(self):
        self.assertIn('"evidence_ref"',
                      inspect.getsource(editor.NetworkTableEditor._build))
        self.assertIn('"evidence_ref"',
                      inspect.getsource(editor.NetworkTableEditor._ref_choices))
        self.assertIn('"evidence_type_instances", "Evidence Type Instances"',
                      inspect.getsource(editor.install_network_editor))
