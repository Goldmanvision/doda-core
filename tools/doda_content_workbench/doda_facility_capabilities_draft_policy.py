"""Facility Capabilities applied-draft guards; retain the existing close chain."""


def facility_capabilities_draft_dirty(app):
    editor = getattr(app, "facility_capabilities_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_facility_capabilities_project_change(app, dialogs):
    if facility_capabilities_draft_dirty(app):
        dialogs.showwarning(
            "Facility Capabilities",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_facility_capabilities_draft_close_guard(app, dialogs):
    if getattr(app, "_facility_capabilities_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if facility_capabilities_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Facility Capabilities Draft",
            "Close and discard applied Facility Capabilities draft changes?",
            default="no", parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._facility_capabilities_close_guard_installed = True
