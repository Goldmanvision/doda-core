"""Enum Catalog applied-draft guards; retain the existing close chain."""


def enum_catalog_draft_dirty(app):
    editor = getattr(app, "enum_catalog_editor", None)
    return bool(editor is not None and getattr(editor, "dirty", False))


def allow_enum_catalog_project_change(app, dialogs):
    if enum_catalog_draft_dirty(app):
        dialogs.showwarning(
            "Enum Catalog",
            "Save to Source or Revert Draft before switching projects. Draft retained.",
            parent=app,
        )
        return False
    return True


def install_enum_catalog_draft_close_guard(app, dialogs):
    if getattr(app, "_enum_catalog_close_guard_installed", False):
        return
    previous = getattr(app, "_network_close_handler", None)

    def on_close():
        if enum_catalog_draft_dirty(app) and not dialogs.askyesno(
            "Unsaved Enum Catalog Draft",
            "Close and discard applied Enum Catalog draft changes?",
            default="no", parent=app,
        ):
            return
        if previous is not None:
            return previous()
        return app.destroy()

    app._network_close_handler = on_close
    app.protocol("WM_DELETE_WINDOW", on_close)
    app._enum_catalog_close_guard_installed = True
