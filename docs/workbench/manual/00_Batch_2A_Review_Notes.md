# Batch 2A editorial review notes

Prepared October 6, 2026. Not part of the beginner manual.

## Deliverable

Chapter 4 covers six core tables. It continues Batch 1 without changing the earlier chapter files. Batch 2B will cover qualifications, capabilities, installations, staffing rules, and overrides.

## Sources reviewed

- doda_content_workbench/doda_track_editor.py: complete source.
- doda_content_workbench/doda_metrics_editor.py: complete source.
- doda_content_workbench/doda_metric_tiers_editor.py: substantial source through save/removal logic; final tail truncated.
- doda_content_workbench/doda_facilities_editor.py: complete source.
- doda_content_workbench/doda_flavor_text_editor.py: complete source.
- doda_content_workbench/doda_enum_catalog_editor.py: complete source.
- source/department_tracks.csv, source/metrics.csv, source/metric_tiers.csv, source/facilities.csv: retrieved snapshot.
- Previously reviewed validator and exporter: cross-table constraints and export normalization.

## Findings requiring attention

1. Metric Tiers layout: several controls and frames share row 9 / column 1; buttons also share row 9. This warrants visual confirmation before instructions promise every control is accessible. Manual flags it rather than silently assuming a repaired layout.
2. Enum Catalog helper refresh_dependents_after_catalog_save calls itself. The shown save path does not directly call this helper; do not claim all saves recurse or fail. Actual dependent refresh remains subject to GUI review/testing.
3. New metric creation and metric retirement can be blocked by opposing cross-table requirements: metrics require tiers, while tiers require metrics. No coordinated multi-table GUI transaction was found in the reviewed editors.
4. Moving shared tier boundaries has the same invalid-intermediate-state problem.
5. Metrics dropdowns use active enums but form validation hard-codes two polarity identifiers and one display mode. New enum values do not automatically extend support.
6. The six reviewed editors do not show Task Templates-style source digest guards. Do not generalize its concurrent-edit protection.
7. Post-save validation warnings are not automatic rollbacks.
8. Flavor LANGUAGE generation includes inactive rows; Active is not an export-exclusion switch.

## Review requests

Confirm the Metric Tiers layout in the running GUI. Determine whether the recursive enum helper is used elsewhere. Agree on a separately verified coordinated multi-table authoring procedure before writing new-metric creation instructions.

No source files were modified and no application was executed by this documentation step.
