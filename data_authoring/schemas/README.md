# DoDA Content Workbench Schemas

This directory will contain machine-readable schemas and controlled-value exports.

The first CLI version will validate the CSV headers, stable IDs, foreign keys,
metric ranges, and tier coverage before it creates a generated PK3 overlay.

Editable source data belongs in:

`data_authoring/source/`

Generated runtime data must never become the manual source of truth.
