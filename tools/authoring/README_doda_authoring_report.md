# DoDA Strategic Data Operations Report Generator

## Purpose and Scope

`build_doda_authoring_report.py` is a standalone, offline developer tool designed to generate human-readable Markdown operations briefs from validated DoDA CSV authoring data. It aggregates personnel availability, active and pending operations, completed missions, and dataset summary statistics into a single structured report.

### Prerequisite
The standalone CSV validator (`validate_doda_authoring.py`) must exist and successfully validate the target data directory before this report is considered authoritative.

### Explicit Scope Disclaimer
This tool is an offline authoring review artifact. It is not a runtime loader, does not load data into UZDoom, native DoDA, LibColony, save files, FOIMS-X, or ZScript, does not modify saves, and does not replace native validation. The script does not calculate strategic progression, assign people, invoke LibColony, alter CSV content, or invent simulation values.

---

## Command Contract

Run the script using Python 3 standard library:

```bash
python tools/build_doda_authoring_report.py \
  --data-dir <directory> \
  --output <report.md>
```

### Example Usage

To generate an operations report from the example fixture datasets:

```bash
python tools/build_doda_authoring_report.py \
  --data-dir tools/examples \
  --output tools/examples/expected_operations_report.md
```

---

## Expected Input Files

The tool reads four UTF-8 CSV files from the specified `--data-dir`:

1. **`people.csv`**: `person_id`, `display_name`, `status`, `workload`
2. **`locations.csv`**: `location_id`, `display_name`
3. **`tasks.csv`**: `task_id`, `display_name`, `location_id`, `state`, `required_work`, `current_progress`, `assigned_person_count`
4. **`assignments.csv`**: `assignment_id`, `person_id`, `task_id`, `assignment_state`

---

## Report Structure

The generated Markdown document contains the following sections:

1. **Header**: Report generation timestamp (ISO 8601 UTC) and directory name.
2. **Summary**: Personnel count, location count, task count, current staffing assignment count, task breakdown by state (`ACTIVE`, `PENDING`, `COMPLETE`), and unassigned personnel count.
3. **Current Operations**: Details for each `ACTIVE` and `PENDING` task, including resolved location names, progress percentages, declared assignment counts, resolved staffing counts, and assigned personnel names/IDs.
4. **Completed Operations**: Details for `COMPLETE` tasks, including location display name, final progress, and historical/current assignment summaries.
5. **Personnel Availability**: Complete roster of personnel with workload, raw status, and current task assignment (or `UNASSIGNED`).
6. **Validation Notes**: Standard authoring review notices and reference to `validate_doda_authoring.py`.

---

## Deterministic Ordering Rules

- **Tasks**: State priority `ACTIVE` first, then `PENDING`, then `COMPLETE`; ties broken alphabetically by `task_id`.
- **Personnel within tasks**: Sorted alphabetically by `person_id`.
- **Personnel Availability**: Sorted alphabetically by `person_id`.
- **Completed Operations**: Sorted alphabetically by `task_id`.

---

## Exit Codes

- `0` (Success): Report generated and written successfully to the `--output` path.
- Non-zero (`1`): A data integrity error occurred (e.g., missing file, missing header, foreign key mismatch, non-integer or negative work/progress value, or write failure). A concise error description is printed to `stderr`.
