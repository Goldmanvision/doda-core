"""Task Templates inline multi-row editing; no editor popup and no source writes."""
import csv
import re
import doda_task_schema as schema
from doda_row_selection import MULTIPLE_VALUES, selection_display, set_form_state

DROPDOWNS = {"capability_id", "priority", "target_type", "target_family_id", "reward_mode", "loop_task", "active"}
BOOLEANS = {"loop_task", "active"}


class TaskInlineEditor:
    def __init__(self, editor):
        self.editor = editor
        self.active = False
        self.loading = False
        self.selection = ()
        self.original = []
        self.changes = {}
        self.description_seen = ""
        for name, variable in editor.vars.items():
            variable.trace_add("write", lambda *_args, n=name: self.changed(n))
            if name == "task_template_id":
                continue
            widget = editor.widgets[name]
            if name in DROPDOWNS:
                widget.bind("<<ComboboxSelected>>", lambda _e, n=name: self.changed(n), add="+")
            else:
                widget.bind("<FocusIn>", lambda _e, n=name: self.focus(n), add="+")
                widget.bind("<ButtonRelease-1>", lambda _e, n=name: self.focus(n), add="+")
        editor.description.bind("<<Modified>>", self.description_modified, add="+")
        editor.description.bind("<FocusIn>", lambda _e: self.focus("description"), add="+")
        editor.description.bind("<ButtonRelease-1>", lambda _e: self.focus("description"), add="+")

    def same_session(self, selected):
        return self.active and tuple(selected) == self.selection and self.editor.loaded_rows == self.original

    def refresh_choices(self, multiple):
        for name in DROPDOWNS & set(self.editor.vars):
            values = ("TRUE", "FALSE") if name in BOOLEANS else tuple(self.editor.choices(name))
            if multiple:
                values = tuple(dict.fromkeys(("",) + tuple(values)))
            self.editor.widgets[name].configure(values=values, state="readonly")

    def begin(self, selected, force=False):
        if not force and self.same_session(selected):
            return
        selected = tuple(selected)
        by_id = {row["task_template_id"]: row for row in self.editor.loaded_rows}
        if len(selected) < 2 or len(selected) != len(set(selected)) or any(key not in by_id for key in selected):
            raise ValueError("Selection no longer matches the task draft. Reselect the rows.")
        self.active = False
        self.loading = True
        try:
            self.selection = selected
            self.original = [dict(row) for row in self.editor.loaded_rows]
            rows = [by_id[key] for key in selected]
            self.changes = {}
            set_form_state(self.editor, False)
            self.refresh_choices(True)
            for name, variable in self.editor.vars.items():
                variable.set(selection_display(rows, name, show_common=True))
            self.editor.widgets["task_template_id"].configure(state="disabled")
            self.editor.description.configure(state="normal")
            text = selection_display(rows, "description", show_common=True)
            self.editor.description.delete("1.0", "end")
            self.editor.description.insert("1.0", text)
            self.description_seen = self.editor.description.get("1.0", "end-1c")
            self.editor.description.edit_modified(False)
            self.active = True
        finally:
            self.loading = False
        self.editor._set_status(f"{len(selected)} templates selected - edit fields, then Apply to List. Untouched fields are preserved.")

    def end(self):
        self.active = False
        self.changes = {}
        self.selection = ()
        self.original = []
        self.refresh_choices(False)

    def changed(self, name):
        if not self.active or self.loading or name == "task_template_id":
            return
        self.changes[name] = self.editor.vars[name].get()
        self.note_changes()

    def note_changes(self):
        self.editor._set_status(f"{len(self.selection)} templates selected; {len(self.changes)} edited field(s) ready for Apply to List.")

    def description_modified(self, _event=None):
        widget = self.editor.description
        if not widget.edit_modified():
            return
        widget.edit_modified(False)
        self.flush_description()

    def flush_description(self):
        current = self.editor.description.get("1.0", "end-1c")
        if self.active and not self.loading and current != self.description_seen:
            self.changes["description"] = current
            self.note_changes()
        self.description_seen = current

    def focus(self, name):
        if not self.active or name in self.changes or name == "task_template_id":
            return
        widget = self.editor.description if name == "description" else self.editor.widgets[name]
        def select_placeholder():
            if not self.active or name in self.changes:
                return
            value = self.editor.description.get("1.0", "end-1c") if name == "description" else self.editor.vars[name].get()
            if value != MULTIPLE_VALUES:
                return
            if name == "description":
                widget.tag_add("sel", "1.0", "end-1c")
                widget.mark_set("insert", "end-1c")
            else:
                widget.selection_range(0, "end")
                widget.icursor("end")
        widget.after_idle(select_placeholder)

    def apply(self):
        self.flush_description()
        if not self.active:
            raise ValueError("Select the task rows before editing.")
        if tuple(self.editor.tree.selection()) != self.selection or self.editor.loaded_rows != self.original:
            raise ValueError("Task draft or selection changed. Reselect rows before applying.")
        if not self.changes:
            self.editor._set_status("No deliberately edited fields. Task draft unchanged.")
            return False
        changes = dict(self.changes)
        allowed = set(self.editor.vars) | {"description"}
        for name, value in changes.items():
            if name not in allowed or name == "task_template_id":
                raise ValueError("Task identity fields cannot be batch-edited.")
            if not isinstance(value, str) or value.strip() == MULTIPLE_VALUES:
                raise ValueError("Placeholder text cannot be applied as task data.")
        candidate = [dict(row) for row in self.original]
        priorities = set(self.editor.choices("priority"))
        capabilities = set(self.editor.choices("capability_id"))
        families = set(self.editor.choices("target_family_id"))
        for row in candidate:
            if row["task_template_id"] not in self.selection:
                continue
            row.update({name: value.strip() for name, value in changes.items()})
            if not re.fullmatch(r"[A-Z][A-Z0-9_]*", row["task_template_id"]):
                raise ValueError("Invalid task identity in draft.")
            problems = schema.errors(row, priorities)
            if row.get("capability_id") and row["capability_id"] not in capabilities:
                problems.append("unknown capability_id")
            if row.get("target_family_id", "") not in families:
                problems.append("unknown LOCATION station family")
            if problems:
                raise ValueError(row["task_template_id"] + ": " + "; ".join(problems))
        keys = [row["task_template_id"] for row in candidate]
        if len(keys) != len(set(keys)):
            raise ValueError("Duplicate task IDs in draft.")
        self.editor._validate_rows(candidate)
        if tuple(self.editor.tree.selection()) != self.selection or self.editor.loaded_rows != self.original:
            raise ValueError("Task draft changed during validation. No batch rows applied.")
        self.editor.loaded_rows = candidate
        self.editor.dirty = True
        for key in self.selection:
            row = next(row for row in candidate if row["task_template_id"] == key)
            self.editor.tree.item(key, values=tuple(row[field] for field in self.editor.tree["columns"]))
        count = len(self.selection)
        self.begin(self.selection, force=True)
        self.editor._set_status(f"Updated {count} task draft rows; {len(changes)} field(s). UNSAVED CHANGES.")
        return True


def install_task_inline(editor):
    controller = getattr(editor, "_task_inline", None)
    if controller is None:
        controller = TaskInlineEditor(editor)
        editor._task_inline = controller
    return controller


def end_task_inline(editor):
    controller = getattr(editor, "_task_inline", None)
    if controller is not None:
        controller.end()


def apply_task_inline(editor):
    controller = getattr(editor, "_task_inline", None)
    try:
        if controller is None:
            raise ValueError("Reselect multiple task rows before editing.")
        return controller.apply()
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        editor.app.log(f"Task Templates batch Apply blocked; draft retained: {error}")
        editor._set_status("Batch Apply blocked: " + str(error).splitlines()[0] + " See Activity Log.")
        return False
