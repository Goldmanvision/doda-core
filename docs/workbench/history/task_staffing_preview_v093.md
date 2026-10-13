# Task staffing in the read-only preview v093

- Saved-source task previews now validate and display task staffing.
- Staffing rows are filtered by task template.
- Inactive drafts remain explicitly labelled.
- Blank minimum means unconfigured; preferred/maximum mean unspecified.
- No authored rows does not imply that no staffing is required.
- No live eligibility, allocation, execution, or balance changes.
- Existing resource-flow preview behavior and export behavior are retained.

Automated acceptance: 493 baseline tests; 499 after change.
Manual acceptance pending: Field Surveillance and Investigate preview displays.
