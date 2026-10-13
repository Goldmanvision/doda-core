"""Inline multi-row editing; no bulk window or operation chooser."""
import csv

from doda_bulk_edit import BulkEditError, apply_to_draft
from doda_row_selection import MULTIPLE_VALUES, selection_display, set_form_state

DROPDOWN_KINDS = {"bool", "choice", "ref", "track_ref", "task_ref", "collection_type_ref", "evidence_ref"}
REF_KINDS = {"ref", "track_ref", "task_ref", "collection_type_ref", "evidence_ref"}


class InlineBulkEditor:
    def __init__(self, editor):
        self.editor = editor
        self.active = False
        self.loading = False
        self.selection = ()
        self.original = []
        self.changes = {}
        self.initial_values = {}
        self.traces = []
        self.fields = {f.name: f for f in editor.spec.fields}
        for name, field in self.fields.items():
            widget = editor.widgets[name]
            kind = getattr(field, "kind", "text")
            if kind in DROPDOWN_KINDS:
                self.initial_values[name] = widget.cget("values")
            trace = editor.vars[name].trace_add("write", lambda *_a, n=name: self.changed(n))
            self.traces.append((name, trace))
            if name in editor.spec.key_columns:
                continue
            if kind in DROPDOWN_KINDS:
                widget.bind("<<ComboboxSelected>>", lambda _e, n=name: self.changed(n), add="+")
            elif kind != "evidence_multi":
                widget.bind("<FocusIn>", lambda _e, n=name: self.focus(n), add="+")
                widget.bind("<ButtonRelease-1>", lambda _e, n=name: self.focus(n), add="+")

    def same_session(self, selection):
        return self.active and self.selection == tuple(selection) and self.original == self.editor.rows

    def begin(self, selection, force=False):
        if not force and self.same_session(selection):
            return
        self.active = False
        self.loading = True
        try:
            self.selection = tuple(selection)
            self.original = [dict(row) for row in self.editor.rows]
            selected = [self.original[int(item)] for item in self.selection]
            self.changes = {}
            set_form_state(self.editor, False)
            for name, field in self.fields.items():
                widget = self.editor.widgets[name]
                if getattr(field, "kind", "text") == "evidence_multi":
                    widget._bulk_mode = True
                self.editor.vars[name].set(selection_display(selected, name))
                if name in self.editor.spec.key_columns:
                    widget.configure(state="disabled")
            self.active = True
        finally:
            self.loading = False
        self.editor._set_status(
            f"{len(self.selection)} rows selected - edit Record fields, then Apply to List. "
            "Untouched fields are preserved."
        )

    def end(self):
        self.active = False
        self.changes = {}
        self.selection = ()
        self.original = []
        for name, field in self.fields.items():
            if getattr(field, "kind", "text") == "evidence_multi":
                self.editor.widgets[name]._bulk_mode = False
        for name, values in self.initial_values.items():
            self.editor.widgets[name].configure(values=values)

    def changed(self, name):
        if not self.active or self.loading or name in self.editor.spec.key_columns:
            return
        self.changes[name] = self.editor.vars[name].get()
        suffix = " UNSAVED CHANGES." if self.editor.dirty else ""
        self.editor._set_status(
            f"{len(self.selection)} rows selected; {len(self.changes)} edited field(s) ready for Apply to List." + suffix
        )

    def focus(self, name):
        if not self.active or name in self.changes or name in self.editor.spec.key_columns:
            return
        if self.editor.vars[name].get() != MULTIPLE_VALUES:
            return
        widget = self.editor.widgets[name]
        def select_placeholder():
            if self.active and name not in self.changes and self.editor.vars[name].get() == MULTIPLE_VALUES:
                widget.selection_range(0, "end")
                widget.icursor("end")
        widget.after_idle(select_placeholder)


def install_inline(editor):
    controller = getattr(editor, "_inline_bulk", None)
    if controller is None:
        controller = InlineBulkEditor(editor)
        editor._inline_bulk = controller
    return controller


def refresh_inline_choices(editor, reference_keys, evidence_choices):
    controller = install_inline(editor)
    previous = controller.loading
    controller.loading = True
    try:
        for field in editor.spec.fields:
            kind = field.kind
            widget = editor.widgets[field.name]
            if kind == "evidence_multi":
                widget.set_options(evidence_choices(editor.app.source_directory))
            elif kind in DROPDOWN_KINDS:
                if kind == "bool":
                    choices = ("true", "false")
                elif kind == "choice":
                    choices = field.choices
                elif kind == "collection_type_ref":
                    collection_kind = controller.changes.get("collection_kind")
                    if collection_kind is None:
                        kinds = {controller.original[int(item)].get("collection_kind", "") for item in controller.selection}
                        collection_kind = next(iter(kinds)) if len(kinds) == 1 else None
                    choices = reference_keys(editor.app.source_directory, field, collection_kind)
                else:
                    choices = reference_keys(editor.app.source_directory, field)
                widget.configure(values=tuple(dict.fromkeys(("",) + tuple(choices))))
    finally:
        controller.loading = previous


def apply_inline(editor, validate, decimal_check):
    controller = install_inline(editor)
    if not controller.active:
        editor._set_status("Batch Apply blocked: reselect the rows before editing.")
        return False
    changes = dict(controller.changes)
    try:
        applied = apply_to_draft(
            editor, controller.selection, controller.original, changes, validate, decimal_check,
        )
    except (ValueError, OSError, UnicodeError, csv.Error) as error:
        message = str(error)
        log = getattr(editor.app, "log", None)
        if callable(log):
            log(f"[{editor.spec.table}] Batch Apply blocked; draft retained: {message}")
        editor._set_status("Batch Apply blocked: " + message.splitlines()[0] + " See Activity Log.")
        return False
    if not applied:
        editor._set_status("No deliberately edited fields. Draft unchanged.")
        return False
    selection = controller.selection
    for selected in selection:
        index = int(selected)
        editor.tree.item(selected, values=[
            editor.rows[index].get(field.name, "") for field in editor.spec.fields if not field.multiline
        ])
    controller.begin(selection, force=True)
    editor._ref_choices()
    editor._set_status(
        f"Updated {len(selection)} draft rows; {len(changes)} field(s). UNSAVED CHANGES."
    )
    return True
