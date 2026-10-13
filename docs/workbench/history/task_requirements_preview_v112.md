# Saved task requirements preview v112

Preview buttons on Task Templates, Task Staffing and Task Prerequisites.
Reads saved task templates, staffing rules and prerequisites.
Unsaved forms/lists are excluded; unknown saved template IDs are rejected.
Required source files and exact task-template header are checked.
Staffing/prerequisite definitions are validated with existing validators.
Source hashes are checked before/after loading to detect snapshot changes.
Shows active definitions and inactive drafts without enabling execution.
Per-agent quantities remain separate from task-wide quantities.
Blank minimum is unconfigured; blank staffing maximum is not confirmed unlimited.
No inventory, eligibility, assignment, vehicle allocation or runtime execution.
No source CSV, export schema, staffing count or prerequisite changes.
This preview does not replace full project validation.
Expected tests: 636 baseline; 653 after installation.
Manual GUI acceptance required after installation.
