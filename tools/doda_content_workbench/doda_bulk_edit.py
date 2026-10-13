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
        raise BulkEditError("Draft or selection changed. Reselect the rows before applying.")
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
