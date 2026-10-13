# Task resource-flow preview GUI integration

Scope: authoring UI only.

- Added the saved-source preview to the Workbench Preview menu.
- Added Preview Saved Template to the task resource-flow editor.
- Preview is a Workbench-owned Toplevel, with no nested mainloop.
- Reopening reads a new validated source snapshot.
- Unsaved editor drafts are explicitly excluded.
- Missing saved template IDs and invalid source block opening.
- No source CSV, balance, execution, or export behavior changes.

Acceptance: 471 baseline tests and 476 post-change tests.
Manual acceptance remains pending until menu and button are exercised.
