import ast
import inspect
import textwrap
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
import doda_row_selection as selection
import doda_network_editor as shared
import doda_task_templates_editor as tasks


class Variable:
    def __init__(self, value=""):
        self.value = value
        self.callbacks = []
    def trace_add(self, mode, callback):
        self.callbacks.append(callback)
        return str(len(self.callbacks))
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
        for callback in self.callbacks:
            callback()


class Widget:
    def __init__(self, state="normal"):
        self.state = state
    def cget(self, name):
        return () if name == "values" else self.state
    def configure(self, **kwargs):
        self.state = kwargs.get("state", self.state)
    def bind(self, *args, **kwargs):
        pass


class RowSelectionTests(unittest.TestCase):
    def shared_editor(self):
        fields = [
            SimpleNamespace(name=name, kind="text")
            for name in ("id", "value", "blank")
        ]
        rows = [
            {"id": "A", "value": "1", "blank": ""},
            {"id": "B", "value": "2", "blank": ""},
        ]
        tree = Mock()
        tree.selection.return_value = ("0", "1")
        return SimpleNamespace(
            title="Test", tree=tree, rows=rows,
            spec=SimpleNamespace(fields=fields, key_columns=("id",)),
            selected_index=0,
            vars={f.name: Variable() for f in fields},
            widgets={
                f.name: Widget("readonly" if f.name == "id" else "normal")
                for f in fields
            },
            _ref_choices=Mock(), _set_status=Mock(), _clear_form=Mock(),
            _form_row=Mock(), dirty=False,
        )

    def test_extended_selection_configured_on_both_tables(self):
        for method in (
            shared.NetworkTableEditor._build,
            tasks.TaskTemplatesEditor.build,
        ):
            tree = ast.parse(textwrap.dedent(inspect.getsource(method)))
            modes = [
                kw.value.value
                for node in ast.walk(tree) if isinstance(node, ast.Call)
                for kw in node.keywords
                if kw.arg == "selectmode" and isinstance(kw.value, ast.Constant)
            ]
            self.assertIn("extended", modes)

    def test_display_blank_and_occupied_fields(self):
        self.assertEqual(
            selection.selection_display([{"x": ""}, {"x": ""}], "x"), ""
        )
        self.assertEqual(
            selection.selection_display([{"x": "1"}, {"x": "1"}], "x"),
            "Multiple values",
        )
        self.assertEqual(
            selection.selection_display([{"x": ""}, {"x": "1"}], "x"),
            "Multiple values",
        )

    def test_single_selection_action_allowed(self):
        obj = self.shared_editor()
        obj.tree.selection.return_value = ("0",)
        dialogs = Mock()
        self.assertTrue(selection.require_single(obj, "Apply", dialogs))
        dialogs.showwarning.assert_not_called()

    def test_multiple_selection_action_blocked(self):
        obj = self.shared_editor()
        dialogs = Mock()
        self.assertFalse(selection.require_single(obj, "Apply", dialogs))
        dialogs.showwarning.assert_called_once()

    def test_shared_multiple_selection_is_editable_with_protected_keys_and_preserves_rows(self):
        obj = self.shared_editor()
        before = [dict(row) for row in obj.rows]
        shared.NetworkTableEditor._on_select(obj)
        self.assertIsNone(obj.selected_index)
        self.assertEqual(obj.vars["value"].get(), "Multiple values")
        self.assertEqual(obj.vars["blank"].get(), "")
        self.assertEqual(obj.widgets["id"].state, "disabled")
        self.assertEqual(obj.widgets["value"].state, "normal")
        self.assertEqual(obj.widgets["blank"].state, "normal")
        self.assertEqual(obj._inline_bulk.changes, {})
        self.assertEqual(obj.rows, before)
        self.assertFalse(obj.dirty)

    def test_return_to_single_selection_restores_fields(self):
        obj = self.shared_editor()
        shared.NetworkTableEditor._on_select(obj)
        obj.tree.selection.return_value = ("1",)
        shared.NetworkTableEditor._on_select(obj)
        self.assertEqual(obj.selected_index, 1)
        self.assertEqual(obj.vars["value"].get(), "2")
        self.assertEqual(obj.widgets["id"].state, "readonly")
        self.assertEqual(obj.widgets["value"].state, "normal")
        self.assertEqual(obj._ref_choices.call_count, 2)

    def test_deselect_last_row_clears_multiple_state(self):
        obj = self.shared_editor()
        shared.NetworkTableEditor._on_select(obj)
        obj.tree.selection.return_value = ()
        shared.NetworkTableEditor._on_select(obj)
        self.assertFalse(obj._multi_selection)
        self.assertIsNone(obj.selected_index)
        obj._clear_form.assert_called_once()
        self.assertEqual(obj.widgets["value"].state, "normal")

    def test_task_template_multiple_selection_preserves_rows(self):
        tree = Mock()
        tree.selection.return_value = ("A", "B")
        rows = [
            dict(task_template_id="A", display_name="One",
                 description="First", capability_id=""),
            dict(task_template_id="B", display_name="Two",
                 description="Second", capability_id=""),
        ]
        obj = SimpleNamespace(
            tree=tree, loaded_rows=rows, editing_id="A", description=Mock(),
            choices=Mock(return_value=[""]), _set_status=Mock(), app=SimpleNamespace(log=Mock()),
            vars={
                name: Variable()
                for name in ("task_template_id", "display_name", "capability_id")
            },
            widgets={
                name: Widget()
                for name in ("task_template_id", "display_name", "capability_id")
            },
        )
        tasks.TaskTemplatesEditor.on_select(obj)
        self.assertIsNone(obj.editing_id)
        self.assertEqual(obj.vars["display_name"].get(), "Multiple values")
        self.assertEqual(obj.vars["capability_id"].get(), "")
        obj.description.insert.assert_called_once_with("1.0", "Multiple values")
        self.assertEqual(rows[0]["display_name"], "One")

    def test_shared_single_record_actions_blocked_for_multiple_rows(self):
        obj = self.shared_editor()
        with patch.object(shared.messagebox, "showwarning") as dialog:
            for name in ("delete_record", "copy_csv", "paste_csv"):
                getattr(shared.NetworkTableEditor, name)(obj)
        self.assertEqual(dialog.call_count, 3)
        obj._form_row.assert_not_called()
        self.assertFalse(obj.dirty)

    def test_task_remove_remains_blocked_for_multiple_rows(self):
        obj = SimpleNamespace(tree=Mock(), record=Mock(), commit=Mock())
        obj.tree.selection.return_value = ("A", "B")
        with patch.object(tasks.messagebox, "showwarning") as dialog:
            tasks.TaskTemplatesEditor.remove(obj)
        self.assertEqual(dialog.call_count, 1)
        obj.record.assert_not_called()
        obj.commit.assert_not_called()

    def test_shared_bulk_apply_uses_record_panel(self):
        obj = self.shared_editor()
        with patch.object(shared, "apply_inline") as apply:
            shared.NetworkTableEditor.apply_record(obj)
        apply.assert_called_once_with(
            obj, shared.validate_candidate, shared.collection_model_rules.decimal_value,
        )
        obj._form_row.assert_not_called()
        self.assertFalse(obj.dirty)

    def test_shared_same_selection_event_keeps_pending_inline_edit(self):
        obj = self.shared_editor()
        shared.NetworkTableEditor._on_select(obj)
        obj.vars["value"].set("changed")
        shared.NetworkTableEditor._on_select(obj)
        self.assertEqual(obj.vars["value"].get(), "changed")
        self.assertEqual(obj._inline_bulk.changes, {"value": "changed"})
        self.assertEqual(obj._ref_choices.call_count, 1)

    def test_bulk_collection_kind_does_not_clear_untouched_fields(self):
        obj = self.shared_editor()
        shared.NetworkTableEditor._on_select(obj)
        before = {name: var.get() for name, var in obj.vars.items()}
        shared.NetworkTableEditor._collection_kind_changed(obj)
        self.assertEqual({name: var.get() for name, var in obj.vars.items()}, before)
        self.assertEqual(obj._inline_bulk.changes, {})

    def test_bulk_prerequisite_kind_does_not_fill_untouched_fields(self):
        obj = self.shared_editor()
        shared.NetworkTableEditor._on_select(obj)
        before = {name: var.get() for name, var in obj.vars.items()}
        shared.NetworkTableEditor._prerequisite_kind_changed(obj)
        self.assertEqual({name: var.get() for name, var in obj.vars.items()}, before)
        self.assertEqual(obj._inline_bulk.changes, {})
