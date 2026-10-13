"""Selection-only support; bulk data application is a separate slice."""
MULTIPLE_VALUES = "Multiple values"


def selection_count(editor):
    selected = editor.tree.selection()
    return len(selected) if isinstance(selected, (tuple, list)) else 0


def selection_display(rows, field, show_common=False):
    values = [row.get(field, "") for row in rows]
    if show_common and values and all(value == values[0] for value in values):
        return values[0]
    return MULTIPLE_VALUES if any(values) else ""


def set_form_state(editor, readonly):
    states = getattr(editor, "_selection_widget_states", None)
    if states is None:
        states = {
            name: widget.cget("state")
            for name, widget in editor.widgets.items()
        }
        editor._selection_widget_states = states
    for name, widget in editor.widgets.items():
        widget.configure(state="disabled" if readonly else states[name])


def require_single(editor, action, dialogs):
    if selection_count(editor) > 1:
        dialogs.showwarning(
            editor.title if hasattr(editor, "title") else "Task Templates",
            action + " is a single-record action. Select one row. "
            "Bulk Apply is not enabled in this selection-only slice.",
        )
        return False
    return True
