# Batch 1 editorial review notes

Prepared October 6, 2026. These notes are not part of the beginner manual.

## Reading order

1. 01_Introduction.md
2. 02_Getting_Started.md
3. 03_First_Guided_Workflow.md

## Evidence reviewed

- doda_content_workbench/README.md: source-of-truth policy; early command guidance is stale.
- doda_content_workbench/doda_content_workbench.py: twelve-table registry and validation rules. Retrieved validator content was truncated near capacity-warning logic.
- doda_content_workbench/doda_content_export.py: complete export pipeline, paths, normalized types, versions, runtime status, archive entries.
- doda_content_workbench/doda_task_templates_editor.py: complete form and commit implementation.
- doda_content_workbench/doda_content_gui.py: retrieved excerpts verify startup, editor installation, File/Actions/Folders commands, menu names, shortcuts, and validation invocation. Full refresh, export callback, project switching, overview, preview, and notebook layout were not retrieved in full.
- source/task_templates.csv: exact supplied two-row snapshot.
- Conversation: confirmed existing Windows environment and successful script-based GUI launch, validation/export, and sandbox Task Templates commit tests.

## Coverage boundaries

Do not describe this batch as a complete review of the other eleven editors. Their individual source implementations still need inspection for later chapters. Generalized backup/undo/save claims have deliberately been avoided.

Fresh installation instructions, detailed preview operation, screenshots, full GUI refresh behavior, project-switch behavior, and all remaining editor procedures await review. Batch 1 covers an existing installation and a bounded Task Templates workflow.

The GUI module's opening comment claims it cannot edit CSV data, but its executable code installs all twelve editors. Use current behavior, not that stale comment, as the manual authority.

## Questions for review

- Does the launch procedure match the intended deployment for end users?
- Does the Task Templates editor appear under the expected tab label in the current GUI?
- Do the menu-based validation/export procedures and Activity Log instructions match the running application?
- Is a separate complete project copy the preferred training environment?

## PDF production

No PDF has been compiled. Keep the chapter headings, ordinary Markdown tables, and fenced code examples as editable sources. Generate final page numbers and PDF navigation only after chapter approval. Wide CSV examples should be converted to readable field/value layouts in the PDF where needed.
