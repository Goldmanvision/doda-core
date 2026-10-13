import unittest
from unittest.mock import Mock, patch
import doda_task_flow_preview_ui as ui


class PreviewUITests(unittest.TestCase):
    def setUp(self):
        self.items = [
            {"template": {"task_template_id": "A"}},
            {"template": {"task_template_id": "B"}},
        ]

    def test_default_selection(self):
        self.assertEqual(ui.initial_index(self.items, None), 0)

    def test_selected_template(self):
        self.assertEqual(ui.initial_index(self.items, "B"), 1)

    def test_empty_selection(self):
        self.assertEqual(ui.initial_index([], None), -1)

    def test_missing_saved_template(self):
        with self.assertRaises(ValueError):
            ui.initial_index(self.items, "UNSAVED")

    def test_validation_failure_no_window(self):
        owner = Mock()
        with patch.object(
            ui.preview, "load_previews",
            side_effect=ValueError("invalid source"),
        ), patch.object(ui.tk, "Toplevel") as window, patch.object(
            ui.messagebox, "showerror",
        ) as dialog:
            self.assertIsNone(ui.open_task_flow_preview(owner))
            window.assert_not_called()
            dialog.assert_called_once()
            owner.log.assert_called_once()
