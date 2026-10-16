"""Flavor Text applied-draft guards; retain the existing close chain."""


def flavor_text_draft_dirty(app):
    editor = getattr(app, "flavor_text_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_flavor_text_project_change(app, dialogs):
    if flavor_text_draft_dirty(app):
        dialogs.showwarning(
            "Flavor Text",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_flavor_text_draft_close_guard(app, dialogs):
    if getattr(app, "_flavor_text_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if flavor_text_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Flavor Text Draft",
            "Close and discard applied Flavor Text draft changes?",
            default="no", parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._flavor_text_close_guard_installed = True
