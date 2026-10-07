# 3. Your First Guided Workflow

DoDA Content Workbench User Manual — Batch 1

Draft for review | Prepared October 6, 2026

## Contents

- 3.1 Goal and precautions
- 3.2 Validate the starting data
- 3.3 Make a small edit
- 3.4 Revert an unsaved edit
- 3.5 Save and verify
- 3.6 Export saved content
- 3.7 Locate the outputs
- 3.8 Restore the original example value
- 3.9 Troubleshooting
- 3.10 Completion checklist

## 3.1 Goal and precautions

This exercise changes one display name on an existing task template. It teaches selection, form editing, reversion, saving, validation, and export without adding new dependency relationships.

> Recommended practice: use a separate complete project copy for this exercise. A successful save changes the CSV under the displayed project root. Export overwrites generated outputs at that root. Do not experiment in production data unless you intend to make those changes.

Before proceeding, confirm:

- The correct project root is displayed.
- The project contains SIGNAL_REVIEW, or you have selected another existing task.
- No other application is editing the same CSVs.
- You have recorded the original display name.

For the supplied snapshot, the original name is Priority Signal Review. The temporary exercise name is Priority Signal Review - Training.

## 3.2 Validate the starting data

1. Choose Actions > Run Validation.
2. Read the completion notification and process output in Activity Log.
3. If validation fails, stop the exercise and resolve the reported source-data errors first.
4. Review warnings separately from errors. A valid result means no errors; warnings may still be present.

The validation report is written to:

```text
generated/reports/content_validation_report.json
```

Choose Folders > Open Validation Reports Folder to locate it.

Validation checks saved source data. It does not test arbitrary unsaved text currently typed into a form.

## 3.3 Make a small edit

1. Open the Task Templates editor.
2. Select SIGNAL_REVIEW.
3. Find Display Name.
4. Replace Priority Signal Review with Priority Signal Review - Training.
5. Leave the ID, capability, priority, timing fields, sort order, and checkboxes unchanged.

At this point, the change exists only in the form. You have not completed a save.

## 3.4 Revert an unsaved edit

1. Click Revert Form.
2. Confirm Display Name returns to the original value.
3. Enter Priority Signal Review - Training again.

Revert Form reloads the selected record from the editor's loaded rows. It does not retrieve a historical backup and does not undo a completed save.

## 3.5 Save and verify

1. Click Save Template.
2. Wait for validation and the save result.
3. Confirm the success message reports candidate validation passed and provides a backup path.
4. Confirm the edited name appears in the record list.
5. Select another record, then select SIGNAL_REVIEW again.
6. Confirm the edited name is still populated.
7. Choose Actions > Run Validation to check the saved project again.

### What happens during a Task Templates save

| Stage | What the editor does |
|---|---|
| Form checks | Checks required text, ID format, selected choices, and positive numeric fields |
| Duplicate/identity checks | Rejects a new duplicate ID or a changed existing ID |
| Initial change guard | Checks that the source CSV matches the loaded snapshot |
| Candidate creation | Writes sorted task rows to a temporary CSV |
| Project validation | Validates a temporary project containing all twelve tables |
| Second change guard | Checks that the task CSV did not change during validation |
| Backup | Copies the previous task CSV to its backup directory |
| Replacement | Replaces the task CSV with the validated candidate |
| Refresh | Calls the application refresh and displays success |

Task backups are stored under:

```text
data_authoring/backups/task_templates/
```

Click Open Backups to open that directory. Backup names include a timestamp. Opening the directory does not restore a backup.

A form-validation or candidate-validation rejection does not mean the proposed values were saved. Read the message and Activity Log before retrying.

## 3.6 Export saved content

1. Confirm the intended changes have been saved.
2. Choose Actions > Export Generated Content.
3. Wait for the exporter to complete.
4. Read the export process output and completion result.
5. If validation fails, correct the CSV source and retry. The exporter runs validation before generating outputs.

Export reads CSV files, not unsaved forms. Saving does not automatically make the generated JSON or PK3 current.

The exporter is not a general rollback transaction for all generated files. This introductory procedure does not promise that an export failure automatically restores every prior output. Keep backups where preservation of a prior build matters.

## 3.7 Locate the outputs

Use Folders > Open Generated Output Folder and Folders > Open Build Folder.

| Output | Path relative to the project root | Purpose |
|---|---|---|
| Department JSON | generated/data/department_content.json | Normalized records from all twelve tables |
| LANGUAGE fragment | generated/language/DODA_GENERATED_LANGUAGE.txt | Generated title/body language entries from flavor text |
| Manifest | generated/manifest/content_manifest.json | Versions, timestamp, row counts, hashes, and runtime status |
| PK3 overlay | build/doda-generated-content.pk3 | Packaged generated content |

The JSON and manifest use schema version 2 and exporter tool version 0.1.1. The GUI's application version and validator version are different identifiers; do not expect them all to match.

The PK3 contains:

```text
README.txt
data/department_content.json
language/DODA_GENERATED_LANGUAGE.txt
manifest/content_manifest.json
```

Do not manually change these files to fix authored content. Correct the CSV source through the editor and export again.

### CSV and JSON example

The following is a partial CSV extract, not a complete importable task record:

```csv
task_template_id,default_target_effort_minutes,default_deadline_minutes,auto_allocate
SIGNAL_REVIEW,240,120,TRUE
```

The equivalent exported field values use numbers and a JSON Boolean:

```json
{
  "task_template_id": "SIGNAL_REVIEW",
  "default_target_effort_minutes": 240,
  "default_deadline_minutes": 120,
  "auto_allocate": true
}
```

Both timing values must be positive. The validator does not require effort to be less than deadline. Auto Allocate is an authored flag here, not proof that runtime allocation is currently active.

## 3.8 Restore the original example value

If you want the project to finish with its original display name:

1. Select SIGNAL_REVIEW.
2. Change Display Name back to the original value you recorded.
3. Click Save Template and confirm success.
4. Run Actions > Run Validation.
5. Run Actions > Export Generated Content again if you exported the training name earlier.

This restores the selected field value through another validated save. It does not restore the old file byte-for-byte: save ordering, backup history, and export timestamps can differ.

## 3.9 Troubleshooting

| Message or symptom | Meaning | Next action |
|---|---|---|
| Template ID already exists | A new record uses an existing ID | Edit the existing record or choose a genuinely new ID |
| Template ID cannot change after creation | Existing record identity was changed | Retain its original ID |
| Select a valid capability_id or priority | The value is not an allowed active choice | Choose a valid dropdown entry |
| A numeric field must be at least 1 | The field is nonpositive or not a usable integer | Enter a positive whole number |
| Candidate validation failed | The proposed project violates a validator rule | Read Activity Log and fix the identified field or dependency |
| Task CSV changed externally | The loaded snapshot no longer matches the file | Record your unsaved edits, refresh source data, reselect the record, and reapply only the intended changes |
| Task CSV changed during validation | The file changed while the candidate was checked | Stop concurrent editing; refresh and review before retrying |
| Export validation fails | Saved source data is invalid | Fix source data, not generated files |
| Export succeeds but game behavior is unchanged | Runtime integration is not enabled by this exporter | Treat the package as a data-only overlay proof |

Refresh can repopulate editor controls. Copy any unsaved text you want to retain before refreshing; do not assume it will be preserved.

## 3.10 Completion checklist

- I checked the project root.
- I validated the starting saved data.
- I selected and inspected an existing template.
- I demonstrated reverting an unsaved edit.
- I saved a deliberate display-name change.
- I found its backup location.
- I validated saved source data.
- I exported and located the generated outputs.
- I understand that export does not enable runtime integration.
- I restored the original display name if this was only a training exercise.

Later chapters will cover new-record creation, removal, all other editors, dependency planning, and detailed recovery procedures.
