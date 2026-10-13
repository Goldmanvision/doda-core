import ast
import copy
import inspect
import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock

import doda_bulk_edit as bulk
import doda_inline_bulk_edit as inline
import doda_multiselect as multi


class Variable:
    def __init__(self, value=""):
        self.value = value
        self.callbacks = []
    def get(self):
        return self.value
    def set(self, value):
        self.value = value
        for callback in self.callbacks:
            callback()
    def trace_add(self, mode, callback):
        self.callbacks.append(callback)
        return str(len(self.callbacks))


class Widget:
    def __init__(self, state="normal", values=()):
        self.state = state
        self.values = values
        self.bindings = {}
        self.selection_range = Mock()
        self.icursor = Mock()
        self.set_options = Mock()
    def cget(self, name):
        return self.values if name == "values" else self.state
    def configure(self, **kwargs):
        self.state = kwargs.get("state", self.state)
        self.values = kwargs.get("values", self.values)
    def bind(self, event, callback, **kwargs):
        self.bindings[event] = callback
    def after_idle(self, callback):
        callback()


def field(name, kind="text", required=False, choices=()):
    return NS(name=name, label=name, kind=kind, required=required, choices=choices, multiline=False)


class InlineBulkTests(unittest.TestCase):
    def setUp(self):
        fields = (
            field("id", required=True), field("count", "int"), field("blank"),
            field("active", "bool", choices=()), field("evidence", "evidence_multi"),
        )
        self.editor = NS(
            spec=NS(table="example", fields=fields, key_columns=("id",)),
            rows=[dict(id="A", count="3", blank="", active="false", evidence=""),
                  dict(id="B", count="7", blank="", active="false", evidence=""),
                  dict(id="C", count="9", blank="", active="false", evidence="")],
            vars={f.name: Variable() for f in fields},
            widgets={f.name: Widget("readonly" if f.kind == "bool" else "normal", ("true", "false") if f.kind == "bool" else ()) for f in fields},
            tree=Mock(), app=NS(project_root="root", source_directory="source", log=Mock()),
            _set_status=Mock(), _ref_choices=Mock(), dirty=False,
        )
        self.editor.tree.selection.return_value = ("0", "1")
        self.controller = inline.install_inline(self.editor)
        self.controller.begin(("0", "1"))

    def valid(self):
        return Mock(return_value=NS(valid=True, errors=[]))

    def test_same_and_different_populated_fields_show_placeholder(self):
        self.assertEqual(self.editor.vars["count"].get(), "Multiple values")
        self.assertEqual(self.editor.vars["active"].get(), "Multiple values")

    def test_all_blank_fields_stay_blank(self):
        self.assertEqual(self.editor.vars["blank"].get(), "")
        self.assertEqual(self.editor.vars["evidence"].get(), "")

    def test_only_keys_are_disabled(self):
        self.assertEqual(self.editor.widgets["id"].state, "disabled")
        self.assertEqual(self.editor.widgets["count"].state, "normal")
        self.assertEqual(self.editor.widgets["active"].state, "readonly")

    def test_loading_selection_does_not_mark_edits(self):
        self.assertEqual(self.controller.changes, {})
        self.assertFalse(self.editor.dirty)

    def test_focus_selects_placeholder_without_changing_data(self):
        self.controller.focus("count")
        self.editor.widgets["count"].selection_range.assert_called_once_with(0, "end")
        self.assertEqual(self.editor.vars["count"].get(), "Multiple values")
        self.assertEqual(self.controller.changes, {})

    def test_click_blank_field_does_not_mark_edits(self):
        self.controller.focus("blank")
        self.editor.widgets["blank"].selection_range.assert_not_called()
        self.assertEqual(self.controller.changes, {})

    def test_input_tracks_only_edited_field(self):
        self.editor.vars["count"].set("4")
        self.assertEqual(self.controller.changes, {"count": "4"})
        self.assertFalse(self.editor.dirty)

    def test_new_value_in_blank_field(self):
        self.editor.vars["blank"].set("new")
        self.assertEqual(self.controller.changes, {"blank": "new"})

    def test_explicit_clear_is_tracked(self):
        self.editor.vars["count"].set("")
        self.assertEqual(self.controller.changes, {"count": ""})
        self.assertTrue(inline.apply_inline(self.editor, self.valid(), None))
        self.assertEqual([r["count"] for r in self.editor.rows], ["", "", "9"])

    def test_key_writes_cannot_enter_change_map(self):
        self.editor.vars["id"].set("NEW")
        self.assertEqual(self.controller.changes, {})

    def test_untouched_apply_changes_nothing(self):
        before=copy.deepcopy(self.editor.rows)
        validate=self.valid()
        self.assertFalse(inline.apply_inline(self.editor, validate, None))
        self.assertEqual(self.editor.rows, before)
        self.assertFalse(self.editor.dirty)
        validate.assert_not_called()

    def test_apply_changes_only_selected_field_and_rows(self):
        self.editor.vars["blank"].set("new")
        self.assertTrue(inline.apply_inline(self.editor, self.valid(), None))
        self.assertEqual([r["count"] for r in self.editor.rows], ["3", "7", "9"])
        self.assertEqual([r["blank"] for r in self.editor.rows], ["new", "new", ""])
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.controller.changes, {})
        self.assertEqual(self.editor.vars["blank"].get(), "Multiple values")

    def test_invalid_integer_retains_all_rows_and_edit(self):
        before=copy.deepcopy(self.editor.rows)
        self.editor.vars["count"].set("bad")
        self.assertFalse(inline.apply_inline(self.editor, self.valid(), None))
        self.assertEqual(self.editor.rows, before)
        self.assertEqual(self.editor.vars["count"].get(), "bad")
        self.assertFalse(self.editor.dirty)

    def test_placeholder_cannot_be_applied(self):
        self.editor.vars["blank"].set("Multiple values")
        self.assertFalse(inline.apply_inline(self.editor, self.valid(), None))
        self.assertFalse(self.editor.dirty)
        self.assertEqual(self.editor.rows[0]["blank"], "")

    def test_full_validation_failure_is_atomic(self):
        before=copy.deepcopy(self.editor.rows)
        self.editor.vars["count"].set("4")
        validate=Mock(return_value=NS(valid=False, errors=["row two invalid"]))
        self.assertFalse(inline.apply_inline(self.editor, validate, None))
        self.assertEqual(self.editor.rows, before)
        self.assertEqual(self.controller.changes, {"count": "4"})
        self.editor.app.log.assert_called_once()

    def test_validation_exception_preserves_previous_dirty_draft(self):
        self.editor.dirty=True
        before=copy.deepcopy(self.editor.rows)
        self.editor.vars["count"].set("4")
        self.assertFalse(inline.apply_inline(self.editor, Mock(side_effect=OSError("read failed")), None))
        self.assertEqual(self.editor.rows, before)
        self.assertTrue(self.editor.dirty)

    def test_same_selection_event_preserves_pending_edits(self):
        self.editor.vars["count"].set("4")
        self.controller.begin(("0", "1"))
        self.assertEqual(self.controller.changes, {"count": "4"})
        self.assertEqual(self.editor.vars["count"].get(), "4")

    def test_different_selection_resets_unapplied_fields(self):
        self.editor.vars["count"].set("4")
        self.controller.begin(("1", "2"))
        self.assertEqual(self.controller.changes, {})
        self.assertEqual(self.editor.rows[0]["count"], "3")

    def test_end_restores_dropdown_values_and_stops_tracking(self):
        self.editor.widgets["active"].values=("", "true", "false")
        self.controller.end()
        self.assertEqual(self.editor.widgets["active"].values, ("true", "false"))
        self.assertFalse(self.editor.widgets["evidence"]._bulk_mode)
        self.editor.vars["count"].set("8")
        self.assertEqual(self.controller.changes, {})

    def test_stale_selection_rejected(self):
        before=copy.deepcopy(self.editor.rows)
        self.editor.vars["count"].set("4")
        self.editor.tree.selection.return_value=("1", "2")
        self.assertFalse(inline.apply_inline(self.editor, self.valid(), None))
        self.assertEqual(self.editor.rows, before)

    def test_refresh_adds_blank_without_marking_changes(self):
        inline.refresh_inline_choices(self.editor, Mock(), Mock(return_value=[]))
        self.assertEqual(self.editor.widgets["active"].values, ("", "true", "false"))
        self.assertEqual(self.controller.changes, {})

    def test_evidence_commit_does_not_preserve_placeholder(self):
        variable=Variable("Multiple values")
        obj=NS(variable=variable, options=[("EVIDENCE_A", "A")],
               flags={"EVIDENCE_A":NS(get=lambda:True)}, _bulk_mode=True)
        multi.MultiSelectDropdown._commit(obj)
        self.assertEqual(variable.get(), "EVIDENCE_A")

    def test_evidence_blank_summary_is_blank_in_bulk_mode(self):
        obj=NS(variable=Variable(""), summary=Variable(), options=[], flags={}, _bulk_mode=True)
        multi.MultiSelectDropdown._sync(obj)
        self.assertEqual(obj.summary.get(), "")

    def test_evidence_single_mode_keeps_original_prompt(self):
        obj=NS(variable=Variable(""), summary=Variable(), options=[], flags={})
        multi.MultiSelectDropdown._sync(obj)
        self.assertEqual(obj.summary.get(), "Select evidence types...")

    def test_no_bulk_window_code_remains(self):
        for module in (inline, bulk):
            tree=ast.parse(inspect.getsource(module))
            self.assertFalse(any(isinstance(n,ast.Attribute) and n.attr=="Toplevel" for n in ast.walk(tree)))
        self.assertFalse(hasattr(bulk, "open_bulk_editor"))
