import inspect
import unittest
import doda_collection_rules as collection
import doda_network_editor as editor
import doda_page_registry as registry


class CollectionIntegrationTests(unittest.TestCase):
    def test_metadata_columns(self):
        self.assertEqual(
            registry.TABLE_METADATA["collection_receptacles"].columns,
            collection.COLUMNS,
        )

    def test_metadata_key(self):
        self.assertEqual(
            registry.TABLE_METADATA["collection_receptacles"].key_columns,
            ("receptacle_id",),
        )

    def test_required_fields(self):
        fields = registry.TABLE_METADATA["collection_receptacles"].fields
        self.assertTrue(all(field.required for field in fields))
        by_name = {field.name: field for field in fields}
        self.assertTrue(by_name["description"].multiline)
        self.assertEqual(by_name["active"].kind, "bool")

    def test_equipment_page_and_registry(self):
        page = registry.page_for_tab_text("Collection Receptacles — Editor")
        self.assertEqual(page.group, "Equipment")
        self.assertEqual(page.tables, ("collection_receptacles",))
        self.assertEqual(registry.check_registry(), [])

    def test_editor_validation_and_installation_hooks(self):
        candidate = inspect.getsource(editor.validate_candidate)
        installer = inspect.getsource(editor.install_network_editor)
        self.assertIn("collection_rules.validate_collection(tmp_root, res)", candidate)
        self.assertIn('"collection_receptacles", "Collection Receptacles"', installer)
