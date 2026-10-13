import csv
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import doda_network_editor as editor


class SharedCsvWriterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="shared-writer-")
        self.root = Path(self.tmp.name)
        self.path = self.root / "catalog.csv"
        self.original = b"id,name\r\nOLD,Original\r\n"
        self.path.write_bytes(self.original)
        self.spec = SimpleNamespace(columns=["id", "name"])

    def tearDown(self):
        self.tmp.cleanup()

    def staged(self):
        return list(self.root.glob(".catalog.csv.*.tmp"))

    def test_round_trip_and_line_endings(self):
        rows = [{"id": "A", "name": 'Comma, quote " and caf\u00e9'}]
        editor.write_rows(self.path, self.spec, rows)
        with self.path.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(list(csv.DictReader(handle)), rows)
        self.assertTrue(self.path.read_bytes().startswith(b"id,name\r\n"))
        self.assertEqual(self.staged(), [])

    def test_missing_columns_remain_blank(self):
        editor.write_rows(
            self.path, self.spec, [{"id": "A", "ignored": "extra"}]
        )
        with self.path.open(encoding="utf-8", newline="") as handle:
            self.assertEqual(
                list(csv.DictReader(handle)), [{"id": "A", "name": ""}]
            )

    def test_empty_rows_write_header_only(self):
        editor.write_rows(self.path, self.spec, [])
        self.assertEqual(self.path.read_bytes(), b"id,name\r\n")
        self.assertEqual(self.staged(), [])

    def test_row_failure_preserves_original_and_cleans_staging(self):
        def failing_rows():
            yield {"id": "A", "name": "First row"}
            raise OSError("simulated row generation failure")
        with self.assertRaises(OSError):
            editor.write_rows(self.path, self.spec, failing_rows())
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(self.staged(), [])

    def test_replace_failure_preserves_original_and_cleans_staging(self):
        with patch.object(
            Path, "replace",
            side_effect=PermissionError("simulated replace failure"),
        ):
            with self.assertRaises(PermissionError):
                editor.write_rows(
                    self.path, self.spec, [{"id": "A", "name": "New"}]
                )
        self.assertEqual(self.path.read_bytes(), self.original)
        self.assertEqual(self.staged(), [])

    def test_fixed_temp_file_is_not_overwritten(self):
        legacy = self.path.with_suffix(".csv.tmp")
        legacy.write_bytes(b"Unrelated staging file")
        editor.write_rows(self.path, self.spec, [{"id": "A", "name": "New"}])
        self.assertEqual(legacy.read_bytes(), b"Unrelated staging file")
        self.assertEqual(self.staged(), [])

    def test_each_write_uses_unique_sibling_staging(self):
        original_factory = editor.tempfile.NamedTemporaryFile
        names = []
        def record(*args, **kwargs):
            handle = original_factory(*args, **kwargs)
            names.append(Path(handle.name))
            return handle
        with patch.object(
            editor.tempfile, "NamedTemporaryFile", side_effect=record
        ):
            editor.write_rows(
                self.path, self.spec, [{"id": "A", "name": "First"}]
            )
            editor.write_rows(
                self.path, self.spec, [{"id": "B", "name": "Second"}]
            )
        self.assertEqual(len(names), 2)
        self.assertNotEqual(names[0], names[1])
        self.assertTrue(all(p.parent == self.root for p in names))
        self.assertTrue(all(not p.exists() for p in names))
