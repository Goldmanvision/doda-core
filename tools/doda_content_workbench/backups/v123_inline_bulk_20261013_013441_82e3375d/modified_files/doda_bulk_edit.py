"""Explicit, atomic draft-only batch editing for shared table pages."""
import csv

from doda_row_selection import MULTIPLE_VALUES, selection_display


class BulkEditError(ValueError):
    pass


def build_candidate(rows, indices, changes, spec, decimal_check=None):
    indices = tuple(indices)
    if len(indices) < 2 or len(set(indices)) != len(indices):
        raise BulkEditError("Select at least two distinct rows.")
    if any(not isinstance(i, int) or i < 0 or i >= len(rows) for i in indices):
        raise BulkEditError("Selection no longer matches the draft.")
    fields = {f.name: f for f in spec.fields}
    for name, value in changes.items():
        if name not in fields:
            raise BulkEditError("Unknown field: " + name)
        if name in spec.key_columns:
            raise BulkEditError("Identity fields cannot be batch-edited: " + name)
        if not isinstance(value, str):
            raise BulkEditError("Field values must be text: " + name)
        if value.strip() == MULTIPLE_VALUES or (
            fields[name].kind == "evidence_multi"
            and MULTIPLE_VALUES in [v.strip() for v in value.split(";")]
        ):
            raise BulkEditError("Placeholder text cannot be applied: " + name)
    candidate = [dict(row) for row in rows]
    for index in indices:
        candidate[index].update({name: value.strip() for name, value in changes.items()})
        row = candidate[index]
        for f in spec.fields:
            value = row.get(f.name, "")
            if f.required and not value.strip():
                raise BulkEditError(f"Row {index + 1}: {f.label} is required.")
            if value and f.kind == "int":
                try:
                    int(value)
                except ValueError:
                    raise BulkEditError(f"Row {index + 1}: {f.label} must be a whole number.")
            if value and f.kind == "decimal" and decimal_check is not None:
                try:
                    decimal_check(value)
                except ValueError as error:
                    raise BulkEditError(f"Row {index + 1}: {f.label}: {error}") from error
            if f.name in changes and value:
                if f.kind == "bool" and value.lower() not in ("true", "false"):
                    raise BulkEditError(f"{f.label} must be true or false.")
                if f.kind == "choice" and f.choices and value not in f.choices:
                    raise BulkEditError(f"{f.label}: select an available choice.")
    keys = [tuple(row.get(k, "") for k in spec.key_columns) for row in candidate]
    if any(any(not value.strip() for value in key) for key in keys):
        raise BulkEditError("Draft contains a blank identity key.")
    if len(keys) != len(set(keys)):
        raise BulkEditError("Draft contains duplicate identity keys.")
    return candidate


def apply_to_draft(editor, selection, original_rows, changes, validate, decimal_check=None):
    if tuple(editor.tree.selection()) != tuple(selection) or editor.rows != original_rows:
        raise BulkEditError("Draft or selection changed. Reopen the bulk editor.")
    if not changes:
        return False
    candidate = build_candidate(
        original_rows, [int(item) for item in selection], changes,
        editor.spec, decimal_check,
    )
    result = validate(editor.app.project_root, editor.spec.table, candidate)
    if not result.valid:
        raise BulkEditError("Batch validation failed; no rows changed.\n\n" + "\n".join(result.errors[:12]))
    if tuple(editor.tree.selection()) != tuple(selection) or editor.rows != original_rows:
        raise BulkEditError("Draft or selection changed during validation. No rows changed.")
    editor.rows = candidate
    editor.dirty = True
    return True


def open_bulk_editor(editor, validate, reference_keys, evidence_choices, decimal_check):
    import tkinter as tk
    from tkinter import messagebox, ttk
    from doda_multiselect import MultiSelectDropdown
    selection = tuple(editor.tree.selection())
    if len(selection) < 2:
        return
    original = [dict(row) for row in editor.rows]
    try:
        selected_rows = [original[int(item)] for item in selection]
    except (ValueError, IndexError):
        messagebox.showerror(editor.title, "Selection no longer matches the draft.")
        return
    window = tk.Toplevel(editor.tab)
    window.title(editor.title + " - Bulk Edit")
    window.transient(editor.tab.winfo_toplevel())
    window.geometry("960x640")
    window.minsize(760, 400)
    window.columnconfigure(0, weight=1)
    window.rowconfigure(1, weight=1)
    ttk.Label(window, text=(
        f"{len(selection)} selected rows. Keep preserves each row; Set replaces; Clear explicitly blanks.\n"
        "Apply changes the draft only. Save to Source remains separate. Identity fields are protected."
    ), padding=10).grid(row=0, column=0, sticky="ew")
    shell = ttk.Frame(window)
    shell.grid(row=1, column=0, sticky="nsew", padx=10)
    shell.columnconfigure(0, weight=1)
    shell.rowconfigure(0, weight=1)
    canvas = tk.Canvas(shell, highlightthickness=0)
    scroll = ttk.Scrollbar(shell, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scroll.set)
    canvas.grid(row=0, column=0, sticky="nsew")
    scroll.grid(row=0, column=1, sticky="ns")
    fields = ttk.Frame(canvas, padding=4)
    fields.columnconfigure(3, weight=1)
    item = canvas.create_window((0, 0), window=fields, anchor="nw")
    fields.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.bind("<Configure>", lambda e: canvas.itemconfigure(item, width=max(e.width, fields.winfo_reqwidth())))
    modes, values, controls = {}, {}, {}
    for col, title in enumerate(("Field", "Current selection", "Operation", "Replacement value")):
        ttk.Label(fields, text=title).grid(row=0, column=col, sticky="w", padx=5, pady=6)

    def set_mode(name, widget, enabled_state):
        mode = modes[name].get()
        widget.configure(state=enabled_state if mode == "Set" else "disabled")
        if mode == "Clear":
            values[name].set("")

    try:
        for row_number, f in enumerate(editor.spec.fields, 1):
            protected = f.name in editor.spec.key_columns
            ttk.Label(fields, text=f.label + (" [key]" if protected else "")).grid(
                row=row_number, column=0, sticky="w", padx=5, pady=4)
            ttk.Label(fields, text=selection_display(selected_rows, f.name)).grid(
                row=row_number, column=1, sticky="w", padx=5, pady=4)
            mode = tk.StringVar(master=window, value="Keep")
            value = tk.StringVar(master=window, value="")
            modes[f.name], values[f.name] = mode, value
            operation = ttk.Combobox(fields, textvariable=mode, values=("Keep", "Set", "Clear"),
                                     width=8, state="disabled" if protected else "readonly")
            operation.grid(row=row_number, column=2, padx=5, pady=4, sticky="ew")
            enabled_state = "normal"
            if f.kind == "evidence_multi":
                widget = MultiSelectDropdown(fields, value)
                widget.set_options(evidence_choices(editor.app.source_directory))
            elif f.kind in ("bool", "choice", "ref", "track_ref", "task_ref", "collection_type_ref", "evidence_ref"):
                if f.kind == "bool":
                    choices = ("true", "false")
                elif f.kind == "choice":
                    choices = f.choices
                else:
                    choices = reference_keys(editor.app.source_directory, f)
                widget = ttk.Combobox(fields, textvariable=value, values=tuple(dict.fromkeys(("",) + tuple(choices))))
                enabled_state = "readonly"
            else:
                widget = ttk.Entry(fields, textvariable=value)
            widget.configure(state="disabled")
            widget.grid(row=row_number, column=3, padx=5, pady=4, sticky="ew")
            controls[f.name] = widget
            operation.bind("<<ComboboxSelected>>", lambda _e, n=f.name, w=widget, s=enabled_state: set_mode(n, w, s))
        def wheel(event):
            canvas.yview_scroll(-int(event.delta / 120), "units")
            return "break"
        canvas.bind("<MouseWheel>", wheel)
        fields.bind("<MouseWheel>", wheel)
        for child in fields.winfo_children():
            if not isinstance(child, ttk.Combobox):
                child.bind("<MouseWheel>", wheel, add="+")
    except (OSError, UnicodeError, csv.Error, tk.TclError, KeyError, ValueError) as error:
        window.destroy()
        messagebox.showerror(editor.title, "Could not open bulk editor; draft unchanged.\n\n" + str(error))
        return

    def apply():
        changes = {}
        for f in editor.spec.fields:
            mode = modes[f.name].get()
            if mode == "Clear":
                changes[f.name] = ""
            elif mode == "Set":
                changes[f.name] = values[f.name].get()
        try:
            changed = apply_to_draft(editor, selection, original, changes, validate, decimal_check)
        except (ValueError, OSError, UnicodeError, csv.Error) as error:
            messagebox.showerror(editor.title, str(error), parent=window)
            return
        if not changed:
            messagebox.showinfo(editor.title, "No fields selected for Set or Clear. Draft unchanged.", parent=window)
            return
        window.destroy()
        for selected in selection:
            index = int(selected)
            editor.tree.item(selected, values=[
                editor.rows[index].get(f.name, "") for f in editor.spec.fields if not f.multiline
            ])
        editor._on_select()
        editor._set_status(f"Updated {len(selection)} draft rows; {len(changes)} field(s). UNSAVED CHANGES.")

    buttons = ttk.Frame(window, padding=10)
    buttons.grid(row=2, column=0, sticky="ew")
    ttk.Button(buttons, text="Apply to Draft", command=apply).pack(side="left")
    ttk.Button(buttons, text="Cancel", command=window.destroy).pack(side="left", padx=8)
    window.bind("<Escape>", lambda _e: window.destroy())
    window.grab_set()
