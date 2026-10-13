import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock

import doda_capability_staffing_draft_policy as policy
import doda_task_draft_policy as task_policy


class CapabilityStaffingPolicyTests(unittest.TestCase):
    def app(self, dirty=False):
        return NS(
            capability_staffing_rules_editor=NS(dirty=dirty),
            destroy=Mock(), protocol=Mock(),
        )

    def test_missing_editor_is_clean(self):
        self.assertFalse(policy.capability_staffing_draft_dirty(NS()))

    def test_missing_dirty_attribute_is_clean(self):
        self.assertFalse(policy.capability_staffing_draft_dirty(
            NS(capability_staffing_rules_editor=NS())
        ))

    def test_dirty_editor_detected(self):
        self.assertTrue(policy.capability_staffing_draft_dirty(self.app(True)))

    def test_clean_project_change_allowed(self):
        dialogs = Mock()
        self.assertTrue(policy.allow_capability_staffing_project_change(
            self.app(), dialogs
        ))
        dialogs.showwarning.assert_not_called()

    def test_dirty_project_change_blocked_and_retained(self):
        app, dialogs = self.app(True), Mock()
        self.assertFalse(policy.allow_capability_staffing_project_change(
            app, dialogs
        ))
        dialogs.showwarning.assert_called_once()
        self.assertTrue(app.capability_staffing_rules_editor.dirty)

    def test_clean_close_delegates(self):
        app, dialogs, previous = self.app(), Mock(), Mock()
        app._network_close_handler = previous
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        app._network_close_handler()
        previous.assert_called_once()
        dialogs.askyesno.assert_not_called()
        app.destroy.assert_not_called()

    def test_dirty_close_cancel_stops_chain(self):
        app, dialogs, previous = self.app(True), Mock(), Mock()
        dialogs.askyesno.return_value = False
        app._network_close_handler = previous
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        app._network_close_handler()
        previous.assert_not_called()
        app.destroy.assert_not_called()
        self.assertTrue(app.capability_staffing_rules_editor.dirty)

    def test_dirty_close_accept_delegates_without_clearing_draft(self):
        app, dialogs, previous = self.app(True), Mock(), Mock()
        dialogs.askyesno.return_value = True
        app._network_close_handler = previous
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        app._network_close_handler()
        previous.assert_called_once()
        self.assertTrue(app.capability_staffing_rules_editor.dirty)

    def test_no_previous_handler_destroys(self):
        app, dialogs = self.app(), Mock()
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        app._network_close_handler()
        app.destroy.assert_called_once()

    def test_window_protocol_uses_same_handler(self):
        app = self.app()
        policy.install_capability_staffing_draft_close_guard(app, Mock())
        app.protocol.assert_called_once_with(
            "WM_DELETE_WINDOW", app._network_close_handler
        )

    def test_installation_is_idempotent(self):
        app, dialogs = self.app(), Mock()
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        first = app._network_close_handler
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        self.assertIs(first, app._network_close_handler)
        app.protocol.assert_called_once()

    def test_task_cancel_after_staffing_accept_preserves_chain(self):
        app = self.app(True)
        app.task_templates_editor = NS(dirty=True)
        previous = Mock()
        app._network_close_handler = previous
        dialogs = Mock()
        dialogs.askyesno.side_effect = [True, False]
        task_policy.install_task_draft_close_guard(app, dialogs)
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        app._network_close_handler()
        self.assertEqual(dialogs.askyesno.call_count, 2)
        previous.assert_not_called()
        app.destroy.assert_not_called()
        self.assertTrue(app.capability_staffing_rules_editor.dirty)
        self.assertTrue(app.task_templates_editor.dirty)

    def test_both_accept_reach_existing_network_handler(self):
        app = self.app(True)
        app.task_templates_editor = NS(dirty=True)
        previous = Mock()
        app._network_close_handler = previous
        dialogs = Mock()
        dialogs.askyesno.return_value = True
        task_policy.install_task_draft_close_guard(app, dialogs)
        policy.install_capability_staffing_draft_close_guard(app, dialogs)
        app._network_close_handler()
        self.assertEqual(dialogs.askyesno.call_count, 2)
        previous.assert_called_once()
        app.destroy.assert_not_called()


if __name__ == "__main__":
    unittest.main()
