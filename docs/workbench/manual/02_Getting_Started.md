# 2. Getting Started

DoDA Content Workbench User Manual — Batch 1

Draft for review | Prepared October 6, 2026

## Contents

- 2.1 Before you begin
- 2.2 Project folders
- 2.3 Launch the existing installation
- 2.4 Confirm the project
- 2.5 Menu orientation
- 2.6 Editor orientation
- 2.7 Read-only first exercise
- 2.8 Startup troubleshooting

## 2.1 Before you begin

This procedure assumes the Workbench is already installed in an existing DoDA project and its Python environment is available. It does not create an environment or install dependencies.

Check for these components:

| Component | Expected location relative to the project root |
|---|---|
| GUI launcher | tools/doda_content_workbench/doda_content_gui.py |
| Validator | tools/doda_content_workbench/doda_content_workbench.py |
| Exporter | tools/doda_content_workbench/doda_content_export.py |
| Editor modules | tools/doda_content_workbench/ |
| Existing Windows environment | tools/doda_content_workbench/.venv/Scripts/python.exe |
| Authored CSVs | data_authoring/source/ |

The .venv path is the existing installation used in the verified project workflow, not a claim that every installation must use that environment name.

> Important: The uploaded folders are named doda_content_workbench and source for review. In the working project, their expected locations are tools/doda_content_workbench and data_authoring/source. Do not rearrange a working installation merely to match uploaded folder names.

## 2.2 Project folders

```text
doda-core/
  DoDA/
  tools/
    doda_content_workbench/
      doda_content_gui.py
      doda_content_workbench.py
      doda_content_export.py
      ...editor modules...
  data_authoring/
    source/
      ...12 CSV files...
    backups/
      task_templates/
  generated/
    data/
    language/
    manifest/
    reports/
  build/
```

| Folder | How to use it |
|---|---|
| tools/doda_content_workbench | Application code; not ordinary authored content |
| data_authoring/source | Saved authored records |
| data_authoring/backups/task_templates | Task Templates CSV backups created by successful commits |
| generated | Rebuildable export outputs and reports |
| build | Generated PK3 package |

Task Templates creates its backup directory when needed. Do not assume an absent backup directory means startup has failed.

## 2.3 Launch the existing installation

1. Open Windows PowerShell.
2. Set the project root to your actual doda-core folder.
3. Run the following commands, replacing the example path if necessary.

```powershell
$root = 'E:\Dev\uzdoom_src\doda-core'
$toolDir = Join-Path $root 'tools\doda_content_workbench'
$pythonPath = Join-Path $toolDir '.venv\Scripts\python.exe'
$guiPath = Join-Path $toolDir 'doda_content_gui.py'

& $pythonPath $guiPath --root $root
```

Expected result: the DoDA Content Workbench window opens. The reviewed GUI declares application version 0.9.0 and loads source data during startup.

The PowerShell window remains occupied while this foreground application process runs. Leave it open; errors may be printed there. Close the Workbench normally when you finish.

The application can discover a project root by searching upward for a folder containing data_authoring, tools, and DoDA. Supplying --root explicitly avoids depending on the current directory.

## 2.4 Confirm the project

1. Read the project path displayed near the application heading.
2. Confirm that it is the project you intend to inspect or edit.
3. If it is incorrect, choose File > Choose Project Root... and select the intended project root.
4. Recheck the displayed path before making any changes.

Choose doda-core, not its source folder, generated folder, or tools folder.

The exact project-switch behavior and handling of unsaved forms require a later review. Finish or discard your work deliberately before switching; do not rely on an unsaved-change prompt.

## 2.5 Menu orientation

The application has File, Actions, Preview, View, Folders, and Help menus. This batch documents the following verified commands:

| Menu | Command | Purpose |
|---|---|---|
| File | Choose Project Root... | Select the working project |
| File | Exit | Close the application |
| Actions | Refresh Source Data | Reload authored source data |
| Actions | Run Validation | Run the project validator |
| Actions | Export Generated Content | Run the exporter |
| Folders | Open Source Data Folder | Open the CSV source directory |
| Folders | Open Generated Output Folder | Open generated outputs |
| Folders | Open Validation Reports Folder | Open the reports directory |
| Folders | Open Build Folder | Open the package directory |

The GUI binds F11 to fullscreen toggling and Ctrl+O to opening the FOIMS-X preview. Ctrl+O is not an Open Project shortcut here. Preview functionality will be covered separately after its implementation is reviewed.

Use the menu commands in this manual even if equivalent buttons are present. This avoids confusing similarly named controls.

## 2.6 Editor orientation

The GUI installs twelve editors. Each is for a particular content table. The Task Templates editor provides a verified introductory example:

| Area or control | Meaning |
|---|---|
| Record list | Existing task templates; columns include ID, name, priority, effort, and deadline |
| Editor form | Fields for the selected record or a new template |
| New Template | Prepare a new-record form |
| Save Template | Validate and commit the proposed record |
| Remove Template | Request confirmed removal of the selected record |
| Revert Form | Reload the selected record or reset a new-record form |
| Open Backups | Open the Task Templates backup directory |

Selecting an existing template populates its form and disables its ID field. Display names are readable labels; IDs are stable references. Renaming a display name does not rename its ID.

Do not assume switching records preserves unsaved form edits. Record selection populates the form from loaded source rows.

## 2.7 Read-only first exercise

Goal: understand a record without changing source data.

1. Open the Task Templates editor.
2. Select SIGNAL_REVIEW in the record list.
3. Compare the form with this supplied-data snapshot.

| Field | Snapshot value |
|---|---|
| Template ID | SIGNAL_REVIEW |
| Display Name | Priority Signal Review |
| Description | Analyze and classify urgent signal interference. |
| Capability | ELECTRONIC_SURVEILLANCE |
| Priority | HIGH |
| Target Effort (minutes) | 240 |
| Deadline (minutes) | 120 |
| Auto Allocate | Checked / TRUE |
| Sort Order | 10 |
| Active | Checked / TRUE |

4. Confirm the ID field is disabled.
5. Select OCCULT_INCIDENT_RESPONSE and observe that the form changes to that record.
6. Do not click Save Template or Remove Template.

Expected result: you can navigate and read the two supplied templates without changing their CSV.

If SIGNAL_REVIEW does not exist in your project, inspect another record. Do not create it solely to make the exercise match.

## 2.8 Startup troubleshooting

| Symptom | First check |
|---|---|
| Python executable cannot be found | Verify the environment path; this procedure does not install Python |
| GUI script cannot be found | Verify the tools/doda_content_workbench location |
| Module import error | Confirm all application modules are present; capture the complete traceback |
| Wrong or missing records | Check the displayed root and data_authoring/source |
| Project discovery fails | Use an explicit --root path |
| Validation status is unknown or old | Run Actions > Run Validation before relying on a status display |

The early README mentions a future python -m doda_workbench command. This manual uses the verified script-based workflow instead.

Next: Chapter 3, Your First Guided Workflow.
