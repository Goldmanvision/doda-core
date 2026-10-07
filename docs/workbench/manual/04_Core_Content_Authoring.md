# 4. Core Content Authoring

DoDA Content Workbench User Manual — Batch 2A

Draft for review | Prepared October 6, 2026

## Contents

- 4.1 Scope and precautions
- 4.2 Common controls and save behavior
- 4.3 Department tracks
- 4.4 Metrics
- 4.5 Metric tiers
- 4.6 Facilities
- 4.7 Flavor text
- 4.8 Enum catalog administration
- 4.9 Dependency planning
- 4.10 Backup and troubleshooting reference
- 4.11 Practice checklist

## 4.1 Scope and precautions

This chapter covers the six foundational authoring tables: Department Tracks, Metrics, Metric Tiers, Facilities, Flavor Text, and Enum Catalog. Capability and staffing tables are covered in the next chapter.

Work in a separate complete project copy for practice. Verify the displayed project root, validate the starting CSVs, and stop concurrent editing before saving. Examples labeled illustrative are not existing records or instructions to paste data into an import tool. This chapter does not document a CSV import feature.

The source review identified a possible Metric Tiers layout defect and an Enum Catalog helper defect. They are explained where relevant. The manual does not promise that every visible control is usable until those issues have been checked in the running GUI.

## 4.2 Common controls and save behavior

The six reviewed editors use a record list and a form. Selecting a record loads its saved values into the form. Key fields are disabled for existing records.

| Editor | Prepare new form | Save | Request deletion |
|---|---|---|---|
| Department Tracks | Add Track | Save Track | Remove Track |
| Metrics | Add Metric | Save Metric | Remove Metric |
| Metric Tiers | Add Tier | Save Tier | Remove Tier |
| Facilities | Add Facility | Save Facility | Remove Facility |
| Flavor Text | Add Flavor Text | Save Flavor Text | Remove Flavor Text |
| Enum Catalog | Add Enum Value | Save Enum Value | Remove Enum Value |

Add prepares a new-record form; it does not immediately add a saved row. All six provide Revert Form and Open Backups. Revert reloads the selected record or resets a new form. It does not undo a completed save.

### Save sequence

1. The editor checks the form fields.
2. It builds a candidate CSV containing the proposed change.
3. It validates a complete temporary project using all twelve tables.
4. If candidate validation fails, it leaves the real source CSV unchanged.
5. If validation passes, it creates a timestamped backup and replaces the source CSV.
6. It refreshes the application and runs post-save validation.
7. It reports success or a post-save warning.

A post-save validation warning differs from candidate rejection: the CSV has already been replaced. Stop additional edits and inspect Activity Log and the reported backup. Do not assume an automatic rollback.

These six implementations do not contain Task Templates' source-hash checks before and after validation. Avoid external edits and multiple Workbench sessions; do not assume identical concurrent-change protection across all editors.

Existing-record keys cannot be renamed through these forms. Change a display label or name when only the readable wording needs to change.

### ID format

For the IDs checked by these forms, begin with an uppercase letter and use uppercase letters, digits, and underscores thereafter.

| Valid illustrative IDs | Invalid illustrative IDs | Reason |
|---|---|---|
| TRAINING_TRACK | training_track | Lowercase letters |
| TRAINING_2 | 2_TRAINING | Starts with a digit |
| FLV_TRAINING_NOTE | TRAINING-NOTE | Hyphen |

This pattern does not automatically apply to every text field. Owner System, Category, descriptive text, and facility linkage fields have their own checks.

## 4.3 Department tracks

A department track is a category referenced by facilities. It does not create a map location, employee, or capability by itself.

Source CSV: data_authoring/source/department_tracks.csv

Record key: track_id

| Form field | CSV field | Entry rule or purpose |
|---|---|---|
| Track ID | track_id | Required uppercase ID; immutable after creation |
| Display Name | display_name | Required readable name |
| Description | description | Required explanatory text |
| Sort Order | sort_order | Integer of at least 1 |
| Active | active | Checkbox saved as TRUE or FALSE |

Add Track defaults Active to checked and Sort Order to one more than the highest existing order. It leaves ID, name, and description empty.

### Create a training track

1. Open the Department Tracks editor in your practice project.
2. Click Add Track.
3. Enter the illustrative values below.
4. Click Save Track.
5. Read the result and verify the new row in the list.
6. Run Actions > Run Validation if you want to inspect the project result independently.

| Field | Illustrative value |
|---|---|
| Track ID | TRAINING_TRACK |
| Display Name | Training Track |
| Description | Groups facilities used for authoring exercises. |
| Sort Order | Retain the proposed positive value |
| Active | Checked |

Complete illustrative CSV row:

```csv
track_id,display_name,description,sort_order,active
TRAINING_TRACK,Training Track,Groups facilities used for authoring exercises.,7,TRUE
```

The order 7 assumes the supplied six-track snapshot. Use an appropriate value for your project instead of treating 7 as mandatory.

### Remove a track

1. Select an existing track.
2. Click Remove Track.
3. Read the confirmation and choose No to cancel or Yes to proceed with validation.
4. If removal is blocked, inspect Activity Log for dependent facilities or other errors.

A facility referencing the track can prevent removal. Deactivating a referenced track can also invalidate facilities because they must refer to active tracks.

The supplied data includes EVIDENCE_HANDLING, FIELD_OPERATIONS, INTELLIGENCE, PUBLIC_COMMUNICATION, INTERNAL_AFFAIRS, and TECHNICAL_INFRASTRUCTURE. These are snapshot records, not a fixed limit on the catalog.

## 4.4 Metrics

A metric defines a measurement's internal bounds, default value, polarity, and display mode. Metric tiers separately define the labeled bands across its range.

Source CSV: data_authoring/source/metrics.csv

Record key: metric_id

| Form field | CSV field | Entry rule or purpose |
|---|---|---|
| Metric ID | metric_id | Required uppercase ID; immutable after creation |
| Display Name | display_name | Required readable name |
| Description | description | Required text |
| Owner System | owner_system | Required text identifying intended ownership |
| Range / Default: Min | internal_min | Integer; must not exceed Max |
| Range / Default: Max | internal_max | Integer; must not be below Min |
| Range / Default: Default | default_value | Integer within the inclusive range |
| Polarity | polarity | Controlled selection; form currently accepts HIGHER_IS_BETTER or LOWER_IS_BETTER |
| UI Display Mode | ui_display_mode | Controlled selection; form currently accepts TIERED_BAR |
| Update Notes | update_notes | Notes; not required by the reviewed form |
| Active | active | Checkbox |

The polarity and display-mode dropdowns read active enum values, but the form also restricts accepted values to the identifiers above. Adding a new enum value does not automatically extend this form's supported choices.

Add Metric defaults Owner System to NativeStrategicCore, Min to 0, Max to 1000, Default to 0, and Active to checked. It prefers HIGHER_IS_BETTER and TIERED_BAR when available. These are form defaults, not evidence that a runtime owner is implemented for a newly authored metric.

### Safely edit an existing metric

1. Select a metric such as PREPAREDNESS.
2. Record the current values you intend to change.
3. Change only Display Name, Description, or Update Notes for your first exercise.
4. Retain its ID and range.
5. Click Save Metric.
6. Confirm success and inspect the selected record again.

The supplied PREPAREDNESS snapshot has bounds 0–1000 and default 300. Its tier coverage already spans that range.

### Creation and range-change limitation

Every metric must have complete tier coverage. Consequently, Add Metric followed by Save Metric can be rejected because the new metric has no tiers. Adding its tiers first can also be rejected because the metric does not yet exist.

The reviewed forms save one table at a time; they do not expose a coordinated metric-plus-tiers transaction. Do not present sequential creation as a guaranteed working workflow. Creating a new metric and its full tier set requires a coordinated authoring procedure outside these individual save operations, to be documented and verified separately.

Changing an existing metric's bounds can similarly fail while its current tier coverage still matches the old bounds. A valid-looking form can therefore be blocked by cross-table validation.

### Removal limitation

Remove Metric asks for confirmation and validates the candidate project. Existing tier references prevent removal. Removing tiers first is not a general solution because missing tier coverage is itself invalid. Treat metric retirement as a coordinated data change, not a beginner deletion exercise.

## 4.5 Metric tiers

A metric tier maps an inclusive numeric interval to a label, short status, color, and flavor-text reference.

Source CSV: data_authoring/source/metric_tiers.csv

Record key: metric_id + tier_id

Unlike the other five tables in this chapter, Metric Tiers has no Active field.

| Form field | CSV field | Entry rule or purpose |
|---|---|---|
| Metric | metric_id | Existing metric selected from a dropdown |
| Tier ID | tier_id | Uppercase ID; unique within the metric |
| Inclusive Range: Min | min_inclusive | Integer lower bound |
| Inclusive Range: Max | max_inclusive | Integer upper bound; at least Min |
| Display Label | display_label | Required label |
| Short Status | short_status | Required text |
| UI Color | ui_color | Hex color or supported status-color alias |
| Flavor Text | flavor_text_id | Existing flavor-text record |
| Sort Order | sort_order | Integer of at least 1 |

The Metric and Tier ID together are immutable after creation. Dropdowns list existing metrics and flavor text; the reviewed editor does not filter those lists to active records.

### Current layout warning

The uploaded build method places the preset frame, Flavor Text dropdown, Sort Order entry, and button frame at overlapping grid positions around row 9. This is a source-level layout concern, not a confirmed screenshot observation.

If fields or buttons overlap or cannot be reached, stop and report the layout issue. Do not guess values in hidden controls. Field rules below remain useful as a schema reference, but confirm control accessibility before performing the edit procedure.

### Understand inclusive ranges

Both endpoints belong to a tier. In the supplied PREPAREDNESS snapshot:

| Tier | Minimum | Maximum | Sort order |
|---|---:|---:|---:|
| FRAGILE | 0 | 200 | 1 |
| OPERATIONAL | 201 | 500 | 2 |
| HARDENED | 501 | 800 | 3 |
| OVEREXTENDED | 801 | 1000 | 4 |

The value 200 belongs to FRAGILE; 201 belongs to OPERATIONAL. There is no missing value and no shared value.

Partial explanatory CSV extract, not a complete importable tier file:

```csv
metric_id,tier_id,min_inclusive,max_inclusive
PREPAREDNESS,FRAGILE,0,200
PREPAREDNESS,OPERATIONAL,201,500
PREPAREDNESS,HARDENED,501,800
PREPAREDNESS,OVEREXTENDED,801,1000
```

| Invalid change | Why validation rejects it |
|---|---|
| Start OPERATIONAL at 200 | Overlaps FRAGILE at 200 |
| Start OPERATIONAL at 202 | Leaves 201 uncovered |
| End the final tier at 999 | Does not cover the metric maximum 1000 |
| Remove FRAGILE | Leaves the beginning of the metric uncovered |

Sort Order does not fix incorrect numeric boundaries. Validation orders intervals by their numeric limits when checking coverage.

### Colors

Use a #RRGGBB value, Choose Color..., or a preset when controls are accessible. The form normalizes supported aliases to uppercase hexadecimal values.

| Preset | Saved hex value |
|---|---|
| Grey | #8C939F |
| Green | #5CCB72 |
| Amber | #F4B942 |
| Red | #EF5B5B |
| Blue | #58A6FF |
| Purple | #B78CFF |

Custom colors are allowed. The supplied CORRUPTION_PRESSURE / LATENT record uses #FF80FF, which is not the Purple preset.

### Edit wording without changing coverage

1. Confirm the editor controls are accessible.
2. Select an existing tier.
3. Change Display Label or Short Status.
4. Leave Metric, Tier ID, Min, Max, and its flavor reference unchanged.
5. Click Save Tier.
6. Confirm candidate and post-save validation results.

Do not use a single-row edit to move a shared boundary between two adjacent tiers: the intermediate save can create a gap or overlap. A coordinated range-change procedure is needed for such changes. Add Tier and Remove Tier remain subject to the same complete-coverage rule.

## 4.6 Facilities

A facility defines a departmental location record, capacity, initial tier, and intended linkage identifiers. Installing a capability at that facility is a separate record covered later.

Source CSV: data_authoring/source/facilities.csv

Record key: facility_id

| Form field | CSV field | Entry rule or purpose |
|---|---|---|
| Facility ID | facility_id | Uppercase ID; immutable after creation |
| Display Name | display_name | Required name |
| Department Track | track_id | Active department track |
| HQ Zone ID | hq_zone_id | Required linkage text |
| Description | description | Required text |
| Personnel Capacity | personnel_capacity | Integer of at least 1 |
| Initial Tier | initial_tier_id | Active FACILITY_TIER enum value |
| Interaction Asset ID | interaction_asset_id | Required linkage text |
| FOIMS Panel ID | foims_panel_id | Required linkage text |
| Active | active | Checkbox |

The editor checks that the linkage text fields are nonempty; a successful form save does not establish that a map asset, zone, or panel exists in the game. Coordinate real linkage IDs with the project owner.

Add Facility defaults capacity to 1, Active to checked, Department Track to the first available active track, and Initial Tier to UNBUILT when available. Review those selections rather than accepting them blindly.

### Inspect an existing facility

1. Select TECHOPS_HUB if present.
2. Compare it with the supplied snapshot below.
3. Inspect its associated facility-capability installations before changing capacity.

| Field | Snapshot value |
|---|---|
| Display Name | Technical Operations Hub |
| Department Track | TECHNICAL_INFRASTRUCTURE |
| HQ Zone ID | HQ_TECHOPS |
| Personnel Capacity | 3 |
| Initial Tier | OPERATIONAL |
| Interaction Asset ID | HQ_ASSET_TECHOPS_CONSOLE |
| FOIMS Panel ID | FOIMS_FACILITY_TECHOPS |
| Active | TRUE |

### Create an illustrative facility

Use a practice project only. The identifiers below are placeholders for the authoring exercise, not existing game assets.

1. Ensure TRAINING_TRACK exists and is active, or select another appropriate active track.
2. Click Add Facility.
3. Enter the values below and choose an available Initial Tier.
4. Click Save Facility.
5. Inspect the validation result and new record.

| Field | Illustrative value |
|---|---|
| Facility ID | TRAINING_ROOM |
| Display Name | Training Room |
| Department Track | TRAINING_TRACK |
| HQ Zone ID | HQ_TRAINING_EXAMPLE |
| Description | Facility record used for authoring practice. |
| Personnel Capacity | 2 |
| Initial Tier | UNBUILT, if available |
| Interaction Asset ID | HQ_ASSET_TRAINING_EXAMPLE |
| FOIMS Panel ID | FOIMS_TRAINING_EXAMPLE |
| Active | Checked |

A saved facility does not automatically install a capability or create a game location.

### Capacity and removal safeguards

Each installation's max_concurrent_personnel must not exceed the facility capacity. Lowering capacity below an existing installation limit is blocked by full candidate validation.

Remove Facility requires confirmation and candidate validation. Existing installations or overrides can prevent deletion. First review dependencies; do not remove records blindly to make an error disappear.

A facility's Initial Tier and an installation's Initial Tier are separate fields. Do not assume that editing one synchronizes the other.

## 4.7 Flavor text

Flavor Text stores titled narrative text referenced by metric tiers. The exporter also generates LANGUAGE title/body entries from these records.

Source CSV: data_authoring/source/flavor_text.csv

Record key: flavor_text_id

| Form field | CSV field | Entry rule or purpose |
|---|---|---|
| Flavor Text ID | flavor_text_id | Uppercase ID; immutable after creation |
| Category | category | Required text; choose an existing category or type a new one |
| Title | title | Required text |
| Body | body | Required multiline text |
| Active | active | Checkbox |

Category is an editable suggestion list based on current rows, not a read-only enum selection. Add Flavor Text defaults to the first existing category, when one exists, and Active to checked.

### Create and remove a standalone training note

1. Click Add Flavor Text.
2. Enter the illustrative record below.
3. Click Save Flavor Text and verify the saved title and body.
4. To clean up, select the record and click Remove Flavor Text.
5. Confirm removal only if no tier references it.

```csv
flavor_text_id,category,title,body,active
FLV_TRAINING_NOTE,TRAINING,Training note,This text exists only for an authoring exercise.,TRUE
```

The editor handles CSV quoting when saving. You do not need to add CSV quotation marks around text in the form. Commas or line breaks in Body should be entered as ordinary text; generated LANGUAGE output escapes special characters.

The record list shortens long titles for display. Select the row to read the full title in the form rather than assuming the stored text was truncated.

Referenced flavor text cannot be deleted while metric tiers still use its ID. Reassign a tier to another valid flavor record and save that change before attempting removal.

The current exporter iterates all flavor rows when building its LANGUAGE fragment; it does not filter them by Active. Do not use deactivation as a guarantee that text disappears from exported artifacts.

## 4.8 Enum catalog administration

Enum Catalog defines group/value pairs used for controlled choices. It is an administrative editor, not a mechanism for implementing a new game feature.

Tab label verified in its source: Enum Catalog — Admin.

Source CSV: data_authoring/source/enum_catalog.csv

Record key: enum_group + enum_value

| Form field | CSV field | Entry rule or purpose |
|---|---|---|
| Enum Group | enum_group | Uppercase identifier; existing suggestion or new text |
| Enum Value | enum_value | Uppercase identifier; existing suggestion or new text |
| Display Label | display_label | Required readable label |
| Description | description | Required explanatory text |
| Sort Order | sort_order | Integer of at least 0; unlike most other ordered tables, zero is allowed |
| Active | active | Checkbox |

The filter above the record list also reads Enum Group. That filter changes which records are displayed; it does not edit their group or deactivate hidden records. Choose All Groups to see the whole list.

Group and Value are disabled for an existing record. Add Enum Value prepares a new form; both identifiers are editable for new records.

### Inspect task priorities safely

1. Open Enum Catalog — Admin.
2. Set the list filter to TASK_PRIORITY.
3. Select a priority row.
4. Read its identifiers, label, description, sort order, and Active setting.
5. Do not change the Group or Value of an existing row.
6. Set the filter back to All Groups when finished.

Adding a group that no application component consumes will not create a new dropdown elsewhere. Adding a value may be insufficient where an editor separately restricts supported choices, as Metrics currently does.

### Administrative edit procedure

1. Validate the current project.
2. Filter to the intended group and select the exact row.
3. Record its original label and description.
4. Change only Display Label or Description for a first exercise.
5. Click Save Enum Value.
6. Read the save and post-save validation result.
7. Inspect the relevant dependent editor choices before using the changed catalog in further work.

Deletion and deactivation are subject to full candidate validation. A value still used by facilities, metrics, or tasks may be required to remain active.

### Dependent-choice refresh caveat

The uploaded module defines refresh_dependents_after_catalog_save() with a call to itself instead of a dependent-refresh operation. If invoked, this is self-recursive and does not implement the intended refresh. The reviewed save method calls the application's refresh_all(), not that helper directly, so this finding alone does not prove catalog saves fail.

If choices appear stale, preserve unsaved form text, use Actions > Refresh Source Data, then inspect again. Capture any logged errors. Do not repeatedly save or assume a new catalog value is immediately supported everywhere.

## 4.9 Dependency planning

| Proposed change | Check first | Why |
|---|---|---|
| Remove or deactivate a track | Facilities using track_id | Facilities require active tracks |
| Change metric bounds | Every tier for that metric | Tier coverage must match both endpoints |
| Add or remove a metric | Metric and complete tier set together | One-table saves can be blocked by circular validation requirements |
| Move a tier boundary | Neighboring intervals | The intermediate state may contain a gap or overlap |
| Remove flavor text | Metric tiers using flavor_text_id | Referenced text must exist |
| Lower facility capacity | Installed capability concurrency | Each installation limit must fit |
| Remove a facility | Installations and staffing overrides | Child references can block deletion |
| Remove or deactivate an enum | Fields consuming that group/value | Referenced controlled values can be required active |

Not every valid final design can be reached through a sequence of individually valid one-record saves. Stop and plan coordinated changes rather than trying to force an invalid intermediate state through the editor.

## 4.10 Backup and troubleshooting reference

All paths below are relative to the project root:

| Editor | Backup directory |
|---|---|
| Department Tracks | data_authoring/backups/department_tracks |
| Metrics | data_authoring/backups/metrics |
| Metric Tiers | data_authoring/backups/metric_tiers |
| Facilities | data_authoring/backups/facilities |
| Flavor Text | data_authoring/backups/flavor_text |
| Enum Catalog | data_authoring/backups/enum_catalog |

Successful removals generally use filenames containing before_remove. Backups copy an entire table CSV, not just the selected row. Restoring one can affect unrelated records saved afterward.

| Symptom | Response |
|---|---|
| Add was clicked but no row exists | Fill the new form and click its Save button |
| Duplicate key error | Select the existing record or choose a genuinely new key |
| Candidate validation fails | Read Activity Log; another table may be responsible |
| Post-save validation fails | Stop editing; the source may already be changed; retain the backup path |
| Numeric range edit fails | Review metric bounds and complete tier coverage |
| Remove fails | Inspect dependencies and required coverage |
| Tier controls overlap | Report the layout concern; do not rely on inaccessible controls |
| Enum changes do not appear | Preserve unsaved text, refresh, and inspect supported choices |
| A linkage ID saves but has no game effect | A nonempty identifier is not proof of runtime integration |

Open Backups only opens the directory. Backup restoration will be documented as a separate, deliberate recovery operation after that procedure is reviewed.

## 4.11 Practice checklist

In a separate practice project:

1. Create TRAINING_TRACK and validate.
2. Create TRAINING_ROOM referring to that track and validate.
3. Create the standalone FLV_TRAINING_NOTE and validate.
4. Inspect PREPAREDNESS and its four tiers without changing their ranges.
5. Inspect TASK_PRIORITY through the Enum Catalog filter without editing.
6. Remove the unreferenced training note if no longer needed.
7. Remove TRAINING_ROOM before removing TRAINING_TRACK.
8. Validate after cleanup.
9. Export only if you need generated outputs updated to the practice project's final saved state.

If removal is blocked, read the exact validation errors instead of deleting additional records indiscriminately.

Next: Chapter 5, Capabilities and Staffing.
