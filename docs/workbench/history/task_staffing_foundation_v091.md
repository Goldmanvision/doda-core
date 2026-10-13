# Task staffing foundation v091

CONFIRMED seed:
- Field Surveillance requires at least three analysts.
- Its task and staffing rule remain inactive drafts.

Foundation representation:
- Task-specific role counts are separate from capability staffing.
- Preferred and maximum counts are optional and remain unspecified.
- A blank maximum is not confirmation of unlimited staffing.
- No skill, training, or qualification requirements are inferred.
- Existing templates and source tables are preserved.

Implementation:
- task_staffing_rules.csv and validator/export CLI.
- Main validation checks the table when present.
- Task Template candidate saves include the new table.
- Separate JSON export marks runtimeImplemented false.
- No allocation, execution, balance changes, or PK3 integration.

Pending:
- GUI editor and Export All integration.
- Further task staffing values and eligibility mappings.
