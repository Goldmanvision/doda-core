"""Capabilities applied-draft guards; preserve existing guard delegation."""


def capabilities_draft_dirty(app):
    editor = getattr(app, "capabilities_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_capabilities_project_change(app, dialogs):
    if capabilities_draft_dirty(app):
        dialogs.showwarning(
            "Capabilities",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_capabilities_draft_close_guard(app, dialogs):
    if getattr(app, "_capabilities_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if capabilities_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Capabilities Draft",
            "Close and discard applied Capabilities draft changes?",
            parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._capabilities_close_guard_installed = True