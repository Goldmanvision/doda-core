"""Task draft protections layered around the existing shared close handler."""
def task_draft_dirty(app):
    editor = getattr(app, "task_templates_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_task_project_change(app, dialogs):
    if task_draft_dirty(app):
        dialogs.showwarning("Task Templates", "Save to Source or Revert Draft before switching projects. Your Task Templates draft is retained.", parent=app)
        return False
    return True


def install_task_draft_close_guard(app, dialogs):
    if getattr(app, "_task_draft_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)
    def on_close():
        if task_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Task Templates Draft", "Close and discard applied Task Templates draft changes?", parent=app
        ):
            return
        if previous is not None:
            previous()
        else:
            app.destroy()
    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._task_draft_close_guard_installed = True
