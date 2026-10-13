"""Facility Staffing Overrides guards; preserve the existing close-handler chain."""


def facility_staffing_overrides_draft_dirty(app):
    editor = getattr(app, "facility_capability_staffing_overrides_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_facility_staffing_overrides_project_change(app, dialogs):
    if facility_staffing_overrides_draft_dirty(app):
        dialogs.showwarning(
            "Facility Staffing Overrides",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_facility_staffing_overrides_draft_close_guard(app, dialogs):
    if getattr(app, "_facility_staffing_overrides_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if facility_staffing_overrides_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Facility Staffing Overrides Draft",
            "Close and discard applied Facility Staffing Overrides draft changes?",
            parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._facility_staffing_overrides_close_guard_installed = True