import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_page_registry as reg

SOURCE = (Path(__file__).resolve().parents[1] / "doda_network_editor.py").read_text(encoding="utf-8-sig")


class EditorCoverageTests(unittest.TestCase):
    def test_every_registry_table_has_an_editor(self):
        missing = [t for t in reg.TABLE_METADATA if f'"{t}"' not in SOURCE]
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()