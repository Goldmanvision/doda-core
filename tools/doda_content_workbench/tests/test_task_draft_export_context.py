import unittest
from types import SimpleNamespace
import test_export_chain as chain


class TaskDraftExportContextTests(unittest.TestCase):
    def setUp(self):
        fixture=chain.ExportChainTests()
        fixture.setUp()
        self.fn=fixture.fn
        self.app=fixture.app
        self.dialog=fixture.dialog

    def test_dirty_task_draft_warns_but_preserves_saved_source_export_chain(self):
        self.app.task_templates_editor=SimpleNamespace(dirty=True)
        self.fn(self.app)
        self.app.log.assert_any_call("Task Templates note: applied drafts are not included; this action uses saved source. Save to Source first to include them.")
        self.app.run_command.assert_called_once()
        self.app.run_network_rules.assert_called_once_with("export",announce=False)
        self.dialog.showinfo.assert_called_once()

    def test_clean_task_editor_adds_no_draft_warning(self):
        self.app.task_templates_editor=SimpleNamespace(dirty=False)
        self.fn(self.app)
        self.assertFalse(any("Task Templates note:" in str(call.args[0]) for call in self.app.log.call_args_list))
        self.app.run_command.assert_called_once()
        self.app.run_network_rules.assert_called_once_with("export",announce=False)
