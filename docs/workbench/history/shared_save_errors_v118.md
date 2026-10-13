# Shared editor backup/write error handling v118

Handles filesystem, Unicode and CSV exceptions around backup/write operations.
Logs the error and shows a save-failure dialog.
Retains in-memory rows and dirty state; skips success logging and editor reload.
A later retry can save once the underlying problem is resolved.
v116 conflict checkpoints and v117 unique staging remain unchanged.
Scope is backup/write handling, not all loading or candidate-validation errors.
No broad catch of programming exceptions or post-save refresh failures is added.
Six regression tests exercise the actual save method with temporary files.
Expected tests: 683 baseline; 689 after installation.
No source data, schemas, runtime behavior or controls are changed.
