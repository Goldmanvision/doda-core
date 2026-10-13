# Modifier-key row selection v121

Enables extended selection in shared table editors and Task Templates.
Uses Tk's native Ctrl-click toggle and Shift-click range behavior.
Multiple selection displays all-blank fields as blank and populated fields
as display-only Multiple values; forms are read-only in this first slice.
Returning to one selected row restores normal single-record editing.
New/load reset selection form state.
Shared Apply/Delete/Copy/Paste and Task Template Save/Remove are blocked
for multiple rows rather than acting on only the first selected row.
Existing shared Save to Source still writes its draft rows, not placeholders.
Bulk Apply and standalone-editor rollout are separate forthcoming slices.
No source CSV, schema, runtime behavior or export output is changed.
Current manually-authored staffing values are preserved.
Expected tests: 697 baseline; 707 after installation.
Manual Ctrl-click and Shift-click check required after installation.
