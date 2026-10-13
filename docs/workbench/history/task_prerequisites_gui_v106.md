# Task Prerequisites integration v106

Added Tasks > Task Prerequisites using the shared editor.
Main validation and GUI rules validation include the catalog.
Candidate saves stage and validate prerequisites without overwriting candidates.
Task Template saves include prerequisites in their staging files.
Export All / rules export produce generated/data/task_prerequisites.json.

Role and weapon type dropdowns permit blank values for generic requirements.
Cross-field requirements are checked by Validate Draft and Save to Source.
Changing Kind does not automatically rewrite other fields in this slice.
Three Investigation prerequisite rows remain inactive.
Vehicle quantity remains unconfigured, with a draft warning.
No existing source CSVs, device limits, allocations or runtime behavior changed.

Automated acceptance: 592 baseline tests; 598 after integration.
Manual acceptance pending: page, draft validation, Validate All and Export All.
