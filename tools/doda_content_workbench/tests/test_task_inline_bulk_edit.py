import ast
import copy
import inspect
import textwrap
import unittest
from types import SimpleNamespace as NS
from unittest.mock import Mock

import doda_task_templates_editor as tasks
import doda_task_inline_bulk_edit as inline


class Variable:
    def __init__(self):
        self.value=""
        self.callbacks=[]
    def get(self):
        return self.value
    def set(self,value):
        self.value=value
        for callback in self.callbacks:
            callback()
    def trace_add(self,mode,callback):
        self.callbacks.append(callback)
        return str(len(self.callbacks))


class Widget:
    def __init__(self,state="normal"):
        self.state=state
        self.values=()
        self.selection_range=Mock()
        self.icursor=Mock()
        self.bindings={}
    def cget(self,name):
        return self.state if name=="state" else self.values
    def configure(self,**kwargs):
        self.state=kwargs.get("state",self.state)
        self.values=kwargs.get("values",self.values)
    def bind(self,event,callback,**kwargs):
        self.bindings[event]=callback
    def after_idle(self,callback):
        callback()


class Text(Widget):
    def __init__(self):
        super().__init__()
        self.text=""
        self.modified=False
        self.tag_add=Mock()
        self.mark_set=Mock()
    def get(self,*args):
        return self.text
    def delete(self,*args):
        self.text=""
        self.modified=True
    def insert(self,index,text):
        self.text=text
        self.modified=True
    def edit_modified(self,value=None):
        if value is not None:
            self.modified=bool(value)
        return self.modified


class Tree:
    def __init__(self):
        self.selected=("A","B")
        self.item=Mock()
    def selection(self):
        return self.selected
    def __getitem__(self,name):
        return ("task_template_id","display_name","priority","target_type","loop_task")
    def selection_remove(self,*args):
        self.selected=()
    def selection_set(self,*args):
        self.selected=tuple(args)


class TaskInlineBulkTests(unittest.TestCase):
    def setUp(self):
        self.editor=tasks.TaskTemplatesEditor.__new__(tasks.TaskTemplatesEditor)
        e=self.editor
        self.base=dict(task_template_id="A",display_name="One",description="First",capability_id="",priority="NORMAL",target_type="TERRITORY",target_family_id="",loop_task="FALSE",time_to_complete_minutes="",reward_mode="CONTINUOUS",payout_count="0",sort_order="1",active="FALSE")
        e.loaded_rows=[dict(self.base),{**self.base,"task_template_id":"B","display_name":"Two","description":"Second","sort_order":"2"},{**self.base,"task_template_id":"C","display_name":"Three","sort_order":"3"}]
        e.vars={name:Variable() for name in tasks.FIELDS if name!="description"}
        e.widgets={name:Widget("readonly" if name in inline.DROPDOWNS else "normal") for name in e.vars}
        e.description=Text()
        e.widgets["description"]=e.description
        e.tree=Tree()
        e.dirty=False
        e.editing_id=None
        e._multi_selection=True
        e._set_status=Mock()
        e.app=NS(log=Mock())
        e._validate_rows=Mock()
        e.commit=Mock()
        e._render_draft=Mock()
        choices={"capability_id":["","CAP_TEST"],"priority":["NORMAL","HIGH"],"target_type":["STATION","TERRITORY","MISSION_AREA"],"target_family_id":["","TECH_LAB"],"reward_mode":["CONTINUOUS","PERIODIC_LUMP_SUM"]}
        e.choices=lambda name:choices.get(name,[])
        self.controller=inline.install_task_inline(e)
        self.controller.begin(e.tree.selection())

    def apply(self):
        return inline.apply_task_inline(self.editor)

    def test_non_identity_fields_are_editable(self):
        self.assertEqual(self.editor.widgets["task_template_id"].state,"disabled")
        self.assertEqual(self.editor.widgets["display_name"].state,"normal")
        self.assertEqual(self.editor.description.state,"normal")
        self.assertEqual(self.editor.widgets["active"].state,"readonly")

    def test_common_values_are_visible(self):
        self.assertEqual(self.editor.vars["priority"].get(),"NORMAL")
        self.assertEqual(self.editor.vars["payout_count"].get(),"0")
        self.assertEqual(self.editor.vars["active"].get(),"FALSE")

    def test_mixed_values_use_placeholder(self):
        self.assertEqual(self.editor.vars["display_name"].get(),"Multiple values")
        self.assertEqual(self.editor.description.get(),"Multiple values")

    def test_all_blank_remains_blank(self):
        self.assertEqual(self.editor.vars["capability_id"].get(),"")
        self.assertEqual(self.editor.vars["time_to_complete_minutes"].get(),"")

    def test_display_does_not_create_edits(self):
        self.assertEqual(self.controller.changes,{})
        self.assertFalse(self.editor.dirty)

    def test_focus_entry_does_not_change_data(self):
        self.controller.focus("display_name")
        self.editor.widgets["display_name"].selection_range.assert_called_once_with(0,"end")
        self.assertEqual(self.controller.changes,{})

    def test_focus_description_selects_placeholder_without_edit(self):
        self.controller.focus("description")
        self.editor.description.tag_add.assert_called_once_with("sel","1.0","end-1c")
        self.assertEqual(self.controller.changes,{})

    def test_typing_tracks_only_the_changed_field(self):
        self.editor.vars["display_name"].set("New")
        self.assertEqual(self.controller.changes,{"display_name":"New"})
        self.assertFalse(self.editor.dirty)

    def test_description_modified_event_tracks_text_only(self):
        self.editor.description.insert("1.0","New description")
        self.controller.description_modified()
        self.assertEqual(self.controller.changes,{"description":"New description"})
        self.assertFalse(self.editor.description.modified)

    def test_programmatic_description_events_do_not_become_edits(self):
        self.controller.description_modified()
        self.assertEqual(self.controller.changes,{})

    def test_last_description_edit_is_flushed_on_apply(self):
        self.editor.description.insert("1.0","New description")
        self.assertTrue(self.apply())
        self.assertEqual([row["description"] for row in self.editor.loaded_rows], ["New description","New description","First"])

    def test_untouched_apply_skips_validation(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows,before)
        self.editor._validate_rows.assert_not_called()

    def test_apply_changes_only_selected_field_and_rows(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.vars["display_name"].set("New")
        self.assertTrue(self.apply())
        for old,row in zip(before,self.editor.loaded_rows):
            for field in tasks.FIELDS:
                if row["task_template_id"] in ("A","B") and field=="display_name":
                    self.assertEqual(row[field],"New")
                else:
                    self.assertEqual(row[field],old[field])
        self.assertTrue(self.editor.dirty)
        self.editor.commit.assert_not_called()

    def test_apply_reloads_common_display_without_new_edits(self):
        self.editor.vars["display_name"].set("New")
        self.assertTrue(self.apply())
        self.assertEqual(self.editor.vars["display_name"].get(),"New")
        self.assertEqual(self.controller.changes,{})
        self.assertFalse(self.apply())

    def test_boolean_edit_is_explicit_not_automatic_activation(self):
        self.editor.vars["loop_task"].set("TRUE")
        self.assertTrue(self.apply())
        self.assertEqual([r["loop_task"] for r in self.editor.loaded_rows],["TRUE","TRUE","FALSE"])
        self.assertEqual([r["active"] for r in self.editor.loaded_rows],["FALSE","FALSE","FALSE"])

    def test_blank_field_accepts_new_value(self):
        self.editor.vars["time_to_complete_minutes"].set("10")
        self.assertTrue(self.apply())
        self.assertEqual([r["time_to_complete_minutes"] for r in self.editor.loaded_rows],["10","10",""])

    def test_explicit_clear_of_optional_field(self):
        self.editor.loaded_rows[0]["time_to_complete_minutes"]="10"
        self.controller.begin(("A","B"),force=True)
        self.editor.vars["time_to_complete_minutes"].set("")
        self.assertTrue(self.apply())
        self.assertEqual(self.editor.loaded_rows[0]["time_to_complete_minutes"],"")

    def test_required_description_clear_is_atomic(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.description.delete("1.0","end")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows,before)
        self.assertEqual(self.controller.changes,{"description":""})

    def test_invalid_integer_is_atomic(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.vars["sort_order"].set("1.5")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows,before)
        self.assertFalse(self.editor.dirty)

    def test_invalid_boolean_is_atomic(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.vars["loop_task"].set("maybe")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows,before)

    def test_placeholder_is_never_applied(self):
        self.editor.vars["display_name"].set("Multiple values")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"One")

    def test_identity_trace_is_ignored_and_identity_injection_rejected(self):
        self.editor.vars["task_template_id"].set("NEW")
        self.assertEqual(self.controller.changes,{})
        self.controller.changes["task_template_id"]="NEW"
        self.assertFalse(self.apply())
        self.assertEqual([r["task_template_id"] for r in self.editor.loaded_rows],["A","B","C"])

    def test_unknown_capability_is_atomic(self):
        self.editor.vars["capability_id"].set("MISSING")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows[0]["capability_id"],"")

    def test_cross_field_validation_failure_on_one_row_blocks_all(self):
        self.editor.loaded_rows[1].update(active="TRUE",capability_id="CAP_TEST")
        self.controller.begin(("A","B"),force=True)
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.vars["loop_task"].set("TRUE")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows,before)
        self.editor._validate_rows.assert_not_called()

    def test_full_candidate_validation_failure_keeps_prior_dirty_draft(self):
        self.editor.dirty=True
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.vars["display_name"].set("New")
        self.editor._validate_rows.side_effect=ValueError("project invalid")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows,before)
        self.assertTrue(self.editor.dirty)
        self.assertEqual(self.controller.changes,{"display_name":"New"})

    def test_candidate_read_error_is_atomic(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.vars["display_name"].set("New")
        self.editor._validate_rows.side_effect=OSError("read failed")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows,before)

    def test_stale_selection_is_rejected(self):
        self.editor.vars["display_name"].set("New")
        self.editor.tree.selected=("B","C")
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"One")

    def test_stale_draft_is_not_overwritten(self):
        self.editor.vars["display_name"].set("New")
        self.editor.loaded_rows[0]["display_name"]="External"
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"External")

    def test_change_during_validation_is_not_overwritten(self):
        self.editor.vars["display_name"].set("New")
        def validate(_rows):
            self.editor.loaded_rows[0]["display_name"]="External"
        self.editor._validate_rows.side_effect=validate
        self.assertFalse(self.apply())
        self.assertEqual(self.editor.loaded_rows[0]["display_name"],"External")
        self.assertEqual(self.editor.loaded_rows[1]["display_name"],"Two")

    def test_same_selection_keeps_pending_edits(self):
        self.editor.vars["display_name"].set("New")
        self.controller.begin(("A","B"))
        self.assertEqual(self.controller.changes,{"display_name":"New"})

    def test_revert_form_resets_inputs_not_draft(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.vars["display_name"].set("New")
        self.editor.revert()
        self.assertEqual(self.controller.changes,{})
        self.assertEqual(self.editor.loaded_rows,before)
        self.assertEqual(self.editor.vars["display_name"].get(),"Multiple values")

    def test_return_to_single_restores_values_and_protected_id(self):
        self.editor.tree.selected=("B",)
        self.editor.on_select()
        self.assertFalse(self.controller.active)
        self.assertEqual(self.editor.vars["display_name"].get(),"Two")
        self.assertEqual(self.editor.description.get(),"Second")
        self.assertEqual(self.editor.widgets["task_template_id"].state,"disabled")
        self.assertEqual(self.editor.widgets["active"].values,("TRUE","FALSE"))

    def test_deselect_does_not_change_rows(self):
        before=copy.deepcopy(self.editor.loaded_rows)
        self.editor.tree.selected=()
        self.editor.on_select()
        self.assertFalse(self.controller.active)
        self.assertEqual(self.editor.loaded_rows,before)

    def test_apply_keeps_multi_selection(self):
        self.editor.vars["display_name"].set("New")
        self.assertTrue(self.apply())
        self.assertEqual(self.editor.tree.selection(),("A","B"))
        self.editor._render_draft.assert_not_called()
        self.assertEqual(self.editor.tree.item.call_count,2)

    def test_boolean_controls_are_dropdowns(self):
        tree=ast.parse(textwrap.dedent(inspect.getsource(tasks.TaskTemplatesEditor.build)))
        self.assertFalse(any(isinstance(node,ast.Attribute) and node.attr=="Checkbutton" for node in ast.walk(tree)))

    def test_no_bulk_window_is_created(self):
        tree=ast.parse(inspect.getsource(inline))
        self.assertFalse(any(isinstance(node,ast.Attribute) and node.attr=="Toplevel" for node in ast.walk(tree)))
