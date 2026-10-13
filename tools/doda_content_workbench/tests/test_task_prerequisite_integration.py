import inspect
import unittest
import doda_content_gui as gui
import doda_content_workbench as core
import doda_network_editor as editor
import doda_page_registry as registry
import doda_task_templates_editor as task_editor
import doda_task_prerequisite_rules as prerequisites


class TaskPrerequisiteIntegrationTests(unittest.TestCase):
    def test_columns_and_key(self):
        spec = registry.TABLE_METADATA["task_prerequisites"]
        self.assertEqual(spec.columns, prerequisites.COLUMNS)
        self.assertEqual(spec.key_columns, ("prerequisite_id",))

    def test_page_and_registry(self):
        page = registry.page_for_tab_text("Task Prerequisites — Editor")
        self.assertEqual(page.group, "Tasks")
        self.assertEqual(page.tables, ("task_prerequisites",))
        self.assertEqual(registry.check_registry(), [])

    def test_field_metadata(self):
        fields = {f.name: f for f in registry.TABLE_METADATA["task_prerequisites"].fields}
        self.assertEqual(fields["task_template_id"].kind, "task_ref")
        self.assertEqual(fields["requirement_kind"].choices, prerequisites.KINDS)
        self.assertEqual(fields["scope"].choices, prerequisites.SCOPES)
        self.assertFalse(fields["min_quantity"].required)
        self.assertTrue(fields["description"].multiline)

    def test_main_validation_hook(self):
        self.assertIn("doda_task_prerequisite_rules.validate_prerequisites",
                      inspect.getsource(core.validate_project))

    def test_candidate_and_task_staging(self):
        candidate = inspect.getsource(editor.validate_candidate)
        self.assertIn("prerequisite_rules.validate_prerequisites(tmp_root, res)", candidate)
        self.assertIn("not (tmp_src / prerequisite_file).is_file()", candidate)
        self.assertIn(prerequisites.PREREQUISITES_FILE, task_editor.FILES)
        installer = inspect.getsource(editor.install_network_editor)
        self.assertIn('"task_prerequisites", "Task Prerequisites"', installer)

    def test_gui_validate_and_export_hooks(self):
        source = inspect.getsource(gui.ContentWorkbenchApp.run_network_rules)
        self.assertIn("doda_task_prerequisite_rules.export(self.project_root)", source)
        self.assertIn("doda_task_prerequisite_rules.validate_prerequisites", source)
        self.assertIn("Task prerequisites exported:", source)
