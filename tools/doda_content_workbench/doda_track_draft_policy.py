"""Department Tracks applied-draft guards; retain the existing close chain."""


def track_draft_dirty(app):
    editor = getattr(app, "track_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_track_project_change(app, dialogs):
    if track_draft_dirty(app):
        dialogs.showwarning(
            "Department Tracks",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_track_draft_close_guard(app, dialogs):
    if getattr(app, "_track_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if track_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Department Tracks Draft",
            "Close and discard applied Department Tracks draft changes?",
            default="no", parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._track_close_guard_installed = True
