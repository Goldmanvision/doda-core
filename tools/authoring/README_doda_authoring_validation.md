# DoDA CSV Authoring Validation Utility

## Purpose and Scope

`validate_doda_authoring.py` is a standalone, offline developer tool designed to validate authoring CSV datasets for future DoDA strategic systems. It ensures data consistency, schema conformity, foreign-key integrity, and domain constraints across authoring tables before any data is processed or converted.

### Explicit Scope Disclaimer
This tool is not a runtime loader, does not change UZDoom content, does not modify native DoDA state, does not modify saves, and does not replace native validation.

---

## Exact Command to Run

Run the validator from the repository root or tools directory by supplying `--data-dir`:

```bash
python tools/validate_doda_authoring.py --data-dir <directory>
```

For example, to validate the provided fixture datasets:

```bash
python tools/validate_doda_authoring.py --data-dir tools/examples
```

---

## CSV Schemas

The validator expects four UTF-8 CSV files with headers within the target directory:

### 1. `people.csv`
- `person_id` (string, required, unique primary key)
- `display_name` (string, required, nonblank)
- `status` (string, required)
- `workload` (integer, required, range `0` through `100` inclusive)

### 2. `locations.csv`
- `location_id` (string, required, unique primary key)
- `display_name` (string, required, nonblank)

### 3. `tasks.csv`
- `task_id` (string, required, unique primary key)
- `display_name` (string, required, nonblank)
- `location_id` (string, required, foreign key referencing `locations.csv`)
- `state` (string, required, must be one of: `PENDING`, `ACTIVE`, `COMPLETE`)
- `required_work` (integer, required, integer > 0)
- `current_progress` (integer, required, integer from `0` through `required_work` inclusive)
- `assigned_person_count` (integer, required, must equal the count of `PENDING` or `ACTIVE` assignments for this task)

### 4. `assignments.csv`
- `assignment_id` (string, required, unique primary key)
- `person_id` (string, required, foreign key referencing `people.csv`)
- `task_id` (string, required, foreign key referencing `tasks.csv`)
- `assignment_state` (string, required, must be one of: `PENDING`, `ACTIVE`, `COMPLETE`, `CANCELLED`)

---

## Exit Codes

- `0` (Success): All CSV files exist, schemas match, and all validation rules passed. Record counts and `DODA AUTHORING VALIDATION PASSED` are printed to stdout.
- Non-zero (`1`): One or more validation errors occurred. Detailed issue diagnostics (file name, CSV row number, column or rule name, and explanation) are printed to stderr.

---

## Example Validation Failure

If an invalid task state is specified or assigned person count does not match the assignment records, the validator outputs:

```text
Validation failed with 2 issue(s):

  tasks.csv:2 [state] Invalid task state 'IN_PROGRESS'. Must be one of: ACTIVE, COMPLETE, PENDING
  tasks.csv:2 [assigned_person_count] assigned_person_count is 1, but found 2 PENDING or ACTIVE assignment(s) for task 'TASK_MORROW_SURVEY_001' in assignments.csv
```
