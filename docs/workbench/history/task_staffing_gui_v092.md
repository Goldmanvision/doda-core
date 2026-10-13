# Task Staffing GUI and export integration v092

- Added Tasks > Task Staffing using the shared metadata-driven editor.
- Composite key: task_template_id+personnel_role.
- Minimum, preferred, and maximum fields remain optional in draft forms.
- Candidate validation checks task staffing alongside the other saved tables.
- Validate All and rules validation include task staffing.
- Export All and rules export produce generated/data/task_staffing_rules.json.
- Existing staffing seed and all source CSVs are preserved.
- No runtime staffing allocation, task execution, or PK3 staffing payload added.

Automated acceptance: 488 baseline tests; 493 after integration.
Manual acceptance pending: page, draft validation, Validate All, Export All.
