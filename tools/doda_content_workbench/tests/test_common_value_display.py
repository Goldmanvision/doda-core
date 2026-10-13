import unittest
from unittest.mock import Mock
from types import SimpleNamespace as NS

import doda_row_selection as selection
import doda_inline_bulk_edit as inline


class Variable:
    def __init__(self):
        self.value = ""
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
    def __init__(self):
        self.state = "normal"
    def cget(self, name):
        return () if name == "values" else self.state
    def configure(self, **kwargs):
        self.state = kwargs.get("state", self.state)
    def bind(self, *args, **kwargs):
        pass


class CommonValueDisplayTests(unittest.TestCase):
    def display(self, values):
        return selection.selection_display([{"x": v} for v in values], "x", show_common=True)

    def test_same_integer_text_shows_actual_value(self):
        self.assertEqual(self.display(["1", "1", "1"]), "1")

    def test_same_text_shows_actual_value(self):
        self.assertEqual(self.display(["AGENT", "AGENT"]), "AGENT")

    def test_same_boolean_shows_actual_value(self):
        self.assertEqual(self.display(["false", "false"]), "false")

    def test_all_blank_remains_blank(self):
        self.assertEqual(self.display(["", "", ""]), "")

    def test_different_values_show_multiple(self):
        self.assertEqual(self.display(["1", "2"]), "Multiple values")

    def test_mixed_blank_and_populated_show_multiple(self):
        self.assertEqual(self.display(["", "1"]), "Multiple values")

    def test_empty_selection_is_blank(self):
        self.assertEqual(self.display([]), "")

    def test_legacy_task_template_display_is_unchanged(self):
        self.assertEqual(selection.selection_display([{"x": "1"}, {"x": "1"}], "x"), "Multiple values")

    def test_missing_and_blank_are_equivalent(self):
        self.assertEqual(selection.selection_display([{}, {"x": ""}], "x", show_common=True), "")

    def test_distinct_authored_representations_are_not_normalized(self):
        self.assertEqual(self.display(["1", "01"]), "Multiple values")


class CommonValueInlineTests(unittest.TestCase):
    def setUp(self):
        fields=tuple(NS(name=n,label=n,kind="text",required=False,multiline=False) for n in ("id","minimum","preferred","maximum","blank"))
        self.editor=NS(
            spec=NS(table="example",fields=fields,key_columns=("id",)),
            rows=[dict(id=i,minimum="1",preferred="1",maximum="2",blank="") for i in ("A","B","C")],
            vars={f.name:Variable() for f in fields}, widgets={f.name:Widget() for f in fields},
            tree=Mock(), app=NS(project_root="root",log=Mock()),
            dirty=False,_set_status=Mock(),_ref_choices=Mock(),
        )
        self.editor.tree.selection.return_value=("0","1","2")
        self.controller=inline.install_inline(self.editor)
        self.controller.begin(("0","1","2"))

    def test_common_staffing_counts_display_without_becoming_edits(self):
        self.assertEqual([self.editor.vars[n].get() for n in ("minimum","preferred","maximum")], ["1","1","2"])
        self.assertEqual(self.controller.changes,{})
        self.assertFalse(self.editor.dirty)

    def test_apply_without_edit_preserves_rows_and_skips_validation(self):
        before=[dict(r) for r in self.editor.rows]
        validate=Mock()
        self.assertFalse(inline.apply_inline(self.editor,validate,None))
        self.assertEqual(self.editor.rows,before)
        validate.assert_not_called()

    def test_edit_other_field_preserves_common_counts(self):
        self.editor.vars["blank"].set("note")
        validate=Mock(return_value=NS(valid=True,errors=[]))
        self.assertTrue(inline.apply_inline(self.editor,validate,None))
        self.assertEqual([r["minimum"] for r in self.editor.rows],["1","1","1"])
        self.assertEqual([r["maximum"] for r in self.editor.rows],["2","2","2"])
        self.assertEqual(self.editor.vars["blank"].get(),"note")
        self.assertEqual(self.controller.changes,{})

    def test_explicit_clear_of_common_value_is_tracked(self):
        self.editor.vars["minimum"].set("")
        self.assertEqual(self.controller.changes,{"minimum":""})
        validate=Mock(return_value=NS(valid=True,errors=[]))
        self.assertTrue(inline.apply_inline(self.editor,validate,None))
        self.assertEqual([r["minimum"] for r in self.editor.rows],["","",""])
        self.assertEqual(self.editor.vars["minimum"].get(),"")

    def test_protected_common_key_component_stays_disabled(self):
        self.editor.spec.key_columns=("id","preferred")
        self.controller.begin(("0","1","2"),force=True)
        self.assertEqual(self.editor.vars["preferred"].get(),"1")
        self.assertEqual(self.editor.widgets["preferred"].state,"disabled")
        self.assertEqual(self.controller.changes,{})
