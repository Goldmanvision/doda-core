# Shared editor save checkpoint hardening v116

Adds source-hash rechecks after candidate validation and after backup preparation.
Blocks writing when a changed, deleted or newly-created source is detected.
Keeps existing pre-validation guard, validation, backups and atomic writer.
Blocked saves do not reload the draft editor.
Successful saves retain existing clean-editor refresh behavior.
No CSV schemas, source data, runtime behavior or controls are changed.
These are checkpoint checks, not an interprocess lock or a guarantee against
all possible edits between the last check and the writer's replacement.
Eight regression tests use temporary source files and the actual save method.
Expected tests: 668 baseline; 676 after installation.
No live export is needed for this editor-only change.
