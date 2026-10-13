# Investigation vehicle prerequisite v108

Confirmed by user 2026-10-10:
- One shared motor vehicle per Investigation task assignment.
- Standard vehicle supports team sizes up to 4.
- Van supports team sizes up to 6.
- Capacity is distinct from minimum vehicle quantity.

The first v108 runner stopped at the hash guard without patch writes.
Fresh capture showed min_quantity already saved as 1.
This corrected patch preserves quantity 1 and changes only the vehicle
description in task_prerequisites.csv, preserving its existing byte formatting.
All other rows, fields and source CSVs remain unchanged.
All three Investigation prerequisite definitions remain inactive drafts.
Investigation staffing maximum remains 2 agents.

Capacities are documented only; no structured vehicle catalog, seat checks,
multiple-vehicle allocation, travel timing, inventory or runtime eligibility.
Teams beyond capacity and multiple-vehicle rules remain unresolved.
Historical records of previously unconfigured quantities remain intact.

Acceptance: 606 baseline and post-change tests.
Main/candidate validation and temporary export checked.
Manual acceptance pending: vehicle quantity/description, Validate All, Export All.
