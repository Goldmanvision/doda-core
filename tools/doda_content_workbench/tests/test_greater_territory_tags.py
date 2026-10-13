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
EXPECTED = {
    "GT_UPSTATE_NEW_YORK": ["cold", "forest", "gothic", "rural", "small_town"],
    "GT_NEW_YORK_CITY": ["industrial", "temperate", "urban"],
    "GT_NEW_MEXICO": ["arid", "cosmic", "desert", "military", "small_town"],
    "GT_SOUTH_CAROLINA": ["forest", "government", "hazardous", "humid", "industrial", "swamp"],
    "GT_MARYLAND": ["coastal", "government", "suburban", "temperate", "urban"],
    "GT_THE_DREAMLANDS": ["cosmic", "otherworldly", "surreal"],
}


def validate(root):
    result = net.Result()
    data = terr.validate_territory(root, result)
    return result, data


class GreaterTerritoryTagTests(unittest.TestCase):
    def copy_source(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        target = Path(temp.name) / "data_authoring" / "source"
        shutil.copytree(ROOT / "data_authoring" / "source", target)
        return Path(temp.name), target

    def edit(self, source, name, old, new):
        path = source / name
        text = path.read_text(encoding="utf-8-sig")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8", newline="")

    def test_seeded_tags_and_export(self):
        result, data = validate(ROOT)
        self.assertTrue(result.valid, result.errors)
        self.assertEqual(len(data["greaterTerritoryTags"]), 20)
        self.assertEqual(len(data["greaterTerritoryTagLinks"]), 27)
        self.assertEqual({t["category"] for t in data["greaterTerritoryTags"]}, set(terr.TAG_CATEGORIES))
        tags = {item["greaterTerritoryId"]: item["tags"] for item in data["greaterTerritories"]}
        self.assertEqual(tags, EXPECTED)
        self.assertFalse(any("has no tags yet" in w for w in result.warnings))

    def test_unknown_tag_is_an_error(self):
        temp_root, source = self.copy_source()
        self.edit(source, "greater_territory_tag_links.csv", "GT_UPSTATE_NEW_YORK,forest,", "GT_UPSTATE_NEW_YORK,bogus,")
        result, _ = validate(temp_root)
        self.assertTrue(any("is not a known tag_id" in e for e in result.errors))

    def test_unknown_greater_territory_is_an_error(self):
        temp_root, source = self.copy_source()
        self.edit(source, "greater_territory_tag_links.csv", "GT_NEW_MEXICO,desert,", "GT_BOGUS,desert,")
        result, _ = validate(temp_root)
        self.assertTrue(any("is not a known greater_territory_id" in e for e in result.errors))

    def test_duplicate_pair_is_an_error(self):
        temp_root, source = self.copy_source()
        path = source / "greater_territory_tag_links.csv"
        lines = path.read_text(encoding="utf-8-sig").splitlines()
        lines.append("LINK_DUPLICATE,GT_UPSTATE_NEW_YORK,forest,test,999,false")
        path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8", newline="")
        result, _ = validate(temp_root)
        self.assertTrue(any("duplicate link for" in e for e in result.errors))

    def test_tag_id_must_be_lowercase(self):
        temp_root, source = self.copy_source()
        self.edit(source, "greater_territory_tags.csv", "\nforest,TERRAIN", "\nForest,TERRAIN")
        result, _ = validate(temp_root)
        self.assertTrue(any("tag_id must be lowercase" in e for e in result.errors))

    def test_editor_registers_tag_tables(self):
        tags = registry.TABLE_METADATA["greater_territory_tags"]
        self.assertEqual(tags.fields[0].name, "tag_id")
        links = {f.name: f for f in registry.TABLE_METADATA["greater_territory_tag_links"].fields}
        self.assertEqual(links["greater_territory_id"].ref_table, "greater_territories")
        self.assertEqual(links["tag_id"].ref_table, "greater_territory_tags")


if __name__ == "__main__":
    unittest.main()
