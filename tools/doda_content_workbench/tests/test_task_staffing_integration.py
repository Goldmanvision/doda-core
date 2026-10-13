import inspect
import unittest
import doda_task_staffing_rules as staffing
import doda_network_editor as editor
import doda_page_registry as registry


class TaskStaffingIntegrationTests(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(
            registry.TABLE_METADATA["task_staffing_rules"].columns,
            staffing.COLUMNS,
        )

    def test_composite_key(self):
        self.assertEqual(
            registry.TABLE_METADATA["task_staffing_rules"].key_columns,
            ("task_template_id", "personnel_role"),
        )

    def test_optional_counts_and_role_choices(self):
        fields = {
            field.name: field
            for field in registry.TABLE_METADATA["task_staffing_rules"].fields
        }
        for name in ("min_contributors", "preferred_contributors", "max_contributors"):
            self.assertFalse(fields[name].required)
            self.assertEqual(fields[name].kind, "int")
        self.assertEqual(fields["personnel_role"].choices, staffing.PERSONNEL_ROLES)

    def test_page_and_registry(self):
        page = registry.page_for_tab_text("Task Staffing — Editor")
        self.assertEqual(page.group, "Tasks")
        self.assertEqual(page.tables, ("task_staffing_rules",))
        self.assertEqual(registry.check_registry(), [])

    def test_editor_wiring(self):
        candidate = inspect.getsource(editor.validate_candidate)
        installer = inspect.getsource(editor.install_network_editor)
        self.assertIn("task_staffing_rules.validate_staffing(tmp_root, res)", candidate)
        self.assertIn('"task_staffing_rules", "Task Staffing"', installer)
