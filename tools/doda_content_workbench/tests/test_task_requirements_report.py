import copy
import inspect
import unittest
from unittest.mock import Mock, patch
import doda_task_requirements_preview as preview


class TaskRequirementsReportTests(unittest.TestCase):
    def setUp(self):
        self.model = preview.build_preview(
            {
                "task_template_id": "INVESTIGATE",
                "display_name": "Investigate",
                "active": "FALSE",
                "capability_id": "",
                "target_type": "TERRITORY",
                "target_family_id": "",
            },
            [{
                "taskTemplateId": "INVESTIGATE",
                "personnelRole": "AGENT",
                "minContributors": 1,
                "preferredContributors": 1,
                "maxContributors": 2,
                "sortOrder": 10,
                "active": False,
            }],
            [],
        )

    def test_report_header_and_template(self):
        report = preview.build_report(self.model, [])
        self.assertTrue(report.startswith("=== SAVED TASK REQUIREMENTS REPORT ==="))
        self.assertIn("Template: INVESTIGATE", report)
        self.assertIn("AGENT: minimum=1; preferred=1; maximum=2", report)
        self.assertTrue(report.endswith("\n"))

    def test_report_scope(self):
        report = preview.build_report(self.model, [])
        self.assertIn("Unsaved drafts are excluded.", report)
        self.assertIn("No live eligibility or inventory checks.", report)
        self.assertIn("reopen to refresh", report)

    def test_snapshot_warnings_are_labeled(self):
        report = preview.build_report(self.model, ["Other task has a draft minimum"])
        self.assertIn("SNAPSHOT DEFINITION WARNINGS (ALL LOADED TEMPLATES)", report)
        self.assertIn("Other task has a draft minimum", report)

    def test_no_warnings(self):
        report = preview.build_report(self.model, [])
        self.assertTrue(report.endswith("  None.\n"))

    def test_copy_exact_report_and_order(self):
        owner = Mock()
        report = preview.copy_requirements_report(owner, self.model, ["draft warning"])
        owner.clipboard_clear.assert_called_once_with()
        owner.clipboard_append.assert_called_once_with(report)
        owner.update_idletasks.assert_called_once_with()
        owner.log.assert_called_once_with(
            "Copied saved Task Requirements Preview: INVESTIGATE"
        )
        self.assertEqual(
            [call[0] for call in owner.mock_calls],
            ["clipboard_clear", "clipboard_append", "update_idletasks", "log"],
        )

    def test_copy_selected_model(self):
        other = copy.deepcopy(self.model)
        other["template"]["task_template_id"] = "OTHER"
        other["template"]["display_name"] = "Other task"
        other["staffingRules"] = []
        report = preview.copy_requirements_report(Mock(), other, [])
        self.assertIn("Template: OTHER", report)
        self.assertNotIn("Template: INVESTIGATE", report)

    def test_copy_failure_not_logged_as_success(self):
        owner = Mock()
        owner.clipboard_append.side_effect = RuntimeError("clipboard unavailable")
        with self.assertRaises(RuntimeError):
            preview.copy_requirements_report(owner, self.model, [])
        owner.log.assert_not_called()
        owner.update_idletasks.assert_not_called()

    def test_inputs_not_mutated(self):
        warnings = ["draft warning"]
        before = copy.deepcopy((self.model, warnings))
        preview.copy_requirements_report(Mock(), self.model, warnings)
        self.assertEqual(before, (self.model, warnings))

    def test_report_uses_loaded_snapshot_without_rereading(self):
        with patch.object(
            preview, "load_previews", side_effect=AssertionError("unexpected reload")
        ), patch.object(
            preview, "source_hashes", side_effect=AssertionError("unexpected reread")
        ):
            first = preview.build_report(self.model, [])
            second = preview.build_report(self.model, [])
        self.assertEqual(first, second)

    def test_copy_button_and_failure_dialog_wiring(self):
        source = inspect.getsource(preview.open_task_requirements_preview)
        self.assertIn('text="Copy Requirements Report"', source)
        self.assertIn("copy_requirements_report(owner, models[selected], warnings)", source)
        self.assertIn("except tk.TclError as error:", source)
        self.assertIn("No saved template is selected.", source)
        self.assertEqual(source.count("load_previews("), 1)
