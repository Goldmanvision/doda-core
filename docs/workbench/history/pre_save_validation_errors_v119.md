# Shared editor pre-save error handling v119

Handles filesystem, Unicode and CSV exceptions in the pre-save phase.
Scope: initial source hash, candidate validation and post-validation source hash.
Reports validation could not complete and source save was not attempted.
Keeps in-memory rows and dirty state; skips backup/write/success/reload.
Existing validation failures and external-change conflict dialogs are retained.
v116 checkpoints, v117 staging and v118 backup/write handling remain unchanged.
Programming exceptions are not broadly suppressed.
Eight regression tests use temporary files and the actual save method.
Expected tests: 689 baseline; 697 after installation.
No source data, schemas, runtime behavior or controls are changed.
