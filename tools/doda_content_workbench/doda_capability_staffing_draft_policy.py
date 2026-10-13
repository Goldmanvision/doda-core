"""Capability Staffing applied-draft guards; installed after existing guards."""


def capability_staffing_draft_dirty(app):
    editor = getattr(app, "capability_staffing_rules_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_capability_staffing_project_change(app, dialogs):
    if capability_staffing_draft_dirty(app):
        dialogs.showwarning(
            "Capability Staffing Rules",
            "Save to Source or Revert Draft before switching projects. "
            "Your Capability Staffing draft is retained.",
            parent=app,
        )
        return False
    return True


def install_capability_staffing_draft_close_guard(app, dialogs):
    if getattr(app, "_capability_staffing_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if capability_staffing_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Capability Staffing Draft",
            "Close and discard applied Capability Staffing draft changes?",
            parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._capability_staffing_close_guard_installed = True
