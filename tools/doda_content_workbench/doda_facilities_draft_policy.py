"""Facilities applied-draft guards; retain the existing close chain."""


def facilities_draft_dirty(app):
    editor = getattr(app, "facilities_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_facilities_project_change(app, dialogs):
    if facilities_draft_dirty(app):
        dialogs.showwarning(
            "Facilities",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_facilities_draft_close_guard(app, dialogs):
    if getattr(app, "_facilities_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if facilities_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Facilities Draft",
            "Close and discard applied Facilities draft changes?",
            default="no", parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._facilities_close_guard_installed = True
