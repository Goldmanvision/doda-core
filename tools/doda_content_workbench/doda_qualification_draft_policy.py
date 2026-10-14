"""Qualifications applied-draft guards; preserve existing guard delegation."""


def qualification_draft_dirty(app):
    editor = getattr(app, "qualification_catalog_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_qualification_project_change(app, dialogs):
    if qualification_draft_dirty(app):
        dialogs.showwarning(
            "Qualifications",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_qualification_draft_close_guard(app, dialogs):
    if getattr(app, "_qualification_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if qualification_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Qualifications Draft",
            "Close and discard applied Qualifications draft changes?",
            parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._qualification_close_guard_installed = True