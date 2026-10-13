# Copy saved requirements report v113

Adds Copy Requirements Report to the saved task requirements preview.
Copies the selected model from the already-loaded source snapshot.
Does not reread files, validate again, save, export or modify editor drafts.
Snapshot-wide warnings are explicitly labeled as ALL LOADED TEMPLATES.
Copies through the Workbench owner rather than the transient preview window.
Logs copy success only after clipboard operations complete.
Reports clipboard errors and handles an empty selection.
Existing staffing/prerequisite semantics and export schemas are unchanged.
Expected tests: 653 baseline; 663 after installation.
Manual clipboard check required after successful installation.
