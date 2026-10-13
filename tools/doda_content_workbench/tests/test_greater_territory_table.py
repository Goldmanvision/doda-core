import csv
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import doda_network_rules as net
import doda_page_registry as registry
import doda_territory_rules as terr

ROOT = net.find_project_root(Path(__file__).resolve().parent)
EXPECTED = {"GT_UPSTATE_NEW_YORK", "GT_NEW_YORK_CITY", "GT_NEW_MEXICO",
            "GT_SOUTH_CAROLINA", "GT_MARYLAND", "GT_THE_DREAMLANDS"}


def validate(root):
    result = net.Result()
    data = terr.validate_territory(root, result)
    return result, data


class GreaterTerritoryTableTests(unittest.TestCase):
    def copy_source(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "data_authoring" / "source"
        shutil.copytree(ROOT / "data_authoring" / "source", target)
        return Path(temp.name), target

    def test_seeded_table_and_export(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual({item["greaterTerritoryId"] for item in data["greaterTerritories"]}, EXPECTED)
        for item in data["territories"]:
            self.assertIn(item["greaterTerritoryId"], EXPECTED)
            self.assertEqual(item["greaterTerritoryId"], item["region"])

    def test_unknown_reference_is_an_error(self):
        temp_root, source = self.copy_source()
        path = source / "territories.csv"
        path.write_text(path.read_text(encoding="utf-8-sig").replace("GT_NEW_MEXICO", "GT_BOGUS"),
                        encoding="utf-8", newline="")
        result, _ = validate(temp_root)
        self.assertTrue(any("not a known greater_territory_id" in e for e in result.errors))

    def test_duplicate_id_is_an_error(self):
        temp_root, source = self.copy_source()
        path = source / "greater_territories.csv"
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        lines.append(lines[1])
        path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
        result, _ = validate(temp_root)
        self.assertTrue(any("duplicate greater_territory_id" in e for e in result.errors))

    def test_editor_registers_table_and_reference(self):
        spec = registry.TABLE_METADATA["greater_territories"]
        self.assertEqual(spec.fields[0].name, "greater_territory_id")
        region = next(f for f in registry.TABLE_METADATA["territories"].fields if f.name == "region")
        self.assertEqual(region.kind, "ref")
        self.assertEqual(region.ref_table, "greater_territories")


if __name__ == "__main__":
    unittest.main()
