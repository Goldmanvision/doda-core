# 1. Introduction

DoDA Content Workbench User Manual — Batch 1

Draft for review | Prepared October 6, 2026

## Contents

- 1.1 Who this manual is for
- 1.2 What the Workbench does
- 1.3 What the Workbench does not do
- 1.4 The authoring workflow
- 1.5 The twelve content tables
- 1.6 Essential terminology
- 1.7 Safety rules

## 1.1 Who this manual is for

This manual is for a person who needs to inspect or author DoDA content but has not used the Content Workbench before. You do not need to write Python or understand the application implementation to use its editor forms.

You will need access to an existing DoDA project with the Workbench installed. This first batch explains how to launch that installation, inspect a record, make a controlled edit, validate the project, and export generated content. It is not a fresh-installation guide.

The examples use the supplied October 6, 2026 data snapshot. Your records may differ after further editing. Example counts and values are not requirements for every project.

## 1.2 What the Workbench does

The Workbench provides a desktop interface for authored content stored in CSV files. A CSV is a text file arranged as a table: the first row names the fields, and each later row describes one record.

The GUI installs editors for twelve authoring tables. It also provides commands to refresh source data, run validation, export generated content, open project folders, and view process output.

The project root is the main project folder. The Workbench uses that root to locate its scripts, authored CSVs, generated outputs, reports, and build artifacts. Choosing the correct root is essential: saving a record affects the source data under that root.

## 1.3 What the Workbench does not do

The current exporter packages data; it does not activate new game behavior. It does not edit MAPINFO, GAMEINFO, the root LANGUAGE file, zscript.txt, maps, native C++, or ZScript.

A successful export produces a data-only PK3 overlay proof. Its manifest marks the native loader and MAPINFO, LANGUAGE, and ZScript integration flags as disabled.

Do not interpret any of the following as proof that authored content works in-game:

| Result | What it establishes | What it does not establish |
|---|---|---|
| A form contains values | Values are currently displayed in the editor | Those values have been saved |
| A save succeeds | The selected editor's save operation completed | Generated outputs are current |
| Validation succeeds | Saved CSVs satisfy the implemented validation rules | Game behavior or balancing is correct |
| Export succeeds | Generated data and the package were produced | Runtime integration is enabled |

## 1.4 The authoring workflow

Use this mental model:

**Inspect -> Edit form -> Save source -> Validate source -> Export outputs**

1. Inspect existing records and their relationships before changing anything.
2. Edit a record using its editor form.
3. Save using the editor's save button. Typing alone is not saving.
4. Run project validation to inspect the saved data as a whole.
5. Export when you need refreshed generated files and a package.

The Task Templates editor additionally validates a complete candidate project before replacing its CSV. That protects the saved source from invalid task changes. This manual does not assume that every editor has identical save or backup behavior; later chapters will describe each editor separately.

## 1.5 The twelve content tables

| Table | Purpose | Key fields identifying a record |
|---|---|---|
| Enum catalog | Controlled choices used by other records | enum_group + enum_value |
| Department tracks | Departmental categories | track_id |
| Metrics | Measurements, limits, defaults, and display settings | metric_id |
| Metric tiers | Labeled numeric bands for a metric | metric_id + tier_id |
| Facilities | Facilities and their capacity and category | facility_id |
| Flavor text | Titles and descriptive text | flavor_text_id |
| Qualification catalog | Qualifications used in staffing rules | qualification_id |
| Capabilities | Capability definitions and standing-operation labels | capability_id |
| Facility capabilities | Capability installations at facilities | facility_id + capability_id |
| Capability staffing rules | Contributor requirements by qualification | capability_id + qualification_id |
| Facility capability staffing overrides | Installation-specific contributor counts | facility_id + capability_id + qualification_id |
| Task templates | Task defaults associated with capabilities | task_template_id |

A combined key identifies a record using more than one field. For example, the same capability can be installed at different facilities without those installations being the same record.

Some tables depend on records in others. A task references a capability; a facility-capability installation references both a facility and a capability. Removing or deactivating a referenced parent can make the project invalid.

## 1.6 Essential terminology

| Term | Meaning in this manual |
|---|---|
| Active | A Boolean field used by validation and selection rules; not a promise of live game execution |
| Authored source | Editable CSV data under data_authoring/source |
| Backup | A saved copy of an earlier file; not an automatic undo command |
| Candidate | Proposed data tested before it replaces a source file |
| Controlled value | A choice supplied by an approved catalog rather than arbitrary text |
| Export | Rebuilding generated data and the PK3 from saved CSVs |
| Field | One named property of a record |
| ID | A stable identifier used to identify or reference a record |
| Manifest | Export metadata including timestamps, row counts, hashes, and runtime status |
| Project root | The folder containing the project's authoring data, tools, and game content |
| Record | One row of authored content |
| Refresh | Reloading source data into the application; not saving a form |
| Validation | Checking the data against implemented rules |

## 1.7 Safety rules

- Check the displayed project path before saving or exporting.
- Practice on a separate project copy when learning to create or remove records.
- Keep source CSVs as the authority. Do not manually repair generated JSON or a PK3.
- Do not assume unchecking Active removes all reference requirements.
- Do not treat Revert Form as an undo for a completed save.
- Avoid concurrent editing of the same source data in another Workbench window or spreadsheet.
- Record the old value before making your first edit.
- Read validation errors rather than repeatedly retrying the same change.

Next: Chapter 2, Getting Started.
